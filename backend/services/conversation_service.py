
from sqlalchemy.orm import Session

from backend.shared.db.models import Conversation, Message


def create_conversation(db: Session, user_id: str, title: str, agent_type: str = "chat"):
    conv = Conversation(
        user_id=user_id,
        title=title,
        agent_type=agent_type
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_user_conversations(db: Session, user_id: str, agent_type: str = None, limit: int = 50):
    query = db.query(Conversation).filter(Conversation.user_id == user_id)
    if agent_type:
        query = query.filter(Conversation.agent_type == agent_type)
    return query.order_by(Conversation.created_at.desc()).limit(limit).all()

def get_conversation(db: Session, conv_id: str, user_id: str):
    return db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == user_id
    ).first()

def get_messages(db: Session, conv_id: str, limit: int = 100):
    return db.query(Message).filter(
        Message.conversation_id == conv_id
    ).order_by(Message.created_at.asc()).limit(limit).all()

def add_message(db: Session, conv_id: str, role: str, content: str, agent_type: str = "chat"):
    msg = Message(
        conversation_id=conv_id,
        role=role,
        content=content,
        agent_type=agent_type
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
