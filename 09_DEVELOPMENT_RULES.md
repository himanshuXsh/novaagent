# 09_DEVELOPMENT_RULES.md — NovaAgent Development Rules

## Folder Rules
- Frontend and backend stay in separate top-level folders (`frontend/`, `backend/`) — never mix Streamlit UI code and FastAPI route code in the same file/folder.
- One component = one file. One LangGraph node = one file. No "god files."
- CSS lives only in `frontend/styles/*.css`, never as large inline strings in `.py` files (small scoped injection points are the only exception).

## Python Style
- Python 3.11+, type hints on every function signature.
- Follow PEP 8; format with `black`, lint with `ruff`.
- Pydantic models for all FastAPI request/response schemas — no raw dicts crossing the API boundary.
- SQLAlchemy models live only in `backend/shared/db/models.py`.

## Naming
- Files/functions: `snake_case`. Classes: `PascalCase`. Constants: `UPPER_SNAKE_CASE`.
- API routes: plural nouns, kebab-free (`/agents/code`, not `/agent-code`).
- DB tables: plural snake_case (`credit_transactions`), matching `07_DATABASE_DESIGN.md` exactly — never rename a table/column without updating that doc first.

## Components (Frontend)
- Every reusable UI piece (card, button, table row, chat bubble) is a function in `components/`, imported by page modules — never redefined inline per page.
- Page modules (`pages/*.py`) primarily call components + existing API client functions; they should not contain large blocks of raw HTML/CSS.

## CSS
- Design tokens (colors, spacing, radius) defined once in `styles/theme.css`, referenced everywhere else — never hardcode a hex value or px spacing outside the token system.

## Error Handling
- Every API endpoint returns the standard error shape from `08_API_SPECIFICATION.md` (`{"error": {"code", "message"}}`) — never a raw stack trace or unhandled 500 with no body.
- Frontend never shows a raw exception to the user — always the styled Error State component (`03_UI_UX_DESIGN_SYSTEM.md`).
- Agent node failures must degrade gracefully — one agent's error must not crash the chat session or the whole request.

## Logging
- Structured JSON logs on the backend (not print statements) — include `user_id`, `agent_type`, `request_id`, `duration_ms` on every agent call.
- Never log secrets, JWTs, or full document/message content at INFO level — log identifiers/metadata, not raw sensitive payloads.

## Security
- No secrets in code — all keys/credentials via environment variables (`.env`, never committed).
- JWT short-lived access tokens; validate on every protected route via `AuthGuard` middleware.
- Rate limiting (Redis sliding window) on all agent endpoints.
- Input validation via Pydantic on every request body — never trust client input directly in a DB query (use the ORM, never raw string-interpolated SQL).

## Performance
- Credits deduction and DB writes happen after a successful agent response, not blocking the streamed response to the user.
- RAG queries always filter by `document_id` in Qdrant — never a full-collection scan.
- Cache short-term chat memory in Redis (not re-fetched from Postgres on every turn).

## Git
- One feature/phase per branch (or per commit if working directly on `main` for a solo project) — see `11_DEVELOPMENT_PHASES.md` for phase boundaries.
- `.gitignore` excludes: `venv/`, `__pycache__/`, `.env`, `chroma_db/` or vector-store local data, `node_modules/` (if any), build artifacts.
- Never commit real credentials, even temporarily "to test" — use `.env.example` with placeholder values instead.

## Commits
- Format: `Phase N: <short description>` (matches the phase-based workflow in `11_DEVELOPMENT_PHASES.md` and `13_PROMPTS.md`).
- Each commit should represent one verified, working phase deliverable — not a half-finished intermediate state.
- Run `git diff --stat` before every commit to confirm the changed files match what the phase was actually supposed to touch (frontend-only phases touch only `frontend/`, etc.).
