# 05_INFORMATION_ARCHITECTURE.md — NovaAgent Information Architecture

## Navigation (Sidebar — persistent across all authenticated pages)
1. Dashboard
2. Chat Agent
3. Coding Agent
4. Search Agent
5. PDF / PPT Agent
6. Image Agent
7. RAG Assistant
8. Billing
9. Settings

## Routes / Pages

| Route | Page | Auth Required |
|---|---|---|
| `/login` | Login | No |
| `/dashboard` | Dashboard / Home | Yes |
| `/chat` | Chat Agent | Yes |
| `/coding` | Coding Agent | Yes |
| `/search` | Search Agent | Yes |
| `/documents` | PDF/PPT Agent | Yes |
| `/image` | Image Agent | Yes |
| `/rag` | RAG Assistant | Yes |
| `/billing` | Billing & Credits | Yes |
| `/settings` | Settings (tabbed: Profile, API Keys, Notifications, Billing, Security) | Yes |

(In Streamlit's multipage model, each route maps to a file under `frontend/pages/`.)

## Authentication Flow
```
Land on /login
  → Click "Continue with Google" → Google OAuth consent
     → Backend verifies token, creates/finds user, issues JWT
        → Session stored in Redis (TTL-based)
           → Redirect to /dashboard
  (or) Email/password path → same JWT issuance → /dashboard

Every subsequent page load: AuthGuard checks JWT/session validity
  → valid: render page
  → invalid/expired: redirect to /login
```

## Agent Flow (general pattern, applies to Chat/Coding/Search/PDF/Image/RAG)
```
User on /dashboard clicks an Agent Card (or picks from sidebar)
  → navigates to that agent's page
     → user submits a prompt (+ optional file upload for RAG/PDF/Image)
        → credits check (see Billing Flow) → if insufficient, block + show upsell
        → request sent to backend → LangGraph router → specialist agent node
           → response streamed back → rendered in the agent's page-specific UI
              (chat bubble / artifact panel / result cards / file card / citation chips)
        → credits deducted on success → conversation/message persisted
           → dashboard's "Recent Activity" and metrics update on next load
```

## Billing Flow
```
User views /billing → sees current balance + usage bar + plan cards + transactions
  → "Buy Credits" or "Choose a Plan" → (MVP: simulated purchase, adds to mocked
     ledger; stretch: real Razorpay Test Mode checkout)
        → balance updates → transaction row appended → confirmation shown
  → If balance hits 0 during agent use: non-blocking banner shown site-wide,
     linking back to /billing (does not hard-block navigation, per Design.md)
```

## Settings Flow
```
User on /settings → left tab nav switches the right-side form panel:
  Profile → avatar, name, email, bio, timezone → Save Changes → persisted via API
  API Keys → (future: user-provided keys for BYO-model support) → view/regenerate
  Notifications → toggle preferences → persisted
  Billing → shortcut view into /billing's plan/transaction data
  Security → password change, session management, (future: 2FA)
```

## Dashboard Flow
```
User lands on /dashboard after login
  → fetch: credits balance, message count, files count, conversation count
  → fetch: usage-over-time series (for the line chart)
  → fetch: agent-usage distribution (for the donut chart)
  → fetch: recent activity feed (last N actions across all agents)
  → fetch: storage overview (documents/images/ppts/other, size used vs. quota)
  → render metric cards, agent grid, charts, activity feed, storage panel
  → clicking any Agent Card navigates to that agent's route
```

## Site Map (visual)

```
Login
  │
  ▼
Dashboard ──┬── Chat Agent
            ├── Coding Agent
            ├── Search Agent
            ├── PDF/PPT Agent
            ├── Image Agent
            ├── RAG Assistant
            ├── Billing ── (Plans, Transactions)
            └── Settings ── (Profile, API Keys, Notifications, Billing, Security)
```
