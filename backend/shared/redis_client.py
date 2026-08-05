import redis.asyncio as redis

from backend.shared.config import settings
from backend.shared.logger import get_logger

logger = get_logger(__name__)

# Add connection pooling and retry logic to Redis
redis_client = redis.from_url(
    settings.redis_url, 
    decode_responses=True,
    socket_timeout=5.0,
    socket_connect_timeout=5.0,
    retry_on_timeout=True,
    max_connections=50,
)

async def get_redis():
    try:
        # Check connection before returning it
        await redis_client.ping()
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise
    return redis_client
