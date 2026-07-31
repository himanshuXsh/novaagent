from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.shared.db.session import get_db
from backend.shared.db.models import User
from backend.services.auth_service.oauth import oauth
from backend.services.auth_service.jwt_utils import create_access_token
from backend.gateway.middleware.auth_guard import get_current_user
from backend.shared.redis_client import redis_client
from backend.gateway.routers import dashboard, chat, coding, search, documents, images, rag, billing
import uuid
import json

router = APIRouter(prefix="/api/v1")
router.include_router(dashboard.router, prefix="", tags=["Dashboard"])
router.include_router(chat.router, prefix="", tags=["Chat"])
router.include_router(coding.router, prefix="", tags=["Coding Agent"])
router.include_router(search.router, prefix="", tags=["Search Agent"])
router.include_router(documents.router, prefix="", tags=["Document Agent"])
router.include_router(images.router, prefix="", tags=["Image Agent"])
router.include_router(rag.router, prefix="", tags=["RAG Agent"])
router.include_router(billing.router, prefix="", tags=["Billing"])

@router.get("/auth/google/login")
async def google_login(request: Request):
    # Determine the absolute redirect URI using the request object
    redirect_uri = request.url_for('google_auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
    except Exception as e:
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")
    
    email = user_info.get("email")
    name = user_info.get("name")
    google_id = user_info.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name, google_id=google_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    session_id = str(uuid.uuid4())
    # store session for 24 hours
    await redis_client.setex(f"session:{session_id}", 86400, str(user.id))
    
    jwt_token = create_access_token(data={"session_id": session_id})
    
    # Redirect back to Streamlit frontend with JWT
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"http://localhost:8501/?jwt={jwt_token}")


@router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "credits_balance": user.credits_balance
    }

from pydantic import BaseModel

class UserProfileUpdate(BaseModel):
    name: str

@router.patch("/auth/me")
async def update_me(update_data: UserProfileUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.name = update_data.name
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "credits_balance": user.credits_balance
    }
