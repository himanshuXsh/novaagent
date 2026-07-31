# 14_TESTING_QA.md — NovaAgent Testing & QA Strategy

## Unit Testing
- Scope: pure functions with no I/O — strategy/scoring logic, formatters, validators.
- Tool: `pytest`.
- Rule: every LangGraph node gets at least one standalone unit test with a mocked LLM call (deterministic, no real API cost) before being wired into the router graph.
- Target: core business logic (credit deduction math, RAG similarity-threshold gate, router classification fallback) has explicit unit tests, not just "it ran once."

## Integration Testing
- Scope: FastAPI endpoint ↔ database ↔ Redis/Qdrant interactions using a test database (separate from dev/prod).
- Tool: `pytest` + `httpx.AsyncClient` against the FastAPI app; `pytest-asyncio`.
- Rule: every endpoint in `08_API_SPECIFICATION.md` has at least one integration test covering the happy path and one error path (e.g., insufficient credits, invalid input).

## UI Testing
- Scope: Streamlit page rendering and interaction correctness.
- Tool: browser subagent (Antigravity) for visual verification against `03_UI_UX_DESIGN_SYSTEM.md` reference screens; manual click-through for interaction flows (send message, upload file, click buttons).
- Rule: every phase's UI changes are screenshot-compared against the reference before being marked complete (per `11_DEVELOPMENT_PHASES.md`).

## API Testing
- Scope: contract correctness — request/response shapes match `08_API_SPECIFICATION.md` exactly.
- Tool: `pytest` + Pydantic schema validation; optionally a Postman/Insomnia collection mirroring the spec for manual exploration.
- Rule: status codes match the table in `08_API_SPECIFICATION.md` for every tested scenario (200/402/401/429/etc.).

## Security Testing
- Verify: no endpoint is reachable without a valid JWT except `/auth/*`.
- Verify: rate limiting actually triggers a 429 under rapid repeated requests.
- Verify: no secrets appear in logs, error responses, or committed files (scan git history for accidentally committed `.env` values before any public push).
- Verify: SQL injection is not possible — confirm all queries go through the SQLAlchemy ORM, not raw string interpolation.
- Verify: file uploads (RAG documents) are validated for type/size before processing.

## Performance Testing
- Verify: chat response begins streaming within ~2s under normal load.
- Verify: dashboard loads within ~1s using cached/indexed queries (per `07_DATABASE_DESIGN.md` index list).
- Tool: simple load testing with `locust` or repeated timed `httpx` calls — full load-testing infra is a stretch goal, not required for MVP.

## Acceptance Testing
Run through `01_PRD.md`'s Acceptance Criteria end-to-end as a real user would, on the deployed (not local) environment, before calling the project "done":
- [ ] All 7 core agents work end-to-end with real data
- [ ] Dashboard reflects live, accurate metrics
- [ ] Design system applied consistently across every screen
- [ ] RAG correctly refuses out-of-document questions
- [ ] Credits deduct only on success
- [ ] Deployed to a live free-tier URL

## Production Checklist
- [ ] All unit + integration tests passing in CI
- [ ] No hardcoded secrets anywhere in the codebase
- [ ] `.env.example` complete and up to date
- [ ] Every page screenshot-verified against reference screens
- [ ] Rate limiting verified working on all agent endpoints
- [ ] Error states never leak stack traces to the frontend
- [ ] Database migrations apply cleanly on a fresh database
- [ ] Full user journey manually walked through on the deployed environment
- [ ] `12_MEMORY.md` accurately reflects true completion status of every phase
