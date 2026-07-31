from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.shared.db.models import User, Conversation, Message, GeneratedFile, CreditTransaction
from datetime import datetime, timedelta

def get_dashboard_metrics(db: Session, user_id: str):
    # Total conversations
    conversations_count = db.query(Conversation).filter(Conversation.user_id == user_id).count()
    
    # Total messages (user and assistant)
    # Get all conversations for user, then count messages
    messages_count = db.query(Message).join(Conversation).filter(Conversation.user_id == user_id).count()
    
    # Total files generated
    files_count = db.query(GeneratedFile).filter(GeneratedFile.user_id == user_id).count()
    
    # Credits balance
    user = db.query(User).filter(User.id == user_id).first()
    credits_balance = user.credits_balance if user else 0
    
    return {
        "conversations": conversations_count,
        "messages": messages_count,
        "files": files_count,
        "credits": credits_balance
    }

def get_dashboard_charts(db: Session, user_id: str):
    # Credits usage over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    usage_data = db.query(
        func.date(CreditTransaction.created_at).label('date'),
        func.sum(CreditTransaction.amount).label('total_used')
    ).filter(
        CreditTransaction.user_id == user_id,
        CreditTransaction.amount < 0,
        CreditTransaction.created_at >= thirty_days_ago
    ).group_by(func.date(CreditTransaction.created_at)).all()
    
    usage_chart = [{"date": str(d), "used": abs(u)} for d, u in usage_data]
    
    # Agent distribution
    agent_data = db.query(
        Conversation.agent_type,
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.user_id == user_id
    ).group_by(Conversation.agent_type).all()
    
    distribution_chart = [{"agent": a, "count": c} for a, c in agent_data]
    
    return {
        "usage": usage_chart,
        "distribution": distribution_chart
    }

def get_dashboard_activity(db: Session, user_id: str):
    # Recent 5 conversations
    recent_convs = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.created_at.desc()).limit(5).all()
    
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "agent_type": c.agent_type,
            "created_at": c.created_at.isoformat()
        }
        for c in recent_convs
    ]
