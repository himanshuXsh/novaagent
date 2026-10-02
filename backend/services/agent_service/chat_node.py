import json

from groq import AsyncGroq

from backend.shared.memory import get_recent_messages
from backend.shared.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

async def stream_chat_response(db, conv_id, user_message, agent_type="chat"):
    # 1. Fetch history from Redis memory
    history = await get_recent_messages(conv_id)
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. If you are not confident about a fact, say so clearly instead of guessing. Do not invent specific numbers, dates, names, or citations you are not certain about. If a question requires current/real-time information you don't have, say that clearly rather than answering as if you know."}
    ]
    
    for msg in history:
        # Avoid passing the one we are just processing if we already appended it in the router
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # We append the user message explicitly since we deferred DB and Redis writes to background
    messages.append({"role": "user", "content": user_message})
    
    # 2. Call Groq
    try:
        stream = await client.chat.completions.create(
            model=settings.groq_fast_model,
            messages=messages,
            temperature=0.3,
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
    except Exception as e:
        yield json.dumps({"content": f"\n\n[Error from API: {e!s}]"}) + "\n"
        yield json.dumps({"done": True, "full_content": f"[Error from API: {e!s}]"}) + "\n"

