# 10_PROJECT_STRUCTURE.md — NovaAgent Complete Folder Structure

```
novaagent/
├── backend/
│   ├── gateway/
│   │   ├── __init__.py
│   │   ├── router.py              # top-level FastAPI route registration
│   │   └── middleware/
│   │       ├── auth_guard.py
│   │       └── rate_limiter.py
│   ├── services/
│   │   ├── auth_service/
│   │   │   ├── oauth.py           # Authlib Google OAuth flow
│   │   │   └── jwt_utils.py
│   │   ├── chat_service/
│   │   │   └── conversations.py   # conversation/message CRUD
│   │   ├── agent_service/
│   │   │   ├── graph.py           # LangGraph router + graph assembly
│   │   │   └── nodes/
│   │   │       ├── chat_node.py
│   │   │       ├── code_node.py
│   │   │       ├── pdf_node.py
│   │   │       ├── ppt_node.py
│   │   │       ├── search_node.py
│   │   │       ├── image_node.py
│   │   │       └── rag_node.py
│   │   └── billing_service/
│   │       └── credits.py         # deduction guard, ledger writes
│   ├── shared/
│   │   ├── redis_client.py
│   │   ├── db/
│   │   │   ├── models.py          # SQLAlchemy models (07_DATABASE_DESIGN.md)
│   │   │   └── session.py
│   │   └── config.py              # env var loading
│   ├── alembic/                   # migrations (07_DATABASE_DESIGN.md plan)
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_agents.py
│   │   ├── test_billing.py
│   │   └── test_rag.py
│   ├── docker-compose.yml         # Postgres, Redis, Qdrant, MinIO
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app.py                     # entry point, injects CSS, renders shell
│   ├── components/
│   │   ├── layout/
│   │   │   ├── sidebar.py
│   │   │   └── navbar.py
│   │   ├── cards.py
│   │   ├── buttons.py
│   │   ├── tables.py
│   │   ├── charts.py
│   │   ├── chat.py
│   │   ├── artifact_panel.py
│   │   ├── file_card.py
│   │   └── profile.py
│   ├── styles/
│   │   ├── theme.css
│   │   ├── layout.css
│   │   ├── sidebar.css
│   │   ├── dashboard.css
│   │   ├── chat.css
│   │   ├── agents.css
│   │   ├── forms.css
│   │   ├── tables.css
│   │   └── responsive.css
│   ├── pages/
│   │   ├── login.py
│   │   ├── dashboard.py
│   │   ├── chat.py
│   │   ├── coding.py
│   │   ├── search.py
│   │   ├── pdf.py
│   │   ├── image.py
│   │   ├── rag.py
│   │   ├── billing.py
│   │   └── settings.py
│   ├── utils/
│   │   └── api_client.py          # all backend API calls, single source
│   └── assets/
│       ├── logo/                  # per 04_LOGO_BRANDING.md exports
│       └── icons/
├── docs/                          # this entire 15-file documentation set
│   ├── 01_PRD.md ... 15_DEPLOYMENT.md
├── .github/
│   └── workflows/
│       └── ci.yml                 # lint -> test -> build (11/15_DEPLOYMENT.md)
├── .gitignore
└── README.md
```

## Layer Responsibilities

| Folder | Owns |
|---|---|
| `backend/gateway/` | HTTP routing, auth/rate-limit middleware |
| `backend/services/` | Business logic per domain (auth, chat, agents, billing) |
| `backend/shared/` | Cross-cutting infra (DB session, Redis client, config) |
| `frontend/components/` | Reusable, styled, presentation-only UI pieces |
| `frontend/pages/` | Page composition — components + `api_client.py` calls |
| `frontend/styles/` | All CSS, token-driven, no page-specific hardcoded values |
| `frontend/utils/api_client.py` | The ONLY place frontend code calls the backend — single boundary, easy to audit |

## Configuration
- `backend/.env.example` lists every required variable (Groq key, DB URL, Redis URL, Qdrant URL, MinIO credentials, Google OAuth client ID/secret, JWT secret) with placeholder values — real `.env` is git-ignored.
- `frontend/` reads its backend base URL from a single `API_BASE_URL` env var — no hardcoded `localhost` URLs scattered through page files.
