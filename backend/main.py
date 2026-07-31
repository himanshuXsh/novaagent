from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from backend.gateway.router import router
from backend.shared.config import settings

app = FastAPI(title="NovaAgent API")

from backend.gateway.middleware.credit_middleware import CreditDeductionMiddleware

# SessionMiddleware is required by Authlib for OAuth 1.0/2.0 state/nonce
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)
app.add_middleware(CreditDeductionMiddleware)

app.include_router(router)
