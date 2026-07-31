# 06_SYSTEM_ARCHITECTURE.md — NovaAgent System Architecture

## High-Level Architecture

```
Streamlit Frontend
        │
        ▼
   FastAPI Gateway ── Google OAuth (Authlib) ── Redis (sessions + rate limits)
        │
        ▼
 LangGraph Orchestrator (Router Node)
        │
        ├── Chat Agent ─────────► Groq (Llama 3.1, free)
        ├── Coding Agent ───────► Groq (code-capable model, free)
        ├── PDF/PPT Agent ───────► reportlab / python-pptx (OSS) ──► MinIO
        ├── Search Agent ────────► duckduckgo-search (free)
        ├── Image Agent ─────────► Pollinations.ai / HF free inference (stretch)
        └── RAG Agent ───────────► sentence-transformers ──► Qdrant
        │
        ▼
PostgreSQL (users, conversations, messages, artifacts, documents, credits)
```

## Free/Open-Source Substitution Table

| Component | Paid original | NovaAgent's free/OSS choice |
|---|---|---|
| Database | MongoDB | PostgreSQL + SQLAlchemy |
| Auth | Firebase Auth | FastAPI + Authlib (Google OAuth) + JWT |
| File storage | AWS S3 | MinIO (self-hosted, S3-compatible) or local disk for MVP |
| Billing | Razorpay (live) | Mocked credits ledger; Razorpay Test Mode as stretch |
| LLM | DeepSeek via OpenRouter (paid) | Groq free tier |
| Image gen | DALL-E / Stability | Pollinations.ai or HF free inference (stretch) |
| Search | Tavily (paid tiers) | duckduckgo-search (free, no key) |
| Deployment | AWS ECR/ECS | Docker Compose + Render/Railway free tier |

## Frontend
- Streamlit, custom CSS design system (per `03_UI_UX_DESIGN_SYSTEM.md`), component-based structure (`components/`, `styles/`, `pages/`) — see `10_PROJECT_STRUCTURE.md` for the full tree.

## Backend — FastAPI
- Modular monolith: `gateway/` (routing, auth middleware, rate limiting) + `services/` (auth, chat, agent, billing) + `shared/` (db, redis, middleware).
- Async endpoints; `StreamingResponse` (SSE) for chat/agent token streaming.

## LangGraph (Agent Routing)
- `router_node`: explicit agent-card selection OR lightweight intent classification → dispatches to one specialist node.
- Specialist nodes (`chat`, `code`, `pdf`, `ppt`, `search`, `image`, `rag`) each write only to their own `AgentState` output fields.
- `response_formatter_node`: normalizes output shape before returning to the API layer.

## Redis
- Session storage (JWT session_id → user_id, TTL-based).
- Short-term chat memory (last N messages per conversation, injected into prompts).
- Rate-limit counters (sliding window, per `user_id + endpoint`).

## Qdrant
- Vector store for RAG: `document_chunks` embeddings, filtered by `document_id` on query, similarity-threshold gate before answering.

## PostgreSQL
- System of record for users, conversations, messages, artifacts, documents, document_chunks (metadata only — vectors live in Qdrant), credit_transactions. Full schema in `07_DATABASE_DESIGN.md`.

## Storage
- MinIO (self-hosted, S3 API-compatible) for generated files (PDF/PPT/images) and uploaded documents; local disk acceptable for a simpler MVP milestone before MinIO is wired in.

## Authentication
- Google OAuth via Authlib → backend issues short-lived JWT access token → Redis-backed session → `AuthGuard` middleware validates on every protected route.

## Billing
- `credit_transactions` table is the source of truth; a deduction middleware wraps every agent call and only writes a deduction row on a **successful** response (never before the call, never on failure).

## Agent Routing (Detail)
- Explicit path: user clicks an Agent Card → `agent_type` is set on the request → router skips classification, dispatches directly.
- Inferred path: user types in the default Chat box with no `agent_type` → router runs a short classification prompt → defaults to `chat` on ambiguity (never a dead-end "couldn't understand" response).

## Sequence Diagram — One Agent Call

```
User        Frontend       Gateway        Router         Agent Node      Credits       DB/Redis
 │             │               │             │               │              │             │
 │─send msg───▶│               │             │               │              │             │
 │             │─POST /agent──▶│              │               │              │             │
 │             │               │─auth check──▶│               │              │             │
 │             │               │              │─classify/route▶              │             │
 │             │               │              │               │─call model──▶│             │
 │             │               │              │               │◀─response────│             │
 │             │               │              │               │─deduct──────▶│             │
 │             │               │              │               │─persist msg─────────────────▶│
 │             │◀──stream tokens───────────────────────────────│              │             │
 │◀─render─────│               │              │               │              │             │
```

## Sequence Diagram — RAG Query

```
User → Frontend: upload PDF
Frontend → API: POST /rag/upload
API → Extractor: extract text
API → Chunker: chunk (~500 tok, 50 overlap)
API → Embedder: embed each chunk (sentence-transformers)
API → Qdrant: store {vector, document_id, chunk_text}
API → Postgres: log document status = "Processed"
API → Frontend: {document_id, status}

User → Frontend: ask question
Frontend → API: POST /rag/query {document_id, question}
API → Embedder: embed question
API → Qdrant: similarity search (top_k=4, filtered by document_id)
API → API: score below threshold? → "not found in document"
                                   → else inject chunks → LLM → grounded answer + citations
API → Frontend: {answer, sources}
```

## Folder Structure
See `10_PROJECT_STRUCTURE.md` for the complete tree (frontend + backend).

## Data Flow (Summary)
```
Browser (Streamlit) ⇄ FastAPI Gateway ⇄ LangGraph Orchestrator ⇄ Groq/DuckDuckGo/Qdrant/MinIO
                                    ⇅
                              PostgreSQL + Redis (system of record + cache/session)
```
