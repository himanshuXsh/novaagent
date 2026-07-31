# 11_DEVELOPMENT_PHASES.md — NovaAgent Development Roadmap

Each phase: Objectives → Tasks → Deliverables → Completion Criteria. Work in order; don't start phase N+1 until N's completion criteria are met (see `13_PROMPTS.md` for exact prompts to execute each phase).

---

## Phase 1 — Authentication
**Objectives:** Users can securely log in with Google; sessions persist.
**Tasks:** Set up FastAPI + Authlib Google OAuth flow; JWT issuance; Redis session storage; `AuthGuard` middleware; style the Login page per `03_UI_UX_DESIGN_SYSTEM.md`.
**Deliverables:** `POST /auth/google`, `GET /auth/me`; styled `/login` page.
**Completion Criteria:** A real Google login completes end-to-end and lands the user on a protected page; an unauthenticated user is correctly redirected to `/login`.

## Phase 2 — Dashboard
**Objectives:** Users see a live overview of their workspace.
**Tasks:** Build metric endpoints (credits, messages, files, conversations); usage/agent-distribution chart endpoints; recent-activity feed; style per `03_UI_UX_DESIGN_SYSTEM.md`.
**Deliverables:** `/dashboard` page with real data, Plotly charts.
**Completion Criteria:** Dashboard reflects real counts from Postgres, not hardcoded values; visually matches the reference Dashboard screen.

## Phase 3 — Chat Agent
**Objectives:** Core conversational agent works end-to-end.
**Tasks:** `chat_node` (Groq call + Redis short-term memory); conversation/message CRUD; router node (explicit + inferred paths); styled Chat page with streaming bubbles.
**Deliverables:** `POST /chat/message` (SSE streaming), `GET /chat/conversations`; `/chat` page.
**Completion Criteria:** A real multi-turn conversation persists and streams correctly in the styled UI.

## Phase 4 — Coding Agent
**Objectives:** Code generation with a distinct artifact view.
**Tasks:** `code_node`; artifact panel component (Code/Preview tabs, syntax highlighting, copy/download).
**Deliverables:** `POST /agents/code`; `/coding` page.
**Completion Criteria:** A real coding prompt renders a correct, styled artifact matching the reference Coding screen.

## Phase 5 — Search Agent
**Objectives:** Grounded web search with citations.
**Tasks:** `search_node` using duckduckgo-search; result-card + citation-badge components.
**Deliverables:** `POST /agents/search`; `/search` page.
**Completion Criteria:** A real query returns cited text + image results, styled per reference.

## Phase 6 — PDF/PPT Agent
**Objectives:** Generate real downloadable documents.
**Tasks:** `pdf_node` (reportlab), `ppt_node` (python-pptx); file storage (MinIO or local disk); file-card component.
**Deliverables:** `POST /agents/pdf`, `POST /agents/ppt`, `GET /agents/files`; `/documents` page.
**Completion Criteria:** Real PDF and PPT files are generated, downloadable, and listed as styled cards.

## Phase 7 — Image Agent
**Objectives:** Image generation (or a clean placeholder if the backend isn't built yet).
**Tasks:** `image_node` (free provider, stretch) or a styled empty/placeholder state; image grid component.
**Deliverables:** `POST /agents/image` (or documented `501` placeholder); `/image` page.
**Completion Criteria:** Page matches reference visually; either real generation works or a clearly-labeled "coming soon" state is shown — never a broken/unstyled page.

## Phase 8 — RAG Assistant
**Objectives:** Document upload + grounded Q&A.
**Tasks:** Text extraction, chunking, embedding, Qdrant storage; `rag_node` with similarity-threshold fallback; document-list + citation-chip components.
**Deliverables:** `POST /rag/upload`, `POST /rag/query`; `/rag` page.
**Completion Criteria:** A real PDF upload is queryable with correct citations; an out-of-document question correctly returns "not found."

## Phase 9 — Billing
**Objectives:** Credits are tracked, deducted, and purchasable (simulated).
**Tasks:** `credit_transactions` table + deduction middleware (success-only deduction); plan cards; transaction table; `GET /credits/balance`, `POST /billing/purchase`.
**Deliverables:** `/billing` page matching reference.
**Completion Criteria:** Every agent call correctly deducts credits only on success; balance and transaction history display accurately.

## Phase 10 — Settings
**Objectives:** Users can manage their profile.
**Tasks:** `PATCH /users/me`; tabbed Settings page (Profile, API Keys, Notifications, Billing, Security) per reference.
**Deliverables:** `/settings` page.
**Completion Criteria:** Profile changes persist via a real API call; all 5 tabs render correctly styled.

## Phase 11 — Deployment
**Objectives:** NovaAgent is live on a public URL.
**Tasks:** Full `pytest` suite; GitHub Actions CI (lint → test → build); Dockerize backend + frontend; deploy to Render/Railway free tier; final cross-page visual QA against every reference screen (see `14_TESTING_QA.md`, `15_DEPLOYMENT.md`).
**Deliverables:** Live deployed URL; recorded demo covering all agents.
**Completion Criteria:** Every phase's completion criteria still hold true in the deployed environment, not just locally.

---

## Rate Limiting & Cross-Cutting Work
Not a standalone phase — implemented incrementally starting in Phase 3 (once the first real endpoint exists) and hardened by Phase 11: Redis sliding-window rate limiter per `user_id + endpoint`, per `06_SYSTEM_ARCHITECTURE.md`.
