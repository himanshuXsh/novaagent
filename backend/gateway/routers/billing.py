from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.shared.db.session import get_db
from backend.shared.db.models import User, CreditTransaction
from backend.gateway.middleware.auth_guard import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/balance")
async def get_balance(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"credits": user.credits}

@router.get("/transactions")
async def get_transactions(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = db.query(CreditTransaction).filter(CreditTransaction.user_id == current_user["user_id"]).order_by(CreditTransaction.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": str(tx.id),
            "amount": tx.amount,
            "agent_type": tx.agent_type,
            "balance_after": tx.balance_after,
            "description": tx.description,
            "created_at": tx.created_at.isoformat()
        } for tx in txs
    ]
