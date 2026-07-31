# 07_DATABASE_DESIGN.md — NovaAgent PostgreSQL Design

## ER Diagram

```
users (1) ──── (many) conversations
conversations (1) ──── (many) messages
messages (1) ──── (0..1) artifacts
users (1) ──── (many) documents
documents (1) ──── (many) document_chunks
users (1) ──── (many) credit_transactions
users (1) ──── (many) generated_files
```

## Tables

### users
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default gen_random_uuid() |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| google_id | VARCHAR(255) | UNIQUE, NULLABLE |
| credits_balance | INTEGER | NOT NULL, DEFAULT 240 |
| plan | VARCHAR(50) | NOT NULL, DEFAULT 'starter' |
| timezone | VARCHAR(100) | DEFAULT 'UTC' |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |

### conversations
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| agent_type | VARCHAR(50) | NOT NULL (chat/code/search/pdf/image/rag) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |

### messages
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| conversation_id | UUID | FK → conversations.id, NOT NULL |
| role | VARCHAR(20) | NOT NULL ('user' / 'assistant') |
| content | TEXT | NOT NULL |
| agent_type | VARCHAR(50) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |

### artifacts
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| message_id | UUID | FK → messages.id, NOT NULL |
| type | VARCHAR(50) | NOT NULL ('code', etc.) |
| content | TEXT | NOT NULL |
| language | VARCHAR(50) | NULLABLE |

### documents
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| file_name | VARCHAR(255) | NOT NULL |
| file_path | VARCHAR(500) | NOT NULL (MinIO/local path) |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'processing' ('processing'/'processed'/'failed') |
| page_count | INTEGER | NULLABLE |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |

### document_chunks
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| document_id | UUID | FK → documents.id, NOT NULL |
| chunk_index | INTEGER | NOT NULL |
| text | TEXT | NOT NULL |
| qdrant_vector_id | VARCHAR(100) | NOT NULL, UNIQUE (pointer into Qdrant, vector itself lives there) |

### generated_files
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| message_id | UUID | FK → messages.id, NULLABLE |
| type | VARCHAR(20) | NOT NULL ('pdf'/'ppt'/'image') |
| file_url | VARCHAR(500) | NOT NULL |
| file_size_bytes | BIGINT | NOT NULL |
| credits_used | INTEGER | NOT NULL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |

### credit_transactions
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| amount | INTEGER | NOT NULL (negative = deduction, positive = purchase/bonus) |
| agent_type | VARCHAR(50) | NULLABLE (null for purchases) |
| balance_after | INTEGER | NOT NULL |
| description | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |

## Indexes
- `users(email)` — unique index (login lookup)
- `conversations(user_id, created_at DESC)` — sidebar conversation list query
- `messages(conversation_id, created_at ASC)` — thread ordering
- `document_chunks(document_id)` — chunk retrieval by document
- `credit_transactions(user_id, created_at DESC)` — billing history query
- `generated_files(user_id, type, created_at DESC)` — per-type file listing (PDF/PPT/Image pages)

## Relationships
- `users` 1→N `conversations`, `documents`, `credit_transactions`, `generated_files`
- `conversations` 1→N `messages`
- `messages` 1→(0..1) `artifacts`
- `documents` 1→N `document_chunks`

## Constraints
- `ON DELETE CASCADE` from `users` → all owned rows (account deletion cleans up fully).
- `credits_balance` on `users` has a CHECK constraint `>= 0` — enforced at the DB level as a backstop in addition to the application-level deduction guard.
- `status` on `documents` restricted via CHECK to the 3 enumerated values.

## SQLAlchemy Models (structure reference — implemented in Phase per `11_DEVELOPMENT_PHASES.md`)
```python
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    credits_balance = Column(Integer, nullable=False, default=240)
    plan = Column(String(50), nullable=False, default="starter")
    timezone = Column(String(100), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    conversations = relationship("Conversation", backref="user", cascade="all, delete")
    documents = relationship("Document", backref="user", cascade="all, delete")
    credit_transactions = relationship("CreditTransaction", backref="user", cascade="all, delete")
# ... remaining models follow the table definitions above 1:1
```

## Alembic Plan
1. `alembic init alembic`
2. Migration 001: create `users`
3. Migration 002: create `conversations`, `messages`, `artifacts`
4. Migration 003: create `documents`, `document_chunks`
5. Migration 004: create `generated_files`, `credit_transactions`
6. Migration 005: add indexes (per Indexes section above)
7. Every future schema change = one new Alembic migration, never a manual `ALTER TABLE` outside the migration flow (per `09_DEVELOPMENT_RULES.md`).
