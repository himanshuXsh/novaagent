from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.gateway.router import router
from backend.shared.config import settings
from backend.shared.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="NovaAgent API")

from backend.gateway.middleware.credit_middleware import CreditDeductionMiddleware

# SessionMiddleware is required by Authlib for OAuth 1.0/2.0 state/nonce
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)
app.add_middleware(CreditDeductionMiddleware)


@app.on_event("startup")
async def startup_checks():
    """Wait for all required services before accepting traffic."""
    import asyncio

    # --- PostgreSQL ---
    from backend.shared.db.session import engine
    from sqlalchemy import text
    for attempt in range(10):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL is ready.")
            break
        except Exception as e:
            logger.warning(f"PostgreSQL not ready (attempt {attempt+1}/10): {e}")
            await asyncio.sleep(2)
    else:
        logger.error("PostgreSQL did not become ready in time. Continuing anyway.")

    # --- Redis ---
    from backend.shared.redis_client import redis_client
    for attempt in range(10):
        try:
            await redis_client.ping()
            logger.info("Redis is ready.")
            break
        except Exception as e:
            logger.warning(f"Redis not ready (attempt {attempt+1}/10): {e}")
            await asyncio.sleep(2)
    else:
        logger.error("Redis did not become ready in time. Continuing anyway.")

    logger.info("All startup checks complete. NovaAgent API is accepting requests.")


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {"status": "ok", "service": "novaagent-backend"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

app.include_router(router)

