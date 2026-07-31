from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from backend.shared.db.session import get_db
from backend.shared.db.models import Conversation, Message, Artifact
from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.image_node import generate_image_url

router = APIRouter(prefix="/agents/image", tags=["Image Agent"])

class ImageRequest(BaseModel):
    prompt: str

@router.post("")
async def create_image(req: ImageRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    image_url = generate_image_url(req.prompt)
    
    # Track conversation
    conv = Conversation(user_id=current_user["user_id"], title=req.prompt[:30], agent_type="images")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    # Store user prompt as message
    user_msg = Message(conversation_id=conv.id, role="user", content=req.prompt, agent_type="images")
    db.add(user_msg)
    
    # Store assistant response as message
    asst_msg = Message(conversation_id=conv.id, role="assistant", content="Generated Image", agent_type="images")
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)
    
    # Store image artifact (we store the URL as the content)
    art = Artifact(
        message_id=asst_msg.id,
        type="image",
        content=image_url
    )
    db.add(art)
    db.commit()
    db.refresh(art)
    
    return {
        "artifact_id": str(art.id),
        "url": image_url,
        "prompt": req.prompt
    }

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find all image artifacts belonging to this user
    res = db.query(Artifact, Message).join(Message).join(Conversation).filter(
        Conversation.user_id == current_user["user_id"],
        Conversation.agent_type == "images",
        Artifact.type == "image"
    ).order_by(Artifact.created_at.desc()).all()
    
    output = []
    for art, msg in res:
        # The prompt is the user message right before this assistant message.
        # But we can just find the user message for this conversation id.
        user_prompt = db.query(Message).filter(
            Message.conversation_id == msg.conversation_id,
            Message.role == "user"
        ).first()
        
        output.append({
            "id": str(art.id),
            "url": art.content,
            "prompt": user_prompt.content if user_prompt else "Unknown prompt",
            "created_at": art.created_at.isoformat()
        })
        
    return output
