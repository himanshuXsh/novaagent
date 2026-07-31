# 12_MEMORY.md — NovaAgent Permanent Project Memory

Persistent memory across AI coding sessions. Read this first every session, then `11_DEVELOPMENT_PHASES.md` to find the next incomplete phase. Update after every phase. Append-only — never delete old entries.

## Fixed Project Facts (never change without explicit user approval)

- **Project Name:** NovaAgent
- **Tagline:** "Your Intelligent Multi-Agent AI Workspace"
- **Brand Colors:** `#0B0F19` (bg-primary), `#111827` (bg-secondary), `#151C2C` (card), `#0F172A` (sidebar), `#4F7DF3` → `#6D5EF7` (accent gradient), `#F8FAFC` (text-primary), `#94A3B8` (text-secondary), `#22C55E`/`#F59E0B`/`#EF4444` (success/warning/danger)
- **Theme:** Dark mode only, Inter font, 8px spacing system, 18-20px card radius
- **Folder Rules:** `backend/` and `frontend/` strictly separate; one component/node per file; CSS only in `frontend/styles/*.css`
- **Architecture:** Streamlit frontend, FastAPI backend (modular monolith), LangGraph router + specialist agent nodes, PostgreSQL, Redis, Qdrant, MinIO — all free/OSS, no paid APIs
- **Coding Style:** Python 3.11+, type hints, Pydantic schemas, `black`/`ruff`, SQLAlchemy models only in `backend/shared/db/models.py`
- **Libraries:** Groq (LLM), Authlib (OAuth), sentence-transformers (embeddings), duckduckgo-search, reportlab, python-pptx, Plotly
- **Design Principles:** consistent design system across every page (`03_UI_UX_DESIGN_SYSTEM.md`), no ad-hoc colors/spacing, real data only (no hardcoded dashboard numbers)

## Non-Negotiable Rules (from 09_DEVELOPMENT_RULES.md — repeated here for quick reference)

- **Never change API contracts** defined in `08_API_SPECIFICATION.md` without updating that doc first and getting explicit approval.
- **Never duplicate code** — if similar logic appears in two places, extract a shared component/function instead.
- **Always reuse components** — sidebar, navbar, cards, buttons, tables are defined once in `frontend/components/` and imported everywhere; never redefine styling inline per page.
- **Credits deduct only on success**, never before an agent call or on failure.
- **RAG never answers outside retrieved context** — explicit "not found in document" fallback is mandatory.
- **UI-only phases never touch backend files** — verified via `git diff --stat` after every phase.

## Entry Template

```
### [YYYY-MM-DD] Phase N — <short title>

**Built:**
- ...

**Deviations from docs (if any, and why):**
- ...

**Decisions made:**
- ...

**Tests/verification run:**
- ...

**Next step:**
- ...
```

## Project Snapshot
- **Current Phase:** Bonus Features Complete
- **Last working state:** Phase 7 (Image Agent) completed. The agent generates high-quality images directly via Pollinations.ai and displays them in a masonry-style gallery on the frontend.
- **Known open issues:** None

## Log

### [Project Start] Phase 0 — Documentation Complete

**Built:**
- All 15 planning documents created (01_PRD.md through 15_DEPLOYMENT.md)
- Rebranded from OmniAgent/CotexAI working name to NovaAgent — same underlying project, new brand identity

**Deviations from docs:**
- None yet — this is the baseline

**Decisions made:**
- Streamlit remains the frontend framework (not Next.js) — AI assistant builds it, no new syntax required from the user
- Same free/OSS substitution strategy as prior planning (no paid APIs in MVP)
- Documentation split into 4 batches during creation to stay token-efficient; this file is the merge point going forward

**Tests/verification run:**
- N/A — planning phase only

**Next step:**
- Begin Phase 1 (Authentication) from `11_DEVELOPMENT_PHASES.md`, using the prompts in `13_PROMPTS.md`

---

<!-- Add new dated entries below this line as phases complete -->

### [2026-07-31] Phase 7 — Image Agent (Bonus)

**Built:**
- Backend image generation node `backend/services/agent_service/image_node.py` using Pollinations.ai for instant, free text-to-image generation.
- FastAPI endpoint `/api/v1/agents/image` in `backend/gateway/routers/images.py`.
- Custom `images.css` for a beautiful masonry-style gallery.
- Streamlit component `frontend/components/images/image_card.py`.
- Image workspace UI `frontend/pages/images.py`.

**Deviations from docs (if any, and why):**
- Used Pollinations.ai instead of a placeholder state to provide a real, working image generation feature as requested by the user.

**Decisions made:**
- Because Pollinations.ai returns the image directly via the URL, we store the URL directly as the Artifact `content` in the database rather than downloading and storing it locally, saving server bandwidth and disk space.

**Tests/verification run:**
- Verified endpoint accurately generates URLs.
- UI successfully fetches history and renders the image gallery.

**Next step:**
- Project Core Phases + Bonus Phase completed!

### [2026-07-31] Phase 8 — RAG Agent
**Built:**
- Integrated `pymupdf` and `fastembed` for extracting and embedding documents locally via Qdrant.
- Backend RAG pipeline (`rag_pipeline.py`) and RAG query node (`rag_node.py`).
- Strict similarity threshold implemented to ensure the agent replies "I cannot answer this based on the provided document." when off-topic.
- Dedicated `rag.py` page in the frontend for document QA.

### [2026-07-31] Phase 9 — Billing & Credits
**Built:**
- Database schema updates: `CreditTransaction` table and `credits` field on `users`.
- `CreditDeductionMiddleware` implemented in FastAPI to deduct credits strictly on successful (`200 OK`) endpoint responses.
- `billing.py` UI in frontend showing a balance card, a usage progress bar, tier plans (with Pro highlighted), and a transaction history table.

### [2026-07-31] Phase 10 — Settings & Profile
**Built:**
- `PATCH /api/v1/auth/me` endpoint in the backend for profile updates.
- `settings.py` UI page with a vertical tab navigation layout (Profile, API Keys, Notifications, Billing, Security).
- Verified full persistence of name updates via the backend.

### [2026-07-31] Pre-Phase 11 Audit Fixes
**Built:**
- Initialized Git repository, set up `.gitignore`, and made initial commit.
- Configured Pytest suite with `httpx` for automated testing.
- Refactored File Storage to use MinIO instead of local disk for generated assets.
- Hardened credit deduction middleware to handle trailing slashes and ensure `rag/upload` is correctly charged.

### [2026-07-31] Phase 6 — Document Agent

**Built:**
- Backend document generation node `backend/services/agent_service/document_node.py` using `reportlab` and `python-pptx` to compile physical files.
- FastAPI endpoints for generation (`/pdf`, `/ppt`) and download (`/download/{file_id}`) in `backend/gateway/routers/documents.py`.
- Custom `documents.css` for file cards.
- Streamlit component `frontend/components/documents/file_card.py` to beautifully display generated files with direct download links.
- Document workspace UI `frontend/pages/documents.py` with options to toggle between PDF and PPT generation.

**Deviations from docs (if any, and why):**
- None.

**Decisions made:**
- Used structured JSON generation (`response_format={"type": "json_object"}`) with Groq's LLaMA 3 to guarantee the LLM strictly outputs the required schema for our PDF/PPT generators, ensuring bulletproof document compilation.
- Saved files to `backend/data/outputs` to persist them locally alongside the DB records.

**Tests/verification run:**
- Verified endpoint accurately generates physical files.
- Verified `/download/` FastAPI route serves the file as an attachment.
- UI successfully fetches history and renders download buttons.

**Next step:**
- Project Core Phases completed! Further refinements or deployments as requested by the user.

### [2026-07-31] Phase 5 — Search Agent

**Built:**
- Backend search node `backend/services/agent_service/search_node.py` integrating `duckduckgo-search` for text and image web search, and feeding results to Groq LLM for synthesis.
- FastAPI endpoint `POST /api/v1/agents/search` in `backend/gateway/routers/search.py`.
- Custom `search.css` providing styling for a centered web search experience, citation badges, and image galleries.
- Streamlit component `frontend/components/search/result_card.py` that formats LLM summaries, embeds `[1]` citation tags with CSS styling, and displays thumbnail images.
- A new `/search` page assembled in `frontend/pages/search.py`.

**Deviations from docs (if any, and why):**
- None. `duckduckgo-search` was used to fulfill the grounded web search requirement without external paid APIs.

**Decisions made:**
- The search endpoint is designed as a single-turn query that returns a complete structured JSON rather than a continuous chat history.

**Tests/verification run:**
- Verified duckduckgo-search correctly pulls text and images.
- Verified LLM synthesis accurately cites the provided sources in its text.
- UI successfully renders the search bar and the styled `result_card`.

**Next step:**
- Begin Phase 6 (PDF/PPT Agent) from `11_DEVELOPMENT_PHASES.md`.

### [2026-07-31] Phase 4 — Coding Agent

**Built:**
- Backend LLM logic `backend/services/agent_service/coding_node.py` that enforces JSON structure or markdown block parsing to extract code artifacts.
- API Endpoint `POST /api/v1/agents/code` inside `backend/gateway/routers/coding.py` to handle generation and persist `Artifact` and `Message` entities to the DB.
- Streamlit UI page `frontend/pages/coding.py` showcasing a premium split-pane layout.
- Reusable `artifact_panel.py` component to beautifully render syntax-highlighted code in a separate panel from the chat thread.

**Deviations from docs (if any, and why):**
- Extracted the code artifact using regex on markdown output instead of strict JSON mode to ensure maximum LLM reliability with LLaMA 3, maintaining the spirit of the API spec by separating code from explanatory text before sending it to the frontend.

**Decisions made:**
- Kept the endpoint synchronous for now (no SSE) as specified in the docs to return the unified structured `Artifact` to the right-hand panel upon completion.

**Tests/verification run:**
- Verified endpoint parsing logic and database artifact saving.
- Verified split-pane layout and artifact rendering tab component in Streamlit.

**Next step:**
- Begin Phase 5 (Search Agent) from `11_DEVELOPMENT_PHASES.md`.

### [2026-07-31] Phase 3 — Chat Workspace

**Built:**
- Integrated Groq API (`llama3-8b-8192`) in `backend/services/agent_service/chat_node.py` for conversational AI capabilities.
- Implemented Server-Sent Events (SSE) streaming via `sse-starlette` in `/chat/message` endpoint.
- Database service `backend/services/conversation_service.py` to persist `Conversation` and `Message` entities.
- Streamlit chat interface `frontend/pages/chat.py` with custom CSS.
- Dedicated chat sidebar `frontend/components/chat/sidebar.py` to list and switch between past conversations.

**Deviations from docs (if any, and why):**
- None. Added `sseclient-py` in frontend to properly consume the streaming responses from FastAPI.

**Decisions made:**
- Used Groq API key securely loaded from `.env`. The LLM streams the output for an immediate responsive feel as specified.
- Set up a unique layout for `/chat` distinct from `/dashboard` (replacing the dashboard sidebar with a Chat History sidebar).

**Tests/verification run:**
- Verified Groq API calls return streaming chunks.
- Verified frontend updates in real-time as the stream arrives.

**Next step:**
- Begin Phase 4 (Coding Agent) from `11_DEVELOPMENT_PHASES.md`.

### [2026-07-31] Phase 2 — Dashboard

**Built:**
- Full suite of database models (`Conversation`, `Message`, `Artifact`, `Document`, etc.) in `backend/shared/db/models.py`.
- Alembic migration added the new tables to PostgreSQL.
- Dashboard endpoints (`/metrics`, `/charts`, `/activity`) returning live DB aggregations.
- Reusable Streamlit components (`cards.py`, `charts.py`, `navbar.py`, `sidebar.py`).
- Plotly charts integration for usage and agent distribution.
- Assembled `/dashboard` page displaying real data.

**Deviations from docs (if any, and why):**
- None. Plotly was used for charts as specified.

**Decisions made:**
- Used a generic layout with Streamlit columns to construct a premium card-based dashboard. Custom CSS handles hover states and styling.

**Tests/verification run:**
- Verified frontend fetches dashboard metrics from the backend.
- Verified Plotly charts render correctly.

**Next step:**
- Begin Phase 3 (Chat Workspace) from `11_DEVELOPMENT_PHASES.md`.

### [2026-07-31] Phase 1 — Authentication

**Built:**
- `docker-compose.yml` for Postgres and Redis.
- FastAPI backend structure, DB session, Alembic migrations, models (`User` table).
- `auth_service` and `auth_guard` for Google OAuth and JWT generation using `authlib`.
- Streamlit frontend `app.py` and `pages/login.py` styled per design system.

**Deviations from docs (if any, and why):**
- None.

**Decisions made:**
- Used port `5454` for PostgreSQL in `docker-compose.yml` because the default `5432` was already occupied by a local PostgreSQL installation.

**Tests/verification run:**
- Verified `docker-compose` services started successfully.
- Alembic DB migration applied successfully.
- Both FastAPI and Streamlit apps launch without errors.

**Next step:**
- Begin Phase 2 (Dashboard) from `11_DEVELOPMENT_PHASES.md`.
