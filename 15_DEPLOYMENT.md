# 15_DEPLOYMENT.md — NovaAgent Production Deployment

All free-tier, per `06_SYSTEM_ARCHITECTURE.md`'s substitution table — no paid cloud billing required.

## Docker
- `backend/Dockerfile`: multi-stage build (install deps → copy app → run via `uvicorn`).
- `frontend/Dockerfile`: installs Streamlit + deps, runs via `streamlit run app.py`.

## Docker Compose (local + prod parity)
```yaml
services:
  postgres:
    image: postgres:16
    environment: [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7
  qdrant:
    image: qdrant/qdrant
    volumes: [qdrant_data:/qdrant/storage]
  minio:
    image: minio/minio
    command: server /data
    environment: [MINIO_ROOT_USER, MINIO_ROOT_PASSWORD]
  backend:
    build: ./backend
    depends_on: [postgres, redis, qdrant, minio]
  frontend:
    build: ./frontend
    depends_on: [backend]
volumes:
  pgdata:
  qdrant_data:
```

## Nginx
- Reverse proxy in front of both `frontend` (Streamlit, port 8501) and `backend` (FastAPI, port 8000), routing `/api/*` to backend and everything else to frontend. Only needed for a single-VM deployment style; Render/Railway handle this automatically for their managed services.

## HTTPS
- Render/Railway/Fly.io provide free automatic HTTPS (Let's Encrypt) on their default subdomains — no manual certificate management needed for the free-tier deployment path.

## Redis / Qdrant / PostgreSQL (Hosting)
- **Local/self-hosted**: all three run as Docker Compose services (as above), free.
- **Free-tier managed options**: Render/Railway offer free/low-cost managed Postgres and Redis; Qdrant Cloud has a free tier; if avoiding any managed service entirely, self-host all three in Docker Compose on a single free-tier VM instance.

## Monitoring
- Structured JSON logs from FastAPI (per `09_DEVELOPMENT_RULES.md`) — free-tier log viewing via Render/Railway's built-in dashboards is sufficient for a portfolio project; no paid APM required.
- A simple `/health` endpoint checked by an uptime monitor (e.g., a free UptimeRobot check) is enough production-signal for this project's scale.

## CI/CD — GitHub Actions
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: ruff check backend/
      - run: pytest backend/tests/
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t novaagent-backend ./backend
      - run: docker build -t novaagent-frontend ./frontend
```
- Deploy step (Render/Railway) triggers automatically on merge to `main` via their GitHub integration — no separate deploy job needed in most cases.

## Backups
- PostgreSQL: scheduled `pg_dump` (weekly is sufficient for a portfolio project) stored in MinIO or a free storage tier — not required for MVP demo purposes, but documented as a production-readiness gap to be aware of.
- Qdrant: collection snapshots (Qdrant's built-in snapshot API) if RAG data needs to survive a redeploy.

## Scaling (documented for maturity, not required at MVP scale)
- FastAPI backend is stateless — horizontal scaling is just running more container instances behind the load balancer.
- Redis/Postgres/Qdrant would move to managed, properly-sized services before any real user scale — free-tier self-hosted versions are explicitly a portfolio-stage choice, not a production-scale one, and this document should say so honestly if presented to a technical reviewer.

## Production Checklist
- [ ] All services (Postgres, Redis, Qdrant, MinIO, backend, frontend) run via `docker compose up` with zero manual steps
- [ ] `.env.example` matches every variable actually used in the deployed config
- [ ] HTTPS active on the deployed URL
- [ ] CI pipeline green on `main`
- [ ] `/health` endpoint responding correctly
- [ ] A real end-to-end user journey (per `14_TESTING_QA.md`'s Acceptance Testing) walked through on the live deployed URL, not just locally
- [ ] README updated with the live demo link and setup instructions
