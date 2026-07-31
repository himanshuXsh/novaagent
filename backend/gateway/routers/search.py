from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.shared.db.session import get_db
from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.search_node import generate_search_response

router = APIRouter(prefix="/agents/search", tags=["Search Agent"])

class SearchRequest(BaseModel):
    query: str

@router.post("")
async def perform_search(req: SearchRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # In a real app we might charge credits here
    
    result = await generate_search_response(req.query)
    
    return result
