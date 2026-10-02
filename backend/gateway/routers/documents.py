import os

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sse_starlette.sse import EventSourceResponse
from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.document_node import (
    generate_pdf_document,
    generate_ppt_document,
)
from backend.shared.db.models import Conversation, GeneratedFile, Message
from backend.shared.db.session import get_db

router = APIRouter(prefix="/agents/documents", tags=["Document Agent"])

class DocRequest(BaseModel):
    prompt: str

def save_document_background(user_id: str, title: str, filepath: str, format: str):
    from backend.shared.db.session import SessionLocal
    db = SessionLocal()
    try:
        conv = Conversation(user_id=user_id, title=title, agent_type="documents")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
        msg = Message(conversation_id=conv.id, role="assistant", content="Generated Document", agent_type="documents")
        db.add(msg)
        db.commit()
        db.refresh(msg)
        
        gen_file = GeneratedFile(
            user_id=user_id,
            message_id=msg.id,
            type=format,
            file_url=filepath,
            file_size_bytes=1000,
            credits_used=10
        )
        db.add(gen_file)
        db.commit()
    finally:
        db.close()

@router.post("/pdf")
async def create_pdf(req: DocRequest, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    import json
    
    async def event_generator():
        async for chunk_str in generate_pdf_document(req.prompt):
            if await request.is_disconnected():
                break
                
            chunk = json.loads(chunk_str)
            if chunk.get("event") == "done":
                # Defer DB writes to background so the user gets the file link instantly
                background_tasks.add_task(
                    save_document_background, 
                    user_id, chunk["title"], chunk["filepath"], chunk["format"]
                )
                
                yield {
                    "event": "done",
                    "data": json.dumps({
                        "title": chunk["title"],
                        "filename": chunk["filename"],
                        "format": chunk["format"],
                        "filepath": chunk["filepath"]
                    })
                }
                break
            else:
                yield {
                    "event": "message",
                    "data": json.dumps({"content": chunk.get("content", "")})
                }
                
    return EventSourceResponse(event_generator())

@router.post("/ppt")
async def create_ppt(req: DocRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    doc_info = await generate_ppt_document(req.prompt)
    
    conv = Conversation(user_id=current_user["user_id"], title=doc_info["title"], agent_type="documents")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    msg = Message(conversation_id=conv.id, role="assistant", content="Generated Document", agent_type="documents")
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    gen_file = GeneratedFile(
        user_id=current_user["user_id"],
        message_id=msg.id,
        type="pptx",
        file_url=doc_info["filepath"],
        file_size_bytes=1000,
        credits_used=10
    )
    db.add(gen_file)
    db.commit()
    db.refresh(gen_file)
    
    return {
        "id": str(gen_file.id),
        "title": doc_info["title"],
        "filename": os.path.basename(doc_info["filepath"]),
        "format": "pptx"
    }

from fastapi.responses import FileResponse, RedirectResponse

OUTPUT_DIR = "backend/data/outputs"

@router.get("/raw/{filename}")
async def get_raw_file(filename: str):
    safe_name = os.path.basename(filename)
    path = os.path.join(OUTPUT_DIR, safe_name)
    if os.path.exists(path):
        return FileResponse(path, filename=safe_name)
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/download/{file_id}")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    gen_file = db.query(GeneratedFile).filter(GeneratedFile.id == file_id).first()
    if not gen_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    if gen_file.file_url.startswith("http://") or gen_file.file_url.startswith("https://"):
        return RedirectResponse(url=gen_file.file_url)
    
    filename = os.path.basename(gen_file.file_url)
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, filename=filename)
    return RedirectResponse(url=gen_file.file_url)

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    res = (
        db.query(GeneratedFile, Conversation)
        .select_from(GeneratedFile)
        .join(Message, GeneratedFile.message_id == Message.id)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(Conversation.user_id == current_user["user_id"])
        .order_by(GeneratedFile.created_at.desc())
        .all()
    )
    
    output = []
    for f, c in res:
        output.append({
            "id": str(f.id),
            "title": c.title,
            "filename": os.path.basename(f.file_url) if f.file_url else "document",
            "format": f.type,
            "created_at": f.created_at.isoformat()
        })
        
    return output

class RenameRequest(BaseModel):
    new_name: str

@router.patch("/{file_id}/rename")
async def rename_file(file_id: str, req: RenameRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    gen_file = db.query(GeneratedFile).filter(
        GeneratedFile.id == file_id,
        GeneratedFile.user_id == current_user["user_id"]
    ).first()
    
    if not gen_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    # We update the conversation title since that's what we mapped to filename in history
    if gen_file.message_id:
        msg = db.query(Message).filter(Message.id == gen_file.message_id).first()
        if msg:
            conv = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
            if conv:
                conv.title = req.new_name
                db.commit()
                return {"status": "success", "new_name": req.new_name}
                
    raise HTTPException(status_code=400, detail="Cannot rename this file")

@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    gen_file = db.query(GeneratedFile).filter(
        GeneratedFile.id == file_id,
        GeneratedFile.user_id == current_user["user_id"]
    ).first()
    
    if not gen_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    db.delete(gen_file)
    db.commit()
    return {"status": "success"}

@router.post("/{file_id}/duplicate")
async def duplicate_file(file_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    gen_file = db.query(GeneratedFile).filter(
        GeneratedFile.id == file_id,
        GeneratedFile.user_id == current_user["user_id"]
    ).first()
    
    if not gen_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Clone the GeneratedFile record
    # Find original title to duplicate
    title = "Copy of Document"
    if gen_file.message_id:
        msg = db.query(Message).filter(Message.id == gen_file.message_id).first()
        if msg:
            conv = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
            if conv:
                title = f"Copy of {conv.title}"
                
    # Create new conversation for the duplicate
    new_conv = Conversation(user_id=current_user["user_id"], title=title, agent_type="documents")
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    
    new_msg = Message(conversation_id=new_conv.id, role="assistant", content="Duplicated Document", agent_type="documents")
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    new_file = GeneratedFile(
        user_id=current_user["user_id"],
        message_id=new_msg.id,
        type=gen_file.type,
        file_url=gen_file.file_url,
        file_size_bytes=gen_file.file_size_bytes,
        credits_used=0  # Don't charge for duplicating a record
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return {
        "id": str(new_file.id),
        "title": title,
        "filename": os.path.basename(new_file.file_url) if new_file.file_url else "document",
        "format": new_file.type
    }

