import json
from backend.shared.redis_client import redis_client

async def get_recent_messages(conv_id: str, limit: int = 10):
    """Fetch recent messages for a conversation from Redis memory buffer."""
    key = f"conv:{conv_id}:memory"
    # Redis lrange returns list of strings from left to right (0 to -1)
    msgs = await redis_client.lrange(key, 0, limit - 1)
    
    formatted = []
    for m in msgs:
        try:
            data = json.loads(m)
            # data is {"role": "...", "content": "..."}
            formatted.append(data)
        except:
            pass
            
    # Reverse to return in chronological order since we push to left
    return formatted[::-1]

async def add_message_to_memory(conv_id: str, role: str, content: str):
    """Add a single message to the conversation Redis memory buffer."""
    key = f"conv:{conv_id}:memory"
    data = json.dumps({"role": role, "content": content})
    # Push to left
    await redis_client.lpush(key, data)
    # Keep only the last 20 messages in active memory
    await redis_client.ltrim(key, 0, 19)
    # Expire memory after 1 hour of inactivity
    await redis_client.expire(key, 3600)
