from fastapi import APIRouter, Depends, Request, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.search_node import generate_search_response
from backend.services.conversation_service import create_conversation, add_message
from backend.shared.db.session import get_db

router = APIRouter(prefix="/agents/search", tags=["Search Agent"])

class SearchRequest(BaseModel):
    query: str

def save_search_background(user_id: str, query: str, full_answer: str, sources: list, images: list):
    from backend.shared.db.session import SessionLocal
    db = SessionLocal()
    try:
        title = query[:30] + "..." if len(query) > 30 else query
        conv = create_conversation(db, user_id, title, "search")
        add_message(db, str(conv.id), "user", query, "search")
        
        import json
        assistant_content = json.dumps({
            "answer": full_answer,
            "sources": sources,
            "images": images
        })
        add_message(db, str(conv.id), "assistant", assistant_content, "search")
    finally:
        db.close()

@router.post("")
async def perform_search(req: SearchRequest, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    user_id = current_user["user_id"]
    
    async def event_generator():
        full_answer = ""
        sources = []
        images = []
        
        async for chunk_str in generate_search_response(req.query):
            if await request.is_disconnected():
                break
                
            chunk = json.loads(chunk_str)
            event_type = chunk.get("event")
            
            if event_type == "done":
                background_tasks.add_task(save_search_background, user_id, req.query, full_answer, sources, images)
                yield {
                    "event": "done",
                    "data": json.dumps({"status": "completed"})
                }
                break
            elif event_type == "metadata":
                sources = chunk.get("sources", [])
                images = chunk.get("images", [])
                yield {
                    "event": "metadata",
                    "data": json.dumps({"sources": sources, "images": images})
                }
            else:
                content = chunk.get("content", "")
                full_answer += content
                yield {
                    "event": "message",
                    "data": json.dumps({"content": content})
                }
                
    return EventSourceResponse(event_generator())
