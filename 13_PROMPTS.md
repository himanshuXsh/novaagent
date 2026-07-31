# 13_PROMPTS.md — NovaAgent AI Build Prompts

Use with Antigravity, Claude Code, Cursor, etc. Same discipline throughout: one phase at a time, verify, update `12_MEMORY.md`, commit, stop.

## Master Prompt (paste once, first session)

```
I'm building NovaAgent, a multi-agent AI SaaS platform. Read, in order:
01_PRD.md, 02_BRAND_GUIDELINES.md, 03_UI_UX_DESIGN_SYSTEM.md,
04_LOGO_BRANDING.md, 05_INFORMATION_ARCHITECTURE.md,
06_SYSTEM_ARCHITECTURE.md, 07_DATABASE_DESIGN.md, 08_API_SPECIFICATION.md,
09_DEVELOPMENT_RULES.md, 10_PROJECT_STRUCTURE.md, 11_DEVELOPMENT_PHASES.md,
then 12_MEMORY.md for current state.

Follow 09_DEVELOPMENT_RULES.md strictly. Work ONE phase at a time from
11_DEVELOPMENT_PHASES.md: plan -> wait for my approval -> implement ->
verify (tests/screenshot as relevant) -> update 12_MEMORY.md honestly ->
commit -> stop. Never mark a phase complete with placeholder/mock code
where real logic was expected. Tell me the current phase and your plan
for the next one, then wait.
```

## Login Prompt (Phase 1)
```
Phase 1: implement Google OAuth (FastAPI + Authlib, not Firebase) per
06_SYSTEM_ARCHITECTURE.md and 08_API_SPECIFICATION.md's /auth endpoints.
Style /login per 03_UI_UX_DESIGN_SYSTEM.md and 04_LOGO_BRANDING.md (full
logo lockup, centered card). Test with a real Google login and show me
the JWT/user returned.
```

## Dashboard Prompt (Phase 2)
```
Phase 2: build the dashboard metric/chart/activity endpoints and style
/dashboard per 03_UI_UX_DESIGN_SYSTEM.md (metric row, agent grid, usage +
distribution charts via Plotly, recent activity, storage overview). Use
real data only. Screenshot and compare against the reference Dashboard.
```

## Chat Prompt (Phase 3)
```
Phase 3: implement chat_node, the router node (explicit + inferred
routing per 06_SYSTEM_ARCHITECTURE.md), conversation/message CRUD, and
style /chat per the reference (bubbles, typing indicator, prompt bar).
Test a real multi-turn conversation end-to-end.
```

## Coding Agent Prompt (Phase 4)
```
Phase 4: implement code_node and the artifact panel component
(Code/Preview tabs, syntax highlighting, copy/download) per
03_UI_UX_DESIGN_SYSTEM.md. Test with a real coding prompt and show me
the rendered artifact.
```

## Search Prompt (Phase 5)
```
Phase 5: implement search_node using duckduckgo-search (free, no API
key) and style /search per the reference (answer with citations, image +
web result cards). Test with a real query.
```

## PDF Prompt (Phase 6)
```
Phase 6: implement pdf_node (reportlab) and ppt_node (python-pptx),
file storage via MinIO or local disk, and the file-card component. Test
by generating one real PDF and one real PPT and show me the outputs.
```

## Image Prompt (Phase 7)
```
Phase 7: implement image_node using a free provider (Pollinations.ai or
HF free inference) if feasible now; otherwise build a clean, clearly-
labeled placeholder state per 03_UI_UX_DESIGN_SYSTEM.md's Empty States
spec. Tell me which path you're taking and why.
```

## RAG Prompt (Phase 8)
```
Phase 8: implement the full RAG pipeline (extraction, chunking,
embeddings, Qdrant storage) and rag_node with the mandatory
similarity-threshold "not found in document" fallback per
06_SYSTEM_ARCHITECTURE.md. Test with a real PDF: one answerable question,
one that isn't in the document, show me both responses.
```

## Billing Prompt (Phase 9)
```
Phase 9: implement the credit_transactions table, the success-only
deduction middleware, and style /billing per the reference (balance +
usage bar, plan cards with Pro highlighted, transaction table). Test:
confirm a successful agent call deducts credits and a failed one
doesn't.
```

## Settings Prompt (Phase 10)
```
Phase 10: implement PATCH /users/me and style /settings per the
reference (tab nav: Profile, API Keys, Notifications, Billing, Security).
Confirm Save Changes actually persists via a real backend call.
```

## Refactor Prompt (use anytime code quality needs improvement)
```
Review [file/module] against 09_DEVELOPMENT_RULES.md. Identify any
duplicated logic, missing type hints, inline CSS that should be in
styles/*.css, or components not being reused. Refactor without changing
behavior — show me a git diff and confirm all existing tests still pass.
```

## Testing Prompt
```
Write/complete tests for [phase/module] per 14_TESTING_QA.md's strategy
for that layer (unit/integration/API as appropriate). Run them and show
me the output. Do not mark this done until they pass.
```

## Deployment Prompt (Phase 11)
```
Phase 11: follow 15_DEPLOYMENT.md end to end — Dockerize backend and
frontend, set up GitHub Actions CI, deploy to Render/Railway free tier.
Show me the live URL and confirm the production checklist items.
```

## Bug Fix Prompt
```
This is broken: [describe symptom + paste error/screenshot]. Check
12_MEMORY.md for relevant context on what was built. Find the root
cause, fix it, and add a regression test if practical. Don't change
unrelated code.
```

## Optimization Prompt
```
[Specific page/endpoint] feels slow. Profile it, identify the actual
bottleneck (don't guess), and optimize only that — e.g., add a missing
index per 07_DATABASE_DESIGN.md, reduce an unnecessary re-fetch, or cache
a repeated query in Redis. Show me before/after timing.
```

## Status Audit Prompt (use anytime you're unsure what's actually done)
```
Give me a full status report: which phases from 11_DEVELOPMENT_PHASES.md
are actually complete (code exists, real logic, verified working) vs.
marked complete in 12_MEMORY.md but actually containing placeholder/mock
code. Check git diff --stat scope for each recent phase too. Don't fix
anything yet, just report honestly.
```

## Token-Efficiency Reminder (use each new session)
```
Fresh session. Read 12_MEMORY.md only for context — don't re-read the
other 14 docs unless this specific phase needs a detail from them. Only
work in files relevant to the current phase. Keep responses concise.
```
