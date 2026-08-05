
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.image_node import generate_image_url
from backend.shared.db.models import Artifact, Conversation, Message
from backend.shared.db.session import get_db

router = APIRouter(prefix="/agents/image", tags=["Image Agent"])

class ImageRequest(BaseModel):
    prompt: str

@router.post("")
async def create_image(req: ImageRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    image_url = generate_image_url(req.prompt)
    
    try:
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
    except Exception as e:
        db.rollback()
        from backend.shared.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"Failed to save image generation to DB: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Failed to record image generation")
    
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
    ).order_by(Message.created_at.desc()).all()
    
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
            "created_at": msg.created_at.isoformat()
        })
        
    return output


@router.delete("/{artifact_id}")
async def delete_image(
    artifact_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an image artifact. Verifies ownership before deleting."""
    from fastapi import HTTPException
    from backend.shared.logger import get_logger
    logger = get_logger(__name__)

    # Find the artifact and verify it belongs to the current user
    result = (
        db.query(Artifact, Message, Conversation)
        .join(Message, Artifact.message_id == Message.id)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(
            Artifact.id == artifact_id,
            Artifact.type == "image",
            Conversation.user_id == current_user["user_id"],
        )
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Image not found or access denied.")

    art, msg, conv = result

    try:
        # Delete artifact, messages, and conversation
        db.query(Artifact).filter(Artifact.id == art.id).delete(synchronize_session=False)
        db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
        db.delete(conv)
        db.commit()
        logger.info(f"Deleted image artifact {artifact_id} for user {current_user['user_id']}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete image artifact {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image.")

    return {"status": "deleted", "artifact_id": artifact_id}

