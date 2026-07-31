from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.services.auth_service.jwt_utils import verify_access_token
from backend.shared.redis_client import redis_client

security = HTTPBearer()

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user_id = await redis_client.get(f"session:{session_id}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired")
        
    if isinstance(user_id, bytes):
        user_id = user_id.decode("utf-8")
        
    request.state.user_id = user_id
    
    return {"user_id": user_id, "session_id": session_id}
