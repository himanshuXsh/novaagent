import os
import json
from groq import AsyncGroq
from backend.shared.config import settings
from backend.services.conversation_service import get_messages

client = AsyncGroq(api_key=settings.groq_api_key)

async def stream_chat_response(db, conv_id, user_message, agent_type="chat"):
    # 1. Fetch history
    history = get_messages(db, conv_id)
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    
    for msg in history:
        # We don't want to pass the one we are just processing if it's already in DB,
        # but typically we save the user message to DB *before* calling this.
        messages.append({"role": msg.role, "content": msg.content})
        
    # If the user message isn't in history yet (depends on implementation)
    # messages.append({"role": "user", "content": user_message})
    
    # 2. Call Groq
    stream = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0.7,
        stream=True,
    )
    
    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            yield json.dumps({"content": content}) + "\n"
            
    # Yield a special final chunk if needed, or we just let it end
    # We will save the response in the router using the full_response
    yield json.dumps({"done": True, "full_content": full_response}) + "\n"
