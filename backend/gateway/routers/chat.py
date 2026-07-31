import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.shared.db.session import get_db
from backend.gateway.middleware.auth_guard import get_current_user
from backend.services.conversation_service import (
    create_conversation, get_user_conversations, get_messages, add_message
)
from backend.services.agent_service.chat_node import stream_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    content: str
    agent_type: str = "chat"

@router.get("/conversations")
async def list_conversations(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    convs = get_user_conversations(db, current_user["user_id"])
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

@router.post("/message")
async def send_message(req: ChatRequest, request: Request, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user["user_id"]
    
    conv_id = req.conversation_id
    if not conv_id:
        title = req.content[:30] + "..." if len(req.content) > 30 else req.content
        conv = create_conversation(db, user_id, title, req.agent_type)
        conv_id = str(conv.id)
        
    # Save user message
    add_message(db, conv_id, "user", req.content, req.agent_type)
    
    async def event_generator():
        full_assistant_content = ""
        # SSE format
        async for chunk_str in stream_chat_response(db, conv_id, req.content, req.agent_type):
            if await request.is_disconnected():
                break
                
            chunk = json.loads(chunk_str)
            if chunk.get("done"):
                full_assistant_content = chunk.get("full_content", "")
                
                # Save assistant message to DB
                # Note: db session in generator might be risky if closed, but we are in a Depends scope.
                add_message(db, conv_id, "assistant", full_assistant_content, req.agent_type)
                
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
