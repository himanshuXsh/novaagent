import json

from fastapi import APIRouter, Depends, Request, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.agent_service.chat_node import stream_chat_response
from backend.services.conversation_service import (
    add_message,
    create_conversation,
    get_messages,
    get_user_conversations,
)
from backend.shared.db.session import get_db
from backend.shared.memory import add_message_to_memory

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    conversation_id: str | None = None
    content: str
    agent_type: str = "chat"

@router.get("/conversations")
async def list_conversations(agent_type: str = None, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    convs = get_user_conversations(db, current_user["user_id"], agent_type=agent_type)
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "agent_type": c.agent_type,
            "created_at": c.created_at.isoformat()
        } for c in convs
    ]

@router.get("/conversations/{conv_id}/messages")
async def list_messages(conv_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs = get_messages(db, conv_id)
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        } for m in msgs
    ]

async def save_message_background(conv_id: str, role: str, content: str, agent_type: str, user_id: str):
    # Save to Redis memory for fast retrieval on next turn
    await add_message_to_memory(conv_id, role, content)
    
    # Open a new DB session for background persistence to avoid closed session errors
    from backend.shared.db.session import SessionLocal
    db = SessionLocal()
    try:
        add_message(db, conv_id, role, content, agent_type)
    finally:
        db.close()


@router.post("/message")
async def send_message(req: ChatRequest, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    
    conv_id = req.conversation_id
    if not conv_id:
        title = req.content[:30] + "..." if len(req.content) > 30 else req.content
        conv = create_conversation(db, user_id, title, req.agent_type)
        conv_id = str(conv.id)
        
    # DEFER user message to background task to unblock TTFT!
    background_tasks.add_task(save_message_background, conv_id, "user", req.content, req.agent_type, user_id)
    
    async def event_generator():
        full_assistant_content = ""
        # SSE format
        async for chunk_str in stream_chat_response(db, conv_id, req.content, req.agent_type):
            if await request.is_disconnected():
                break
                
            chunk = json.loads(chunk_str)
            if chunk.get("done"):
                full_assistant_content = chunk.get("full_content", "")
                
                # DEFER assistant message to background (FastAPI will execute this after response completes)
                background_tasks.add_task(save_message_background, conv_id, "assistant", full_assistant_content, req.agent_type, user_id)
                
                yield {
                    "event": "done",
                    "data": json.dumps({"conversation_id": conv_id})
                }
                break
            else:
                yield {
                    "event": "message",
                    "data": json.dumps({"content": chunk["content"]})
                }
                
    return EventSourceResponse(event_generator())
