import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.shared.db.models import CreditTransaction, User
from backend.shared.db.session import SessionLocal

logger = logging.getLogger(__name__)

# Map endpoints to credit cost and agent type
AGENT_COSTS = {
    "/api/v1/chat/message": {"cost": 1, "type": "chat"},
    "/api/v1/agents/code": {"cost": 2, "type": "coding"},
    "/api/v1/agents/search": {"cost": 1, "type": "search"},
    "/api/v1/agents/documents/pdf": {"cost": 5, "type": "documents"},
    "/api/v1/agents/documents/ppt": {"cost": 5, "type": "documents"},
    "/api/v1/agents/image": {"cost": 5, "type": "image"},
    "/api/v1/agents/rag/query": {"cost": 2, "type": "rag"},
    "/api/v1/agents/rag/upload": {"cost": 2, "type": "rag"}
}

class CreditDeductionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only process successful POST requests to agent endpoints
        if request.method == "POST" and response.status_code == 200:
            path = request.url.path.rstrip("/")
            if path in AGENT_COSTS:
                cost_info = AGENT_COSTS[path]
                
                # Check if user_id is in request state (set by auth_guard)
                if hasattr(request.state, "user_id"):
                    user_id = request.state.user_id
                    
                    # Deduct credits
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.id == user_id).first()
                        if user:
                            # We allow negative balance in v1 or we could block it before. 
                            # Since middleware runs AFTER, we just deduct.
                            user.credits -= cost_info["cost"]
                            
                            tx = CreditTransaction(
                                user_id=user.id,
                                amount=-cost_info["cost"],
                                agent_type=cost_info["type"],
                                balance_after=user.credits,
                                description=f"Used {cost_info['type']} agent"
                            )
                            db.add(tx)
                            db.commit()
                    except Exception as e:
                        logger.error(f"Failed to deduct credits: {e}")
                    finally:
                        db.close()
                        
        return response
