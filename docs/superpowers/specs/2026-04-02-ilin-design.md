# ILIN Design Specification

**Date:** 2026-04-02
**Status:** Draft
**Author:** Vishal Raj V, Senior Engineer

## Overview

ILIN (Integrated Local Intelligence Node) is a local CPU-optimized RAG system with role-based access control. An admin creates Topics, uploads documents into them, and assigns users. Assigned users can chat with the topic's documents through a web interface with streaming responses and source citations.

## Requirements Summary

| Requirement | Detail |
|---|---|
| **Authentication** | Simple local auth (SQLite + bcrypt + JWT) |
| **Document Types** | PDF, DOCX, TXT, PPTX, XLSX, Markdown |
| **LLM Backend** | llama.cpp (GGUF) + OpenAI-compatible API support |
| **Embeddings** | sentence-transformers (local, CPU) |
| **Chat Features** | Q&A with chat history, source citations, export |
| **Topic Access** | Admin assigns specific users to specific topics |
| **Scale** | Network deployment, <10 concurrent users |
| **Frontend** | Web-based GUI with Soft UI Evolution design |
| **Architecture** | Modular Python package with FastAPI |

## Architecture

### Layer Overview

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Soft UI Evolution — HTML/CSS/JS)             │
│  ├── Admin Dashboard (Topics, Docs, Users, Assignments) │
│  ├── User Chat Interface (Topics list, Chat, History)   │
│  └── Auth Pages (Login/Logout)                          │
├─────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                    │
│  ├── Auth Router  (login, logout, me)                   │
│  ├── Admin Router (topics CRUD, docs upload, assign)    │
│  └── Chat Router  (streaming chat, history)             │
├─────────────────────────────────────────────────────────┤
│  Core Services                                          │
│  ├── RAG Engine (parse → chunk → embed → retrieve → gen)│
│  ├── LLM Backend (llama.cpp + OpenAI-compatible)        │
│  └── Auth Service (bcrypt, JWT, role checks)            │
├─────────────────────────────────────────────────────────┤
│  Storage                                                │
│  ├── SQLite (users, topics, chat history, assignments)  │
│  ├── FAISS (per-topic vector indexes)                   │
│  └── File Storage (documents, GGUF models, caches)      │
└─────────────────────────────────────────────────────────┘
```

### Project Structure

```
ilin/
├── ilin/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, middleware
│   │   ├── auth_router.py       # /api/auth/* endpoints
│   │   ├── admin_router.py      # /api/topics/*, /api/users/* endpoints
│   │   ├── chat_router.py       # /api/chat endpoints (SSE streaming)
│   │   └── dependencies.py      # Auth deps, role guards, current_user
│   ├── core/
│   │   ├── __init__.py
│   │   ├── rag_engine.py        # RAG pipeline orchestration
│   │   ├── parser.py            # Document parsing (PDF, DOCX, etc.)
│   │   ├── chunker.py           # Text chunking strategies
│   │   ├── embedder.py          # sentence-transformers wrapper
│   │   ├── retriever.py         # FAISS retrieval logic
│   │   ├── generator.py         # LLM generation (llama.cpp + OpenAI)
│   │   └── config.py            # Application configuration
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── service.py           # Password hashing, JWT creation/validation
│   │   └── models.py            # User, Role Pydantic models
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLAlchemy engine, session management
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── vector_store.py      # FAISS index management per topic
│   │   └── file_store.py        # Document file management
│   └── frontend/
│       ├── static/              # CSS, JS, fonts
│       ├── templates/           # HTML templates
│       └── assets/              # Images, icons
├── data/
│   ├── ilin.db                 # SQLite database
│   ├── documents/              # Uploaded documents
│   ├── indexes/                # FAISS indexes per topic
│   └── models/                 # GGUF model files
├── tests/
├── requirements.txt
├── pyproject.toml
└── run.py                      # Entry point
```

## Data Flow

### Document Upload & Indexing

1. **Admin uploads** document to a topic via multipart form
2. **Validation & storage** — file type validated, saved to `data/documents/`, DB record created with status="pending"
3. **Background indexing** — async task: parse → chunk → embed → FAISS index. Status transitions: "pending" → "indexing" → "ready" or "failed"
4. **Available for chat** — assigned users can query. Admin monitors progress via SSE

### Chat Query

1. **User submits question** — selects topic, types question, chat history included for context
2. **Embed & retrieve** — question embedded via sentence-transformers, FAISS retrieves top-k chunks from topic's index
3. **LLM generation** — prompt assembled with system prompt + context chunks + question, sent to llama.cpp or OpenAI-compatible endpoint
4. **Streaming response** — response streamed via SSE to frontend with source citations. Chat session saved to SQLite

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/auth/login | Public | Login, returns JWT |
| POST | /api/auth/logout | JWT | Invalidate token |
| GET | /api/auth/me | JWT | Current user info + role |
| GET | /api/topics | JWT | Topics user has access to |
| POST | /api/topics | Admin | Create new topic |
| PUT | /api/topics/:id | Admin | Update topic |
| DELETE | /api/topics/:id | Admin | Delete topic + index |
| POST | /api/topics/:id/documents | Admin | Upload document(s) |
| GET | /api/topics/:id/documents | JWT | List documents in topic |
| DELETE | /api/topics/:id/documents/:docId | Admin | Remove document |
| POST | /api/topics/:id/assign | Admin | Assign users to topic |
| POST | /api/chat | JWT | Chat query (streaming SSE) |
| GET | /api/chat/history | JWT | User's chat history |
| GET | /api/chat/history/:sessionId/export | JWT | Export chat as TXT/JSON |
| GET | /api/users | Admin | List all users |
| POST | /api/users | Admin | Create new user |

## Database Schema

### Users
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| username | VARCHAR(50) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | VARCHAR(20) | NOT NULL (admin/user) |
| created_at | DATETIME | DEFAULT NOW |

### Topics
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| name | VARCHAR(200) | NOT NULL |
| description | TEXT | NULL |
| created_by | INTEGER | FK → users.id |
| created_at | DATETIME | DEFAULT NOW |

### Documents
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| topic_id | INTEGER | FK → topics.id |
| filename | VARCHAR(500) | NOT NULL |
| file_path | VARCHAR(1000) | NOT NULL |
| file_type | VARCHAR(20) | NOT NULL |
| file_size | INTEGER | NOT NULL |
| status | VARCHAR(20) | NOT NULL (pending/indexing/ready/failed) |
| error_message | TEXT | NULL |
| uploaded_at | DATETIME | DEFAULT NOW |
| indexed_at | DATETIME | NULL |

### TopicAssignments
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| topic_id | INTEGER | FK → topics.id |
| user_id | INTEGER | FK → users.id |
| assigned_at | DATETIME | DEFAULT NOW |

### ChatSessions
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| user_id | INTEGER | FK → users.id |
| topic_id | INTEGER | FK → topics.id |
| created_at | DATETIME | DEFAULT NOW |
| updated_at | DATETIME | DEFAULT NOW |

### ChatMessages
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT |
| session_id | INTEGER | FK → chat_sessions.id |
| role | VARCHAR(10) | NOT NULL (user/assistant) |
| content | TEXT | NOT NULL |
| sources | JSON | NULL (source chunks metadata) |
| created_at | DATETIME | DEFAULT NOW |

## RAG Engine Design

### Document Parsing Pipeline

Adapted from RAG-Anything's pluggable parser pattern:

```
ParserRegistry
├── PDFParser (PyMuPDF/fitz)
├── DOCXParser (python-docx)
├── TXTParser (built-in)
├── PPTXParser (python-pptx)
└── XLSXParser (openpyxl)

Each parser returns: List[TextChunk {text, metadata, page_number}]
```

### Chunking Strategy

- **Default:** Recursive character chunking (500 tokens, 50 overlap)
- **Configurable per topic:** chunk_size, chunk_overlap
- **Metadata preserved:** source document, topic, page/row number

### Embedding Pipeline

- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (CPU-optimized, 384-dim)
- **Batch embedding:** chunks embedded in batches of 32
- **Cached:** embeddings stored alongside FAISS index

### Retrieval

- **Index:** FAISS IndexFlatIP (inner product) with L2-normalized vectors
- **Per-topic:** separate FAISS index per topic in `data/indexes/{topic_id}/`
- **Top-k:** configurable (default 5)
- **Re-ranking:** optional MMR (maximal marginal relevance) for diversity

### Generation

```
LLMBackend (abstract)
├── LlamaCppBackend (llama-cpp-python)
│   ├── GGUF model loading
│   ├── Context window management
│   └── Streaming generation
└── OpenAICompatibleBackend
    ├── Configurable base_url
    ├── API key authentication
    └── Streaming generation
```

**Prompt template:**
```
System: You are a helpful assistant. Answer the user's question based ONLY on the provided context.
If the answer cannot be found in the context, say "I don't have enough information to answer that."

Context:
[chunk 1] (source: document_name, page X)
[chunk 2] (source: document_name, page Y)
...

Question: {user_question}
Answer:
```

## Authentication & Authorization

- **Password hashing:** bcrypt with salt rounds=12
- **JWT:** HS256 algorithm, 24-hour expiry, secret from config/env
- **Role-based access:**
  - `admin` — full access to all endpoints
  - `user` — can only access assigned topics, chat, and own history
- **Middleware:** FastAPI dependency that validates JWT and checks role per endpoint

## Error Handling

| Scenario | Response |
|---|---|
| Invalid credentials | 401 Unauthorized |
| Expired/invalid token | 401 Unauthorized |
| Insufficient permissions | 403 Forbidden |
| Topic not found | 404 Not Found |
| Document upload fails | 422 Unprocessable Entity |
| Indexing fails | Document status → "failed", error logged |
| LLM unavailable | 503 Service Unavailable, user-friendly message |
| Concurrent indexing | Queue documents, process sequentially per topic |

## Frontend Design (Soft UI Evolution)

### Design Principles
- Soft, rounded corners (12-16px)
- Subtle shadows for depth
- Muted color palette with accent colors
- Smooth transitions and hover states
- Clean typography hierarchy

### Pages

**Login Page**
- Centered card with username/password fields
- Soft gradient background
- ILIN branding

**Admin Dashboard**
- Sidebar navigation (Topics, Users, Settings)
- Topic cards with document count, user count, indexing status
- Upload modal with drag-and-drop
- User assignment panel with checkboxes

**User Chat Interface**
- Left sidebar: available topics list
- Main area: chat window with streaming responses
- Message bubbles with soft shadows
- Source citations as expandable accordions below responses
- Chat history accessible via sidebar

## Configuration

```python
# config.py
class Settings:
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Auth
    jwt_secret: str = env("ILIN_JWT_SECRET")
    jwt_expiry_hours: int = 24
    
    # LLM
    llm_backend: str = "llamacpp"  # or "openai"
    llm_model_path: str = "data/models/model.gguf"
    llm_openai_base_url: str = ""
    llm_openai_api_key: str = ""
    llm_openai_model: str = ""
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.7
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    
    # Retrieval
    retrieval_top_k: int = 5
    retrieval_use_mmr: bool = False
    
    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Storage
    data_dir: Path = Path("data")
    db_url: str = "sqlite:///data/ilin.db"
```

## Dependencies

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9
PyJWT>=2.8.0
bcrypt>=4.1.0
sqlalchemy>=2.0.0
faiss-cpu>=1.8.0
sentence-transformers>=2.7.0
llama-cpp-python>=0.2.50
openai>=1.12.0
PyMuPDF>=1.24.0
python-docx>=1.1.0
python-pptx>=0.6.23
openpyxl>=3.1.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
```

## RAG-Anything Reuse Assessment

RAG-Anything (HKUDS) provides a well-structured multimodal RAG framework. For ILIN's CPU-only text-focused use case:

**Reusable patterns:**
- Pluggable parser architecture — adapt for our document types
- Processor mixin pattern — clean pipeline separation
- Context extractor — useful for chunk context management
- Config system — dataclass with env var support
- Batch processing pattern — async concurrency for indexing

**Not reused:**
- LightRAG dependency (too heavy for CPU-only)
- Multimodal processors (images, tables, equations) — out of scope
- VLM integration — not needed for text-only RAG
- Knowledge graph features — overkill for this use case

## Success Criteria

1. Admin can create topics, upload documents, assign users
2. Documents are indexed asynchronously with status tracking
3. Assigned users can chat with topics and get accurate answers
4. Responses stream in real-time with source citations
5. Chat history is persisted and retrievable
6. System runs on CPU with acceptable response times (<10s for typical queries)
7. Supports <10 concurrent users on a single machine
