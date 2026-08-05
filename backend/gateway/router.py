import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.gateway.middleware.auth_guard import get_current_user
from backend.gateway.routers import (
    billing,
    chat,
    coding,
    dashboard,
    documents,
    images,
    rag,
    search,
)
from backend.services.auth_service.jwt_utils import create_access_token
from backend.services.auth_service.oauth import oauth
from backend.shared.db.models import User
from backend.shared.db.session import get_db
from backend.shared.redis_client import redis_client

router = APIRouter(prefix="/api/v1")
router.include_router(dashboard.router, prefix="", tags=["Dashboard"])
router.include_router(chat.router, prefix="", tags=["Chat"])
router.include_router(coding.router, prefix="", tags=["Coding Agent"])
router.include_router(search.router, prefix="", tags=["Search Agent"])
router.include_router(documents.router, prefix="", tags=["Document Agent"])
router.include_router(images.router, prefix="", tags=["Image Agent"])
router.include_router(rag.router, prefix="", tags=["RAG Agent"])
router.include_router(billing.router, prefix="", tags=["Billing"])

from backend.shared.logger import get_logger
logger = get_logger(__name__)

@router.get("/auth/google/login")
async def google_login(request: Request):
    # Determine the absolute redirect URI. 
    # Use API_BASE_URL to avoid Docker internal hostname leaking.
    api_base_url = os.environ.get("API_PUBLIC_URL", "http://localhost:8000/api/v1")
    redirect_uri = f"{api_base_url}/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
    except Exception as e:
        logger.error(f"Google OAuth failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    if not user_info:
        logger.error("Google OAuth succeeded but no user_info returned")
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
    try:
        await redis_client.setex(f"session:{session_id}", 86400, str(user.id))
    except Exception as e:
        logger.error(f"Failed to store session in Redis: {e}")
        raise HTTPException(status_code=500, detail="Session creation failed")
    
    jwt_token = create_access_token(data={"session_id": session_id})
    
    # Redirect back to Streamlit frontend with JWT
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8502")
    return RedirectResponse(url=f"{frontend_url}/?jwt={jwt_token}")


@router.get("/auth/dev-login")
async def dev_login(request: Request, db: Session = Depends(get_db)):
    """DEV ONLY: Create/fetch a test user and return a valid JWT redirect.
    This endpoint should be disabled in production."""
    if os.environ.get("ENV", "development") == "production":
        raise HTTPException(status_code=404, detail="Not found")

    dev_email = "dev@novaagent.local"
    user = db.query(User).filter(User.email == dev_email).first()
    if not user:
        user = User(email=dev_email, name="Dev User", google_id="dev-local")
        db.add(user)
        db.commit()
        db.refresh(user)

    session_id = str(uuid.uuid4())
    await redis_client.setex(f"session:{session_id}", 86400, str(user.id))
    jwt_token = create_access_token(data={"session_id": session_id})

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8502")
    return RedirectResponse(url=f"{frontend_url}/?jwt={jwt_token}")


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
