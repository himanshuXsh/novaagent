# 08_API_SPECIFICATION.md — NovaAgent API Specification

Base URL: `/api/v1`. All protected routes require `Authorization: Bearer <jwt>`.

## Authentication

### `POST /auth/google`
Request:
```json
{ "id_token": "google-issued-id-token" }
```
Response `200`:
```json
{ "jwt": "...", "user": { "id": "uuid", "email": "...", "name": "...", "credits_balance": 240 } }
```
Errors: `401` invalid token.

### `GET /auth/me`
Response `200`: current user object (same shape as above).
Errors: `401` missing/expired session.

---

## Chat

### `POST /chat/message`
Request:
```json
{ "conversation_id": "uuid|null", "content": "string", "agent_type": "chat" }
```
Response: `text/event-stream` (SSE) — streamed tokens, final event includes `message_id`, `conversation_id`.
Errors: `402` insufficient credits, `429` rate limited.

### `GET /chat/conversations`
Response `200`: `[{ "id", "title", "agent_type", "created_at" }]`

---

## Coding

### `POST /agents/code`
Request: `{ "conversation_id": "uuid|null", "prompt": "string" }`
Response `200`:
```json
{ "artifact_id": "uuid", "language": "python", "code": "..." , "message_id": "uuid" }
```

---

## Search

### `POST /agents/search`
Request: `{ "query": "string" }`
Response `200`:
```json
{
  "answer": "AI-generated summary with [1] citations",
  "sources": [{ "title": "...", "url": "...", "snippet": "..." }],
  "images": [{ "url": "...", "thumbnail_url": "..." }]
}
```

---

## PDF / PPT

### `POST /agents/pdf`
Request: `{ "prompt": "string" }`
Response `200`: `{ "file_id": "uuid", "file_url": "...", "file_name": "...", "size_bytes": 123456 }`

### `POST /agents/ppt`
Same shape as `/agents/pdf`, `file_name` ends `.pptx`, response includes `slide_count`.

### `GET /agents/files?type=pdf|ppt`
Response `200`: list of previously generated files for the user (for the PDF/PPT page's card grid).

### `DELETE /agents/files/{file_id}`
Response `204`.

---

## Image (stretch)

### `POST /agents/image`
Request: `{ "prompt": "string" }`
Response `200`: `{ "file_id": "uuid", "image_url": "..." }`
Errors: `501` if the Image Agent isn't wired to a backend yet (frontend shows placeholder state per `03_UI_UX_DESIGN_SYSTEM.md`).

---

## RAG

### `POST /rag/upload`
Multipart form: `file`.
Response `200`: `{ "document_id": "uuid", "status": "processing" }`

### `GET /rag/documents/{document_id}`
Response `200`: `{ "document_id", "status", "page_count", "chunk_count" }`

### `POST /rag/query`
Request: `{ "document_id": "uuid", "question": "string" }`
Response `200`:
```json
{
  "answer": "grounded answer or 'not found in document'",
  "sources": [{ "chunk_index": 3, "page": 12, "excerpt": "..." }]
}
```

---

## Billing

### `GET /credits/balance`
Response `200`: `{ "balance": 240, "plan": "pro" }`

### `POST /credits/deduct` (internal — called by agent middleware, not the frontend directly)
Request: `{ "agent_type": "chat", "amount": 1 }`
Response `200`: `{ "new_balance": 239 }`
Errors: `402` insufficient balance (call blocked before reaching the agent).

### `POST /billing/purchase` (MVP: mocked)
Request: `{ "plan_id": "pro" }`
Response `200`: `{ "new_balance": ..., "transaction_id": "uuid" }`

### `GET /billing/transactions`
Response `200`: paginated list of `credit_transactions` rows.

---

## Settings

### `PATCH /users/me`
Request: `{ "name": "...", "bio": "...", "timezone": "..." }`
Response `200`: updated user object.

---

## Standard Status Codes (all endpoints)

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Resource created |
| 204 | Success, no content (deletes) |
| 400 | Malformed request |
| 401 | Not authenticated / expired session |
| 402 | Insufficient credits |
| 403 | Authenticated but not authorized for this resource |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Unhandled server error |
| 501 | Feature not implemented yet (e.g., Image Agent backend pending) |

## Error Response Shape (all endpoints)
```json
{ "error": { "code": "insufficient_credits", "message": "Human-readable explanation" } }
```
