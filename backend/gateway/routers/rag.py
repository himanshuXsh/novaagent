import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.rag_node import query_document
from backend.services.agent_service.rag_pipeline import process_document
from backend.shared.db.models import Conversation, Document, Message
from backend.shared.db.session import get_db

router = APIRouter(prefix="/agents/rag", tags=["RAG Agent"])

UPLOAD_DIR = "backend/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RagQueryRequest(BaseModel):
    document_id: str
    query: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    doc_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Store in DB
    db_doc = Document(
        id=doc_id,
        user_id=current_user["user_id"],
        file_name=file.filename,
        file_path=filepath,
        status="processing"
    )
    db.add(db_doc)
    db.commit()
    
    # Process
    try:
        chunks = await process_document(filepath, doc_id)
        db_doc.status = "processed"
        db_doc.page_count = chunks # Overloaded just for metric
        db.commit()
    except Exception as e:
        db_doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"document_id": doc_id, "filename": file.filename, "status": "processed"}

@router.post("/query")
async def query_pdf(req: RagQueryRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify doc belongs to user
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user["user_id"]).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    # See if conversation exists for this doc (we'll just use doc_id as conv_id or create one)
    conv = db.query(Conversation).filter(Conversation.title == req.document_id).first()
    if not conv:
        conv = Conversation(user_id=current_user["user_id"], title=req.document_id, agent_type="rag")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
    # Save user msg
    user_msg = Message(conversation_id=conv.id, role="user", content=req.query, agent_type="rag")
    db.add(user_msg)
    db.commit()
    
    # Query RAG
    answer = await query_document(req.query, req.document_id)
    
    # Save assistant msg
    asst_msg = Message(conversation_id=conv.id, role="assistant", content=answer, agent_type="rag")
    db.add(asst_msg)
    db.commit()
    
    return {"answer": answer}

@router.get("/documents")
async def list_documents(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == current_user["user_id"]).order_by(Document.created_at.desc()).all()
    return [{"document_id": str(d.id), "filename": d.file_name, "status": d.status} for d in docs]
