import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.dashboard_service import (
    get_dashboard_activity,
    get_dashboard_charts,
    get_dashboard_metrics,
    get_dashboard_search,
)
from backend.shared.db.session import get_db

os.makedirs("backend/gateway/routers", exist_ok=True)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics")
async def get_metrics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    return get_dashboard_metrics(db, user_id)

@router.get("/charts")
async def get_charts(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    return get_dashboard_charts(db, user_id)

@router.get("/activity")
async def get_activity(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    return get_dashboard_activity(db, user_id)

@router.get("/search")
async def search(q: str = "", current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not q or len(q.strip()) == 0:
        return []
    user_id = current_user["user_id"]
    return get_dashboard_search(db, user_id, q.strip())
