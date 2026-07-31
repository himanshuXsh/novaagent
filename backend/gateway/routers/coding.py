from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.shared.db.session import get_db
from backend.shared.db.models import Artifact
from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.conversation_service import (
    create_conversation, get_messages, add_message
)
from backend.services.agent_service.coding_node import generate_code_response

router = APIRouter(prefix="/agents/code", tags=["Coding Agent"])

class CodeRequest(BaseModel):
    conversation_id: Optional[str] = None
    prompt: str

@router.post("")
async def generate_code(req: CodeRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    
    conv_id = req.conversation_id
    if not conv_id:
        title = req.prompt[:30] + "..." if len(req.prompt) > 30 else req.prompt
        conv = create_conversation(db, user_id, title, "coding")
        conv_id = str(conv.id)
        
    history = get_messages(db, conv_id)
    
    # Save user message
    user_msg = add_message(db, conv_id, "user", req.prompt, "coding")
    
    # Generate response
    response_data = await generate_code_response(history, req.prompt)
    
    # Save assistant message
    asst_msg = add_message(db, conv_id, "assistant", response_data["text_content"], "coding")
    
    artifact_id = None
    language = None
    code_content = None
    
    if response_data["artifact"]:
        art_data = response_data["artifact"]
        language = art_data["language"]
        code_content = art_data["code"]
        
        art = Artifact(
            message_id=asst_msg.id,
            type="code",
            content=code_content,
            language=language
        )
        db.add(art)
        db.commit()
        db.refresh(art)
        artifact_id = str(art.id)
        
    return {
        "artifact_id": artifact_id,
        "language": language,
        "code": code_content,
        "message_id": str(asst_msg.id),
        "conversation_id": conv_id,
        "text_content": response_data["text_content"]
    }
