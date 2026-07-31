from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from backend.shared.db.session import get_db
from backend.shared.db.models import GeneratedFile, Message, Conversation
from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.document_node import generate_pdf_document, generate_ppt_document

router = APIRouter(prefix="/agents/documents", tags=["Document Agent"])

class DocRequest(BaseModel):
    prompt: str

@router.post("/pdf")
async def create_pdf(req: DocRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    doc_info = await generate_pdf_document(req.prompt)
    
    # We could store a dummy conversation/message for the file, but let's just save the file record directly
    # since GeneratedFile requires a message_id. We'll create a single turn conversation.
    conv = Conversation(user_id=current_user["user_id"], title=doc_info["title"], agent_type="documents")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    msg = Message(conversation_id=conv.id, role="assistant", content="Generated Document", agent_type="documents")
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    gen_file = GeneratedFile(
        message_id=msg.id,
        file_name=doc_info["filename"],
        file_path=doc_info["filepath"],
        file_type="application/pdf"
    )
    db.add(gen_file)
    db.commit()
    db.refresh(gen_file)
    
    return {
        "id": str(gen_file.id),
        "title": doc_info["title"],
        "filename": doc_info["filename"],
        "format": "pdf"
    }

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
        message_id=msg.id,
        file_name=doc_info["filename"],
        file_path=doc_info["filepath"],
        file_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    db.add(gen_file)
    db.commit()
    db.refresh(gen_file)
    
    return {
        "id": str(gen_file.id),
        "title": doc_info["title"],
        "filename": doc_info["filename"],
        "format": "pptx"
    }

@router.get("/download/{file_id}")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    # Auth skipped for simplicity of download links, in prod we should verify token
    gen_file = db.query(GeneratedFile).filter(GeneratedFile.id == file_id).first()
    if not gen_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    if not os.path.exists(gen_file.file_path):
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    return FileResponse(path=gen_file.file_path, filename=gen_file.file_name, media_type=gen_file.file_type)

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find all files belonging to this user
    # A bit complex because User -> Conversation -> Message -> GeneratedFile
    # Simplified query
    res = db.query(GeneratedFile, Conversation).join(Message).join(Conversation).filter(Conversation.user_id == current_user["user_id"]).all()
    
    output = []
    for f, c in res:
        output.append({
            "id": str(f.id),
            "title": c.title,
            "filename": f.file_name,
            "format": "pdf" if f.file_name.endswith(".pdf") else "pptx",
            "created_at": f.created_at.isoformat()
        })
        
    return output
