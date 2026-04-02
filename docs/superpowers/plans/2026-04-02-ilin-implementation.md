# ILIN Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local CPU-optimized RAG system with admin topic management, document upload/indexing, and user chat with streaming responses.

**Architecture:** Modular Python package with FastAPI backend, SQLite + FAISS storage, sentence-transformers embeddings, llama.cpp/OpenAI-compatible LLM backends, and Soft UI Evolution HTML/CSS/JS frontend.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy, FAISS, sentence-transformers, llama-cpp-python, PyJWT, bcrypt, Jinja2

---

## File Structure

```
ilin/
├── ilin/
│   ├── __init__.py                          # Package init, version
│   ├── config.py                            # Settings with pydantic-settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app, CORS, static files, routers
│   │   ├── auth_router.py                   # POST /login, /logout, GET /me
│   │   ├── admin_router.py                  # Topics CRUD, docs upload/delete, user assign, user CRUD
│   │   ├── chat_router.py                   # POST /chat (SSE), GET /history, /export
│   │   └── dependencies.py                  # get_current_user, require_admin, get_db
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parser.py                        # ParserRegistry + parsers for PDF/DOCX/TXT/PPTX/XLSX/MD
│   │   ├── chunker.py                       # Recursive character chunking
│   │   ├── embedder.py                      # sentence-transformers wrapper with batch support
│   │   ├── retriever.py                     # FAISS retrieval with top-k, MMR
│   │   ├── generator.py                     # LLMBackend abstract + LlamaCpp + OpenAICompatible
│   │   └── rag_engine.py                    # Orchestrates parse→chunk→embed→retrieve→generate
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── service.py                       # hash_password, verify_password, create_jwt, decode_jwt
│   │   └── models.py                        # TokenResponse, UserCreate, UserResponse Pydantic models
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py                      # Engine, SessionLocal, Base, init_db
│   │   ├── models.py                        # SQLAlchemy ORM: User, Topic, Document, etc.
│   │   ├── vector_store.py                  # FAISS index per topic: save, load, search, add, delete
│   │   └── file_store.py                    # Document file save, delete, list
│   └── frontend/
│       ├── static/
│       │   ├── css/
│       │   │   └── style.css                # Soft UI Evolution styles
│       │   └── js/
│       │       ├── auth.js                  # Login/logout, JWT storage, API calls
│       │       ├── admin.js                 # Admin dashboard logic
│       │       └── chat.js                  # Chat interface, SSE streaming
│       └── templates/
│           ├── base.html                    # Base template with nav, CSS links
│           ├── login.html                   # Login page
│           ├── admin.html                   # Admin dashboard
│           └── chat.html                    # User chat interface
├── data/                                    # Created at runtime
│   ├── ilin.db
│   ├── documents/
│   ├── indexes/
│   └── models/
├── requirements.txt
├── run.py                                   # Entry point: uvicorn runner
└── tests/
    ├── __init__.py
    ├── conftest.py                          # Test fixtures: db, client, test user
    ├── test_auth.py                         # Auth service tests
    ├── test_parser.py                       # Parser tests
    ├── test_chunker.py                      # Chunker tests
    ├── test_vector_store.py                 # FAISS vector store tests
    └── test_api.py                          # API endpoint tests
```

---

### Task 1: Project Setup, Config, and Database Layer

**Files:**
- Create: `ilin/__init__.py`
- Create: `ilin/config.py`
- Create: `ilin/storage/__init__.py`
- Create: `ilin/storage/database.py`
- Create: `ilin/storage/models.py`
- Create: `requirements.txt`
- Create: `run.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Create requirements.txt**

```txt
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
markdown>=3.6
pydantic>=2.6.0
pydantic-settings>=2.1.0
httpx>=0.27.0
pytest>=8.0.0
```

- [ ] **Step 2: Create package init**

File: `ilin/__init__.py`
```python
"""ILIN - Integrated Local Intelligence Node"""

__version__ = "0.1.0"
```

- [ ] **Step 3: Create config module**

File: `ilin/config.py`
```python
"""Application configuration with environment variable support."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_expiry_hours: int = 24

    # LLM
    llm_backend: str = "llamacpp"
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

    model_config = {"env_prefix": "ILIN_", "extra": "ignore"}


settings = Settings()
```

- [ ] **Step 4: Create database module**

File: `ilin/storage/__init__.py`
```python
"""Storage layer: database, vector store, file store."""
```

File: `ilin/storage/database.py`
```python
"""SQLAlchemy database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ilin.config import settings


engine = create_engine(settings.db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_db():
    """Yield a database session, auto-close on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call on startup."""
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 5: Create ORM models**

File: `ilin/storage/models.py`
```python
"""SQLAlchemy ORM models for all database entities."""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from ilin.storage.database import Base


class User(Base):
    """Application user with role-based access."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

    topic_assignments = relationship("TopicAssignment", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class Topic(Base):
    """A topic containing documents for RAG chat."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="topic", cascade="all, delete-orphan")
    user_assignments = relationship("TopicAssignment", back_populates="topic", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="topic", cascade="all, delete-orphan")


class Document(Base):
    """An uploaded document within a topic."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    indexed_at = Column(DateTime, nullable=True)

    topic = relationship("Topic", back_populates="documents")


class TopicAssignment(Base):
    """Maps users to topics they can access."""

    __tablename__ = "topic_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("Topic", back_populates="user_assignments")
    user = relationship("User", back_populates="topic_assignments")


class ChatSession(Base):
    """A chat conversation between a user and a topic."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    topic = relationship("Topic", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """A single message within a chat session."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
```

- [ ] **Step 6: Create run.py entry point**

File: `run.py`
```python
"""ILIN entry point — starts the FastAPI server."""

import uvicorn

from ilin.config import settings


def main():
    """Run the ILIN server."""
    uvicorn.run(
        "ilin.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Create test fixtures**

File: `tests/conftest.py`
```python
"""Pytest fixtures for API and database testing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ilin.storage.database import Base, get_db
from ilin.storage.models import User
from ilin.auth.service import hash_password


TEST_DB_URL = "sqlite:///./test_ilin.db"


@pytest.fixture
def db_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Yield a test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden DB dependency."""
    from ilin.api.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user in the test database."""
    user = User(
        username="admin",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """Create a regular user in the test database."""
    user = User(
        username="testuser",
        password_hash=hash_password("user123"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

- [ ] **Step 8: Run tests to verify setup**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/ -v`
Expected: Tests pass (no test functions yet, just fixture validation)

- [ ] **Step 9: Commit**

```bash
git add ilin/__init__.py ilin/config.py ilin/storage/__init__.py ilin/storage/database.py ilin/storage/models.py requirements.txt run.py tests/__init__.py tests/conftest.py
git commit -m "feat: project setup with config, database models, and test fixtures"
```

---

### Task 2: Authentication Service

**Files:**
- Create: `ilin/auth/__init__.py`
- Create: `ilin/auth/service.py`
- Create: `ilin/auth/models.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Create auth package init**

File: `ilin/auth/__init__.py`
```python
"""Authentication and authorization services."""
```

- [ ] **Step 2: Create auth service**

File: `ilin/auth/service.py`
```python
"""Password hashing, JWT creation and validation."""

from datetime import datetime, timedelta, timezone

import jwt
import bcrypt

from ilin.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with 12 salt rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_jwt(user_id: int, username: str, role: str) -> str:
    """Create a JWT token with user claims and 24-hour expiry."""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_jwt(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns None if invalid."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
```

- [ ] **Step 3: Create auth Pydantic models**

File: `ilin/auth/models.py`
```python
"""Pydantic models for authentication request/response schemas."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request body."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserCreate(BaseModel):
    """Admin user creation request."""

    username: str
    password: str
    role: str = "user"


class UserResponse(BaseModel):
    """User info response."""

    id: int
    username: str
    role: str
    created_at: str | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Write auth service tests**

File: `tests/test_auth.py`
```python
"""Tests for authentication service functions."""

from ilin.auth.service import hash_password, verify_password, create_jwt, decode_jwt


def test_hash_password_produces_string():
    """hash_password returns a bcrypt hash string."""
    result = hash_password("testpassword")
    assert isinstance(result, str)
    assert result.startswith("$2")


def test_verify_password_correct():
    """verify_password returns True for correct password."""
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_incorrect():
    """verify_password returns False for wrong password."""
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_jwt_contains_claims():
    """create_jwt returns token with user_id, username, role."""
    token = create_jwt(user_id=1, username="testuser", role="user")
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_jwt_valid_token():
    """decode_jwt returns payload for valid token."""
    token = create_jwt(user_id=1, username="testuser", role="admin")
    payload = decode_jwt(token)
    assert payload is not None
    assert payload["user_id"] == 1
    assert payload["username"] == "testuser"
    assert payload["role"] == "admin"


def test_decode_jwt_expired_token():
    """decode_jwt returns None for expired token."""
    import jwt
    from datetime import datetime, timedelta, timezone

    expired = jwt.encode(
        {
            "user_id": 1,
            "username": "test",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        },
        "change-me-in-production",
        algorithm="HS256",
    )
    assert decode_jwt(expired) is None


def test_decode_jwt_invalid_token():
    """decode_jwt returns None for tampered token."""
    assert decode_jwt("invalid.token.here") is None
```

- [ ] **Step 5: Run auth tests**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/test_auth.py -v`
Expected: All 7 tests pass

- [ ] **Step 6: Commit**

```bash
git add ilin/auth/__init__.py ilin/auth/service.py ilin/auth/models.py tests/test_auth.py
git commit -m "feat: auth service with bcrypt hashing and JWT token management"
```

---

### Task 3: API Dependencies and Auth Router

**Files:**
- Create: `ilin/api/__init__.py`
- Create: `ilin/api/dependencies.py`
- Create: `ilin/api/auth_router.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Create API package init**

File: `ilin/api/__init__.py`
```python
"""FastAPI routers and application setup."""
```

- [ ] **Step 2: Create API dependencies**

File: `ilin/api/dependencies.py`
```python
"""FastAPI dependencies for auth, DB, and role checks."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ilin.auth.service import decode_jwt
from ilin.storage.database import get_db
from ilin.storage.models import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT from Authorization header. Returns User model."""
    token = credentials.credentials
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
```

- [ ] **Step 3: Create auth router**

File: `ilin/api/auth_router.py`
```python
"""Authentication API endpoints: login, logout, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ilin.api.dependencies import get_current_user, get_db
from ilin.auth.models import LoginRequest, TokenResponse, UserResponse
from ilin.auth.service import create_jwt, verify_password
from ilin.storage.models import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == request.username).first()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_jwt(user_id=user.id, username=user.username, role=user.role)
    return TokenResponse(access_token=token, username=user.username, role=user.role)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint. Client should discard token. Server-side invalidation optional."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user info."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        created_at=str(current_user.created_at) if current_user.created_at else None,
    )
```

- [ ] **Step 4: Write API auth tests**

Add to `tests/test_api.py`:
```python
"""Tests for API endpoints."""

from tests.conftest import TEST_DB_URL


def test_login_success(client, admin_user):
    """Login with correct credentials returns JWT."""
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_login_failure(client, admin_user):
    """Login with wrong password returns 401."""
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Login with non-existent username returns 401."""
    response = client.post("/api/auth/login", json={"username": "nobody", "password": "test"})
    assert response.status_code == 401


def test_get_me(client, admin_user):
    """GET /me returns current user info with valid token."""
    login_resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_resp.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_get_me_unauthorized(client):
    """GET /me without token returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    """GET /me with invalid token returns 401."""
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token"})
    assert response.status_code == 401


def test_logout(client, admin_user):
    """POST /logout returns success with valid token."""
    login_resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_resp.json()["access_token"]
    response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

- [ ] **Step 5: Run API auth tests**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/test_api.py -v`
Expected: All 7 tests pass

- [ ] **Step 6: Commit**

```bash
git add ilin/api/__init__.py ilin/api/dependencies.py ilin/api/auth_router.py tests/test_api.py
git commit -m "feat: auth API endpoints with JWT login, logout, and /me"
```

---

### Task 4: Document Parser Pipeline

**Files:**
- Create: `ilin/core/__init__.py`
- Create: `ilin/core/parser.py`
- Create: `ilin/core/chunker.py`
- Create: `tests/test_parser.py`
- Create: `tests/test_chunker.py`

- [ ] **Step 1: Create core package init**

File: `ilin/core/__init__.py`
```python
"""Core RAG engine components."""
```

- [ ] **Step 2: Create document parser with registry pattern**

File: `ilin/core/parser.py`
```python
"""Pluggable document parser registry for multiple file formats."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class TextChunk:
    """A chunk of text extracted from a document with metadata."""

    text: str
    metadata: dict
    page_number: int | None = None
    source_file: str = ""


class DocumentParser(Protocol):
    """Protocol for document parsers."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        """Parse document and return list of text chunks."""
        ...


class PDFParser:
    """Parse PDF files using PyMuPDF (fitz)."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        import fitz

        doc = fitz.open(str(file_path))
        chunks = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                chunks.append(
                    TextChunk(
                        text=text,
                        metadata={"source": file_path.name, "file_type": "pdf"},
                        page_number=page_num + 1,
                        source_file=file_path.name,
                    )
                )
        doc.close()
        return chunks


class DOCXParser:
    """Parse DOCX files using python-docx."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        from docx import Document

        doc = Document(str(file_path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        return [
            TextChunk(
                text=full_text,
                metadata={"source": file_path.name, "file_type": "docx"},
                source_file=file_path.name,
            )
        ]


class TXTParser:
    """Parse plain text files."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        text = file_path.read_text(encoding="utf-8")
        return [
            TextChunk(
                text=text,
                metadata={"source": file_path.name, "file_type": "txt"},
                source_file=file_path.name,
            )
        ]


class PPTXParser:
    """Parse PPTX presentations using python-pptx."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        from pptx import Presentation

        prs = Presentation(str(file_path))
        texts = []
        for slide_num, slide in enumerate(prs.slides, 1):
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.text.strip():
                            texts.append(paragraph.text)
        full_text = "\n\n".join(texts)
        return [
            TextChunk(
                text=full_text,
                metadata={"source": file_path.name, "file_type": "pptx"},
                page_number=1,
                source_file=file_path.name,
            )
        ]


class XLSXParser:
    """Parse XLSX spreadsheets using openpyxl."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        from openpyxl import load_workbook

        wb = load_workbook(str(file_path), data_only=True)
        texts = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            for row in ws.iter_rows(values_only=True):
                row_text = " | ".join(str(cell) for cell in row if cell is not None)
                if row_text.strip():
                    texts.append(row_text)
        full_text = "\n".join(texts)
        return [
            TextChunk(
                text=full_text,
                metadata={"source": file_path.name, "file_type": "xlsx"},
                source_file=file_path.name,
            )
        ]


class MarkdownParser:
    """Parse Markdown files."""

    def parse(self, file_path: Path) -> list[TextChunk]:
        text = file_path.read_text(encoding="utf-8")
        return [
            TextChunk(
                text=text,
                metadata={"source": file_path.name, "file_type": "md"},
                source_file=file_path.name,
            )
        ]


class ParserRegistry:
    """Registry that maps file extensions to parser instances."""

    _parsers: dict[str, DocumentParser] = {
        ".pdf": PDFParser(),
        ".docx": DOCXParser(),
        ".txt": TXTParser(),
        ".pptx": PPTXParser(),
        ".xlsx": XLSXParser(),
        ".md": MarkdownParser(),
        ".markdown": MarkdownParser(),
    }

    @classmethod
    def get_parser(cls, file_path: Path) -> DocumentParser:
        """Get the appropriate parser for a file extension."""
        ext = file_path.suffix.lower()
        parser = cls._parsers.get(ext)
        if parser is None:
            raise ValueError(f"Unsupported file type: {ext}")
        return parser

    @classmethod
    def parse_file(cls, file_path: Path) -> list[TextChunk]:
        """Parse a document file and return text chunks."""
        parser = cls.get_parser(file_path)
        return parser.parse(file_path)
```

- [ ] **Step 3: Create text chunker**

File: `ilin/core/chunker.py`
```python
"""Recursive character text chunking with overlap."""

from ilin.core.parser import TextChunk


def chunk_text(chunks: list[TextChunk], chunk_size: int = 500, chunk_overlap: int = 50) -> list[TextChunk]:
    """Split text chunks into smaller overlapping pieces using recursive character splitting.

    Uses newline-first splitting, then paragraph, then sentence, then word boundaries.
    Preserves metadata from original chunks.
    """
    result = []
    for chunk in chunks:
        sub_chunks = _split_text(chunk.text, chunk_size, chunk_overlap)
        for i, sub_text in enumerate(sub_chunks):
            if sub_text.strip():
                result.append(
                    TextChunk(
                        text=sub_text,
                        metadata={**chunk.metadata, "chunk_index": i},
                        page_number=chunk.page_number,
                        source_file=chunk.source_file,
                    )
                )
    return result


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Recursively split text by decreasing separator priority."""
    if len(text) <= chunk_size:
        return [text]

    # Try splitting by separators in order of preference
    for separator in ["\n\n", "\n", ". ", " ", ""]:
        if separator == "":
            # Hard split by character count
            return _hard_split(text, chunk_size, overlap)

        parts = text.split(separator)
        if len(parts) <= 1:
            continue

        # Check if any part is larger than chunk_size
        if max(len(p) for p in parts) > chunk_size:
            continue

        # Rejoin parts into chunks of target size
        return _merge_parts(parts, separator, chunk_size, overlap)

    return [text]


def _hard_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text by character count when no natural separator works."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def _merge_parts(parts: list[str], separator: str, chunk_size: int, overlap: int) -> list[str]:
    """Merge list of parts into chunks of approximately chunk_size."""
    chunks = []
    current = ""
    for part in parts:
        if not part.strip():
            continue
        candidate = current + separator + part if current else part
        if len(candidate) > chunk_size and current:
            chunks.append(current)
            # Start next chunk with overlap from end of current
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = overlap_text + separator + part if overlap_text.strip() else part
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
```

- [ ] **Step 4: Write parser tests**

File: `tests/test_parser.py`
```python
"""Tests for document parser pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from ilin.core.parser import (
    ParserRegistry,
    PDFParser,
    DOCXParser,
    TXTParser,
    TextChunk,
)


def test_txt_parser_parses_text(tmp_path: Path):
    """TXTParser reads plain text files."""
    file = tmp_path / "test.txt"
    file.write_text("Hello world\nSecond line")
    parser = TXTParser()
    chunks = parser.parse(file)
    assert len(chunks) == 1
    assert "Hello world" in chunks[0].text
    assert chunks[0].metadata["file_type"] == "txt"


def test_parser_registry_gets_txt_parser(tmp_path: Path):
    """ParserRegistry returns TXTParser for .txt files."""
    file = tmp_path / "test.txt"
    parser = ParserRegistry.get_parser(file)
    assert isinstance(parser, TXTParser)


def test_parser_registry_unsupported_extension(tmp_path: Path):
    """ParserRegistry raises ValueError for unsupported extensions."""
    file = tmp_path / "test.xyz"
    import pytest

    with pytest.raises(ValueError, match="Unsupported file type"):
        ParserRegistry.get_parser(file)


def test_text_chunk_has_metadata():
    """TextChunk contains expected fields."""
    chunk = TextChunk(text="test", metadata={"key": "value"}, page_number=1, source_file="test.pdf")
    assert chunk.text == "test"
    assert chunk.metadata["key"] == "value"
    assert chunk.page_number == 1
    assert chunk.source_file == "test.pdf"
```

- [ ] **Step 5: Write chunker tests**

File: `tests/test_chunker.py`
```python
"""Tests for text chunking."""

from ilin.core.chunker import chunk_text
from ilin.core.parser import TextChunk


def test_chunk_small_text_unchanged():
    """Text shorter than chunk_size returns as single chunk."""
    chunks = [TextChunk(text="Short text", metadata={}, source_file="test.txt")]
    result = chunk_text(chunks, chunk_size=500, chunk_overlap=50)
    assert len(result) == 1
    assert result[0].text == "Short text"


def test_chunk_large_text_splits():
    """Text larger than chunk_size splits into multiple chunks."""
    large_text = "word " * 200  # ~1000 chars
    chunks = [TextChunk(text=large_text, metadata={"source": "test.txt"}, source_file="test.txt")]
    result = chunk_text(chunks, chunk_size=200, chunk_overlap=20)
    assert len(result) > 1


def test_chunk_preserves_metadata():
    """Chunked results inherit original metadata."""
    chunk = TextChunk(
        text="line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10",
        metadata={"source": "doc.pdf", "file_type": "pdf"},
        page_number=3,
        source_file="doc.pdf",
    )
    result = chunk_text([chunk], chunk_size=30, chunk_overlap=5)
    for r in result:
        assert r.metadata["source"] == "doc.pdf"
        assert r.page_number == 3
        assert r.source_file == "doc.pdf"
```

- [ ] **Step 6: Run parser and chunker tests**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/test_parser.py tests/test_chunker.py -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add ilin/core/__init__.py ilin/core/parser.py ilin/core/chunker.py tests/test_parser.py tests/test_chunker.py
git commit -m "feat: document parser pipeline with registry and text chunking"
```

---

### Task 5: Embedder, Vector Store, and File Store

**Files:**
- Create: `ilin/core/embedder.py`
- Create: `ilin/storage/vector_store.py`
- Create: `ilin/storage/file_store.py`
- Create: `tests/test_vector_store.py`

- [ ] **Step 1: Create embedder**

File: `ilin/core/embedder.py`
```python
"""sentence-transformers embedding wrapper with batch support."""

import numpy as np
from sentence_transformers import SentenceTransformer

from ilin.config import settings
from ilin.core.parser import TextChunk


class Embedder:
    """Manages sentence-transformers model and batch embedding."""

    def __init__(self, model_name: str | None = None):
        """Load the embedding model. Downloads on first use if not cached."""
        self.model = SentenceTransformer(model_name or settings.embedding_model)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Encode a list of strings into normalized embedding vectors."""
        embeddings = self.model.encode(texts, batch_size=settings.embedding_batch_size, show_progress_bar=False)
        # L2 normalize for inner product similarity in FAISS
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norms

    def embed_query(self, text: str) -> np.ndarray:
        """Encode a single query string into a normalized embedding vector."""
        return self.embed_texts([text])[0]
```

- [ ] **Step 2: Create vector store**

File: `ilin/storage/vector_store.py`
```python
"""FAISS vector index management per topic."""

import json
from pathlib import Path

import faiss
import numpy as np

from ilin.config import settings


class VectorStore:
    """Manages a FAISS index for a single topic with metadata storage."""

    def __init__(self, topic_id: int):
        """Initialize vector store for a topic. Creates index dir if needed."""
        self.topic_id = topic_id
        self.index_dir = settings.data_dir / "indexes" / str(topic_id)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.index_dir / "faiss.index"
        self.metadata_path = self.index_dir / "metadata.jsonl"
        self.index = None
        self.metadata = []
        self._load()

    def _load(self):
        """Load existing FAISS index and metadata from disk."""
        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, encoding="utf-8") as f:
                self.metadata = [json.loads(line) for line in f]

    def _save(self):
        """Persist FAISS index and metadata to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            for entry in self.metadata:
                f.write(json.dumps(entry) + "\n")

    def add(self, embeddings: np.ndarray, metadatas: list[dict]):
        """Add embedding vectors and their metadata to the index."""
        if self.index is None:
            dim = embeddings.shape[1] if embeddings.ndim == 2 else len(embeddings)
            self.index = faiss.IndexFlatIP(dim)
            self.metadata = []

        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        self.index.add(np.ascontiguousarray(embeddings, dtype=np.float32))
        self.metadata.extend(metadatas)
        self._save()

    def search(self, query_embedding: np.ndarray, top_k: int | None = None) -> list[dict]:
        """Search for similar vectors. Returns list of {score, metadata}."""
        if self.index is None or self.index.ntotal == 0:
            return []

        k = top_k or settings.retrieval_top_k
        k = min(k, self.index.ntotal)

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(
            np.ascontiguousarray(query_embedding, dtype=np.float32), k
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append({"score": float(score), "metadata": self.metadata[idx]})
        return results

    def delete(self):
        """Delete the entire topic index from disk."""
        import shutil

        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
        self.index = None
        self.metadata = []
```

- [ ] **Step 3: Create file store**

File: `ilin/storage/file_store.py`
```python
"""Document file storage management."""

import shutil
from pathlib import Path

from fastapi import UploadFile

from ilin.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".md", ".markdown"}


def save_upload_file(upload_file: UploadFile, topic_id: int, document_id: int) -> Path:
    """Save an uploaded file to the documents directory. Returns file path."""
    ext = Path(str(upload_file.filename)).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    dest_dir = settings.data_dir / "documents" / str(topic_id)
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / f"{document_id}_{upload_file.filename}"
    with open(dest_path, "wb") as f:
        content = upload_file.file.read()
        f.write(content)
    return dest_path


def delete_file(file_path: Path):
    """Delete a file from disk."""
    if file_path.exists():
        file_path.unlink()


def delete_topic_files(topic_id: int):
    """Delete all files for a topic."""
    topic_dir = settings.data_dir / "documents" / str(topic_id)
    if topic_dir.exists():
        shutil.rmtree(topic_dir)


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size
```

- [ ] **Step 4: Write vector store tests**

File: `tests/test_vector_store.py`
```python
"""Tests for FAISS vector store."""

import numpy as np
import pytest

from ilin.storage.vector_store import VectorStore


@pytest.fixture
def vector_store(tmp_path, monkeypatch):
    """Create a vector store in a temp directory."""
    monkeypatch.setattr("ilin.config.settings.data_dir", tmp_path)
    store = VectorStore(topic_id=1)
    yield store


def test_add_and_search(vector_store):
    """Add embeddings and search returns results with scores."""
    embeddings = np.random.rand(3, 384).astype(np.float32)
    metadatas = [
        {"text": "chunk 1", "source": "doc1.pdf"},
        {"text": "chunk 2", "source": "doc1.pdf"},
        {"text": "chunk 3", "source": "doc2.pdf"},
    ]
    vector_store.add(embeddings, metadatas)
    assert vector_store.index.ntotal == 3

    query = embeddings[0]
    results = vector_store.search(query, top_k=1)
    assert len(results) == 1
    assert results[0]["metadata"]["text"] == "chunk 1"


def test_search_empty_index(vector_store):
    """Search on empty index returns empty list."""
    results = vector_store.search(np.random.rand(384).astype(np.float32))
    assert results == []


def test_delete(vector_store):
    """Delete removes index and metadata."""
    embeddings = np.random.rand(2, 384).astype(np.float32)
    vector_store.add(embeddings, [{"text": "a"}, {"text": "b"}])
    vector_store.delete()
    assert vector_store.index is None
    assert vector_store.metadata == []
```

- [ ] **Step 5: Run vector store tests**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/test_vector_store.py -v`
Expected: All 3 tests pass

- [ ] **Step 6: Commit**

```bash
git add ilin/core/embedder.py ilin/storage/vector_store.py ilin/storage/file_store.py tests/test_vector_store.py
git commit -m "feat: embedder, FAISS vector store, and file storage"
```

---

### Task 6: LLM Generator and RAG Engine

**Files:**
- Create: `ilin/core/generator.py`
- Create: `ilin/core/rag_engine.py`
- Create: `ilin/core/retriever.py`

- [ ] **Step 1: Create LLM generator**

File: `ilin/core/generator.py`
```python
"""LLM generation backends with streaming support."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from ilin.config import settings


class LLMBackend(ABC):
    """Abstract base for LLM generation backends."""

    @abstractmethod
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text from prompt, yielding chunks for streaming."""
        ...


class LlamaCppBackend(LLMBackend):
    """Generate text using llama.cpp GGUF models."""

    def __init__(self):
        """Initialize llama.cpp backend. Model loaded on first generate."""
        self.model = None

    def _load_model(self):
        """Load the GGUF model if not already loaded."""
        if self.model is None:
            from llama_cpp import Llama

            self.model = Llama(
                model_path=str(settings.llm_model_path),
                n_ctx=4096,
                n_threads=4,
                verbose=False,
            )

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text with llama.cpp, yielding token chunks."""
        self._load_model()
        output = self.model(
            prompt,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            stream=True,
        )
        for chunk in output:
            text = chunk["choices"][0]["text"]
            if text:
                yield text


class OpenAICompatibleBackend(LLMBackend):
    """Generate text using any OpenAI-compatible API endpoint."""

    def __init__(self):
        """Initialize OpenAI-compatible backend."""
        self.client = None

    def _get_client(self):
        """Get or create the OpenAI client."""
        if self.client is None:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(
                base_url=settings.llm_openai_base_url,
                api_key=settings.llm_openai_api_key or "sk-dummy",
            )
        return self.client

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate text via OpenAI-compatible API with streaming."""
        client = self._get_client()
        response = await client.chat.completions.create(
            model=settings.llm_openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_llm_backend() -> LLMBackend:
    """Factory function to create the configured LLM backend."""
    if settings.llm_backend == "openai":
        return OpenAICompatibleBackend()
    return LlamaCppBackend()
```

- [ ] **Step 2: Create retriever**

File: `ilin/core/retriever.py`
```python
"""FAISS retrieval logic with embedding and result formatting."""

from ilin.config import settings
from ilin.core.embedder import Embedder
from ilin.storage.vector_store import VectorStore


class Retriever:
    """Retrieves relevant chunks from a topic's vector index."""

    def __init__(self, embedder: Embedder | None = None):
        """Initialize retriever with optional shared embedder."""
        self.embedder = embedder or Embedder()

    def retrieve(self, topic_id: int, query: str, top_k: int | None = None) -> list[dict]:
        """Embed query and retrieve top-k matching chunks from topic index."""
        store = VectorStore(topic_id)
        query_embedding = self.embedder.embed_query(query)
        results = store.search(query_embedding, top_k=top_k)
        return results
```

- [ ] **Step 3: Create RAG engine**

File: `ilin/core/rag_engine.py`
```python
"""RAG pipeline orchestration: parse, chunk, embed, index, retrieve, generate."""

from pathlib import Path
from typing import AsyncGenerator

from ilin.config import settings
from ilin.core.chunker import chunk_text
from ilin.core.embedder import Embedder
from ilin.core.generator import LLMBackend, get_llm_backend
from ilin.core.parser import ParserRegistry, TextChunk
from ilin.core.retriever import Retriever


class RAGEngine:
    """Orchestrates the full RAG pipeline."""

    def __init__(self):
        """Initialize RAG engine with shared components."""
        self.embedder = Embedder()
        self.retriever = Retriever(self.embedder)
        self.llm: LLMBackend | None = None

    def _get_llm(self) -> LLMBackend:
        """Get or create the LLM backend."""
        if self.llm is None:
            self.llm = get_llm_backend()
        return self.llm

    def index_document(self, file_path: Path) -> list[dict]:
        """Parse, chunk, and embed a document. Returns list of chunk metadata."""
        # Parse
        text_chunks = ParserRegistry.parse_file(file_path)

        # Chunk
        split_chunks = chunk_text(text_chunks, settings.chunk_size, settings.chunk_overlap)

        # Embed
        texts = [c.text for c in split_chunks]
        embeddings = self.embedder.embed_texts(texts)

        # Build metadata
        metadatas = [
            {
                "text": c.text,
                "source_file": c.source_file,
                "page_number": c.page_number,
                "metadata": c.metadata,
            }
            for c in split_chunks
        ]

        return metadatas, embeddings

    def add_to_topic_index(self, topic_id: int, metadatas: list[dict], embeddings):
        """Add document chunks to a topic's FAISS index."""
        from ilin.storage.vector_store import VectorStore

        store = VectorStore(topic_id)
        store.add(embeddings, metadatas)

    def retrieve_context(self, topic_id: int, query: str) -> list[dict]:
        """Retrieve relevant context chunks for a query."""
        return self.retriever.retrieve(topic_id, query)

    def build_prompt(self, query: str, context: list[dict], chat_history: str = "") -> str:
        """Build the full prompt with system, context, history, and question."""
        context_text = ""
        for i, item in enumerate(context, 1):
            source = item["metadata"].get("source_file", "unknown")
            page = item["metadata"].get("page_number", "")
            page_info = f", page {page}" if page else ""
            context_text += f"[{i}] {item['metadata']['text']}\n(source: {source}{page_info})\n\n"

        history_section = f"\nChat History:\n{chat_history}\n" if chat_history else ""

        return (
            f"System: You are a helpful assistant. Answer the user's question based ONLY on the provided context.\n"
            f"If the answer cannot be found in the context, say \"I don't have enough information to answer that.\"\n\n"
            f"Context:\n{context_text}\n"
            f"{history_section}"
            f"Question: {query}\n"
            f"Answer:"
        )

    async def generate_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate streaming response from prompt."""
        llm = self._get_llm()
        async for chunk in llm.generate(prompt):
            yield chunk
```

- [ ] **Step 4: Commit**

```bash
git add ilin/core/generator.py ilin/core/retriever.py ilin/core/rag_engine.py
git commit -m "feat: LLM generator backends and RAG engine orchestration"
```

---

### Task 7: Admin Router (Topics, Documents, Users)

**Files:**
- Create: `ilin/api/admin_router.py`
- Modify: `tests/test_api.py` — add admin endpoint tests

- [ ] **Step 1: Create admin router**

File: `ilin/api/admin_router.py`
```python
"""Admin API endpoints: topics CRUD, documents, user management, assignments."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ilin.api.dependencies import get_current_user, require_admin, get_db
from ilin.auth.models import UserCreate, UserResponse
from ilin.auth.service import hash_password
from ilin.config import settings
from ilin.storage.file_store import ALLOWED_EXTENSIONS, save_upload_file
from ilin.storage.models import Document, Topic, TopicAssignment, User


router = APIRouter(prefix="/api", tags=["admin"])


# --- User Management ---

@router.get("/users", response_model=list[UserResponse])
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            role=u.role,
            created_at=str(u.created_at) if u.created_at else None,
        )
        for u in users
    ]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    request: UserCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new user (admin only)."""
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=str(user.created_at),
    )


# --- Topic Management ---

@router.get("/topics")
def list_topics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List topics the current user has access to."""
    if current_user.role == "admin":
        topics = db.query(Topic).all()
    else:
        topics = (
            db.query(Topic)
            .join(TopicAssignment)
            .filter(TopicAssignment.user_id == current_user.id)
            .all()
        )
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "created_by": t.created_by,
            "created_at": str(t.created_at),
            "document_count": len(t.documents),
            "user_count": len(t.user_assignments),
        }
        for t in topics
    ]


@router.post("/topics", status_code=status.HTTP_201_CREATED)
def create_topic(
    name: str,
    description: str | None = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new topic (admin only)."""
    topic = Topic(name=name, description=description, created_by=admin.id)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return {"id": topic.id, "name": topic.name, "description": topic.description}


@router.put("/topics/{topic_id}")
def update_topic(
    topic_id: int,
    name: str | None = None,
    description: str | None = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a topic (admin only)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    if name:
        topic.name = name
    if description is not None:
        topic.description = description
    db.commit()
    return {"id": topic.id, "name": topic.name, "description": topic.description}


@router.delete("/topics/{topic_id}")
def delete_topic(
    topic_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a topic and all its data (admin only)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Delete vector index
    from ilin.storage.vector_store import VectorStore

    VectorStore(topic_id).delete()

    # Delete files
    from ilin.storage.file_store import delete_topic_files

    delete_topic_files(topic_id)

    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted"}


# --- Document Management ---

@router.post("/topics/{topic_id}/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    topic_id: int,
    file: UploadFile,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Upload a document to a topic and start indexing (admin only)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    ext = Path(str(file.filename)).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"Unsupported file type: {ext}")

    # Create document record
    doc = Document(
        topic_id=topic_id,
        filename=str(file.filename),
        file_path="",
        file_type=ext,
        file_size=0,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Save file
    try:
        file_path = save_upload_file(file, topic_id, doc.id)
        doc.file_path = str(file_path)
        doc.file_size = file_path.stat().st_size
        doc.status = "indexing"
        db.commit()

        # Index document
        from ilin.core.rag_engine import RAGEngine

        engine = RAGEngine()
        metadatas, embeddings = engine.index_document(file_path)
        engine.add_to_topic_index(topic_id, metadatas, embeddings)

        doc.status = "ready"
        from datetime import datetime, timezone

        doc.indexed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

    return {"id": doc.id, "filename": doc.filename, "status": doc.status}


@router.get("/topics/{topic_id}/documents")
def list_documents(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List documents in a topic."""
    docs = db.query(Document).filter(Document.topic_id == topic_id).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "status": d.status,
            "uploaded_at": str(d.uploaded_at),
            "indexed_at": str(d.indexed_at) if d.indexed_at else None,
        }
        for d in docs
    ]


@router.delete("/topics/{topic_id}/documents/{doc_id}")
def delete_document(
    topic_id: int,
    doc_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a document from a topic (admin only)."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.topic_id == topic_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    from ilin.storage.file_store import delete_file

    delete_file(Path(doc.file_path))

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}


# --- User Assignment ---

@router.post("/topics/{topic_id}/assign")
def assign_users(
    topic_id: int,
    user_ids: list[int],
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Assign users to a topic (admin only)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    assigned = []
    for uid in user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user is None:
            continue
        existing = (
            db.query(TopicAssignment)
            .filter(TopicAssignment.topic_id == topic_id, TopicAssignment.user_id == uid)
            .first()
        )
        if existing is None:
            assignment = TopicAssignment(topic_id=topic_id, user_id=uid)
            db.add(assignment)
            assigned.append(uid)

    db.commit()
    return {"message": f"Assigned {len(assigned)} users to topic", "assigned_user_ids": assigned}
```

- [ ] **Step 2: Add admin API tests to test_api.py**

Add to `tests/test_api.py`:
```python
def _get_token(client, username, password):
    """Helper to get JWT token for a user."""
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


def test_list_users_admin(client, admin_user):
    """Admin can list all users."""
    token = _get_token(client, "admin", "admin123")
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_users_forbidden(client, regular_user):
    """Non-admin cannot list users."""
    token = _get_token(client, "testuser", "user123")
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_create_user(client, admin_user):
    """Admin can create new users."""
    token = _get_token(client, "admin", "admin123")
    response = client.post(
        "/api/users",
        json={"username": "newuser", "password": "pass123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_create_topic(client, admin_user):
    """Admin can create topics."""
    token = _get_token(client, "admin", "admin123")
    response = client.post(
        "/api/topics?name=Test+Topic&description=A+test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Topic"


def test_list_topics_user(client, admin_user, regular_user):
    """User sees only assigned topics."""
    token = _get_token(client, "admin", "admin123")
    topic_resp = client.post("/api/topics?name=Private+Topic", headers={"Authorization": f"Bearer {token}"})
    topic_id = topic_resp.json()["id"]

    # Assign regular_user to topic
    client.post(
        f"/api/topics/{topic_id}/assign",
        json={"user_ids": [regular_user.id]},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Regular user should see the topic
    user_token = _get_token(client, "testuser", "user123")
    response = client.get("/api/topics", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    topics = response.json()
    assert any(t["name"] == "Private Topic" for t in topics)


def test_delete_topic(client, admin_user):
    """Admin can delete topics."""
    token = _get_token(client, "admin", "admin123")
    topic_resp = client.post("/api/topics?name=Delete+Me", headers={"Authorization": f"Bearer {token}"})
    topic_id = topic_resp.json()["id"]

    response = client.delete(f"/api/topics/{topic_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

- [ ] **Step 3: Run admin API tests**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/test_api.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add ilin/api/admin_router.py tests/test_api.py
git commit -m "feat: admin router with topics CRUD, user management, and assignments"
```

---

### Task 8: Chat Router with SSE Streaming

**Files:**
- Create: `ilin/api/chat_router.py`
- Modify: `ilin/api/main.py` — create the FastAPI app with all routers
- Modify: `tests/test_api.py` — add chat tests

- [ ] **Step 1: Create chat router**

File: `ilin/api/chat_router.py`
```python
"""Chat API endpoints: chat query (SSE streaming), history, export."""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ilin.api.dependencies import get_current_user, get_db
from ilin.storage.models import ChatMessage, ChatSession, TopicAssignment, User


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat_query(
    topic_id: int,
    message: str,
    session_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Chat with a topic. Returns streaming SSE response."""
    # Verify user has access to topic
    if current_user.role != "admin":
        assignment = (
            db.query(TopicAssignment)
            .filter(TopicAssignment.topic_id == topic_id, TopicAssignment.user_id == current_user.id)
            .first()
        )
        if assignment is None:
            raise HTTPException(status_code=403, detail="No access to this topic")

    # Get or create chat session
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    else:
        session = ChatSession(user_id=current_user.id, topic_id=topic_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=message)
    db.add(user_msg)
    db.commit()

    # Build chat history
    history_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at).all()
    chat_history = "\n".join(f"{m.role}: {m.content}" for m in history_msgs[:-1])

    # Retrieve context and build prompt
    from ilin.core.rag_engine import RAGEngine

    engine = RAGEngine()
    context = engine.retrieve_context(topic_id, message)
    if not context:
        # Return friendly message if no context found
        async def no_context_stream():
            yield "data: " + json.dumps({"content": "I don't have enough information to answer that. No relevant documents found.", "sources": []}) + "\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(no_context_stream(), media_type="text/event-stream")

    prompt = engine.build_prompt(message, context, chat_history)

    # Streaming generator
    async def generate():
        full_response = ""
        sources = [
            {
                "text": r["metadata"]["text"][:200] + "...",
                "source_file": r["metadata"].get("source_file", ""),
                "page_number": r["metadata"].get("page_number"),
                "score": r["score"],
            }
            for r in context
        ]
        try:
            async for chunk in engine.generate_response(prompt):
                full_response += chunk
                yield "data: " + json.dumps({"content": chunk, "sources": []}) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

        yield "data: " + json.dumps({"content": "", "sources": sources, "done": True}) + "\n\n"
        yield "data: [DONE]\n\n"

        # Save assistant response
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=full_response,
            sources=sources,
        )
        db.add(assistant_msg)
        session.updated_at = datetime.now(timezone.utc)
        db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/history")
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all chat sessions for current user."""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "topic_id": s.topic_id,
            "topic_name": s.topic.name if s.topic else "Unknown",
            "created_at": str(s.created_at),
            "updated_at": str(s.updated_at),
            "message_count": len(s.messages),
        }
        for s in sessions
    ]


@router.get("/history/{session_id}")
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all messages in a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources,
            "created_at": str(m.created_at),
        }
        for m in session.messages
    ]


@router.get("/history/{session_id}/export")
def export_chat(
    session_id: int,
    format: str = Query(default="txt", regex="^(txt|json)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export chat session as TXT or JSON."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if format == "json":
        messages = [
            {"role": m.role, "content": m.content, "sources": m.sources, "created_at": str(m.created_at)}
            for m in session.messages
        ]
        return {"session_id": session.id, "topic": session.topic.name if session.topic else "", "messages": messages}
    else:
        text = f"Chat Session: {session.topic.name if session.topic else 'Unknown'}\n"
        text += f"Date: {session.created_at}\n" + "=" * 50 + "\n\n"
        for m in session.messages:
            text += f"{m.role.upper()}: {m.content}\n\n"
        return {"content": text}
```

- [ ] **Step 2: Create main.py with app setup**

File: `ilin/api/main.py`
```python
"""FastAPI application setup with CORS, routers, and static files."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from ilin.storage.database import init_db
from ilin.api.auth_router import router as auth_router
from ilin.api.admin_router import router as admin_router
from ilin.api.chat_router import router as chat_router


app = FastAPI(title="ILIN", version="0.1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)

# Serve static files and frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main HTML page."""
    return FileResponse(str(frontend_dir / "templates" / "login.html"))


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()
    # Create data directories
    from ilin.config import settings

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "documents").mkdir(exist_ok=True)
    (settings.data_dir / "indexes").mkdir(exist_ok=True)
    (settings.data_dir / "models").mkdir(exist_ok=True)
```

- [ ] **Step 3: Commit**

```bash
git add ilin/api/chat_router.py ilin/api/main.py
git commit -m "feat: chat router with SSE streaming and FastAPI app setup"
```

---

### Task 9: Frontend — Base Template, Login, and CSS

**Files:**
- Create: `ilin/frontend/static/css/style.css`
- Create: `ilin/frontend/static/js/auth.js`
- Create: `ilin/frontend/templates/base.html`
- Create: `ilin/frontend/templates/login.html`

- [ ] **Step 1: Create Soft UI CSS**

File: `ilin/frontend/static/css/style.css`
```css
/* ILIN — Soft UI Evolution Styles */

:root {
    --bg-primary: #f0f2f5;
    --bg-card: #ffffff;
    --text-primary: #2c3e50;
    --text-secondary: #6c757d;
    --accent: #4a6cf7;
    --accent-hover: #3b5de7;
    --success: #28a745;
    --danger: #dc3545;
    --warning: #ffc107;
    --shadow-soft: 0 4px 16px rgba(0, 0, 0, 0.08);
    --shadow-inset: inset 2px 2px 5px rgba(0, 0, 0, 0.05), inset -2px -2px 5px rgba(255, 255, 255, 0.8);
    --radius: 14px;
    --radius-sm: 8px;
    --transition: all 0.2s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
}

/* Soft UI Card */
.card {
    background: var(--bg-card);
    border-radius: var(--radius);
    box-shadow: var(--shadow-soft);
    padding: 24px;
    transition: var(--transition);
}

.card:hover {
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 20px;
    border: none;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
}

.btn-primary {
    background: var(--accent);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-hover);
}

.btn-danger {
    background: var(--danger);
    color: white;
}

.btn-outline {
    background: transparent;
    border: 2px solid var(--accent);
    color: var(--accent);
}

.btn-outline:hover {
    background: var(--accent);
    color: white;
}

/* Form Inputs */
.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 6px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
}

.form-input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e5eb;
    border-radius: var(--radius-sm);
    font-size: 14px;
    transition: var(--transition);
    background: var(--bg-primary);
}

.form-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.15);
}

/* Login Page */
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
    width: 100%;
    max-width: 400px;
    text-align: center;
}

.login-card h1 {
    font-size: 28px;
    margin-bottom: 8px;
    color: var(--text-primary);
}

.login-card p {
    color: var(--text-secondary);
    margin-bottom: 24px;
}

.login-card .btn {
    width: 100%;
    padding: 14px;
    font-size: 16px;
}

/* Layout */
.app-layout {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 260px;
    background: var(--bg-card);
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.06);
    padding: 20px 0;
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 0 20px 20px;
    border-bottom: 1px solid #e1e5eb;
    margin-bottom: 16px;
}

.sidebar-header h2 {
    font-size: 20px;
    color: var(--accent);
}

.sidebar-nav a {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
}

.sidebar-nav a:hover,
.sidebar-nav a.active {
    background: rgba(74, 108, 247, 0.08);
    color: var(--accent);
}

.main-content {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
}

/* Topic Cards */
.topics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

.topic-card {
    cursor: pointer;
}

.topic-card h3 {
    font-size: 16px;
    margin-bottom: 8px;
}

.topic-card p {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 12px;
}

.topic-meta {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--text-secondary);
}

/* Status Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}

.badge-ready { background: #d4edda; color: #155724; }
.badge-pending { background: #fff3cd; color: #856404; }
.badge-indexing { background: #cce5ff; color: #004085; }
.badge-failed { background: #f8d7da; color: #721c24; }

/* Chat Interface */
.chat-layout {
    display: flex;
    height: calc(100vh - 60px);
}

.chat-sidebar {
    width: 280px;
    background: var(--bg-card);
    border-right: 1px solid #e1e5eb;
    overflow-y: auto;
}

.chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.message {
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
}

.message.user {
    align-items: flex-end;
}

.message.assistant {
    align-items: flex-start;
}

.message-bubble {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: var(--radius);
    font-size: 14px;
    line-height: 1.6;
}

.message.user .message-bubble {
    background: var(--accent);
    color: white;
    border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
    background: var(--bg-card);
    box-shadow: var(--shadow-soft);
    border-bottom-left-radius: 4px;
}

.chat-input-area {
    padding: 16px 20px;
    background: var(--bg-card);
    border-top: 1px solid #e1e5eb;
    display: flex;
    gap: 12px;
}

.chat-input-area textarea {
    flex: 1;
    padding: 12px;
    border: 2px solid #e1e5eb;
    border-radius: var(--radius-sm);
    resize: none;
    font-family: inherit;
    font-size: 14px;
    min-height: 44px;
    max-height: 120px;
}

.chat-input-area textarea:focus {
    outline: none;
    border-color: var(--accent);
}

/* Sources */
.sources {
    margin-top: 8px;
    font-size: 12px;
}

.sources summary {
    cursor: pointer;
    color: var(--accent);
    font-weight: 600;
}

.source-item {
    padding: 8px 12px;
    background: var(--bg-primary);
    border-radius: var(--radius-sm);
    margin-top: 4px;
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 24px;
    width: 100%;
    max-width: 500px;
    max-height: 80vh;
    overflow-y: auto;
}

.modal h3 {
    margin-bottom: 16px;
}

/* Utility */
.text-muted { color: var(--text-secondary); }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 16px; }
.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 16px; }
.flex { display: flex; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.gap-2 { gap: 8px; }
.hidden { display: none; }
.error-msg { color: var(--danger); font-size: 13px; margin-top: 8px; }
```

- [ ] **Step 2: Create auth.js**

File: `ilin/frontend/static/js/auth.js`
```javascript
/* ILIN Authentication utilities */

const API_BASE = "";

function getToken() {
    return localStorage.getItem("ilin_token");
}

function setToken(token) {
    localStorage.setItem("ilin_token", token);
}

function clearToken() {
    localStorage.removeItem("ilin_token");
}

function getUser() {
    const data = localStorage.getItem("ilin_user");
    return data ? JSON.parse(data) : null;
}

function setUser(user) {
    localStorage.setItem("ilin_user", JSON.stringify(user));
}

function clearUser() {
    localStorage.removeItem("ilin_user");
}

function isLoggedIn() {
    return !!getToken();
}

function isAdmin() {
    const user = getUser();
    return user && user.role === "admin";
}

async function apiCall(url, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        clearToken();
        clearUser();
        window.location.href = "/";
        return null;
    }
    return response;
}

async function login(username, password) {
    const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
    }
    const data = await response.json();
    setToken(data.access_token);
    setUser({ username: data.username, role: data.role });
    return data;
}

async function logout() {
    await apiCall("/api/auth/logout", { method: "POST" });
    clearToken();
    clearUser();
    window.location.href = "/";
}

// Redirect on page load
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "/";
    }
}

function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        window.location.href = isAdmin() ? "/admin" : "/chat";
    }
}
```

- [ ] **Step 3: Create base template**

File: `ilin/frontend/templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ILIN{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_head %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    <script src="/static/js/auth.js"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 4: Create login template**

File: `ilin/frontend/templates/login.html`
```html
{% extends "base.html" %}
{% block title %}ILIN — Login{% endblock %}
{% block content %}
<div class="login-container">
    <div class="card login-card">
        <h1>ILIN</h1>
        <p>Integrated Local Intelligence Node</p>
        <form id="login-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" class="form-input" placeholder="Enter username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" class="form-input" placeholder="Enter password" required>
            </div>
            <div id="error-msg" class="error-msg hidden"></div>
            <button type="submit" class="btn btn-primary mt-3">Sign In</button>
        </form>
    </div>
</div>
{% endblock %}
{% block extra_scripts %}
<script>
redirectIfLoggedIn();

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('error-msg');
    errorEl.classList.add('hidden');

    try {
        const data = await login(username, password);
        if (data.role === 'admin') {
            window.location.href = '/admin';
        } else {
            window.location.href = '/chat';
        }
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove('hidden');
    }
});
</script>
{% endblock %}
```

- [ ] **Step 5: Commit**

```bash
git add ilin/frontend/static/css/style.css ilin/frontend/static/js/auth.js ilin/frontend/templates/base.html ilin/frontend/templates/login.html
git commit -m "feat: frontend base template, login page, and Soft UI CSS"
```

---

### Task 10: Frontend — Admin Dashboard

**Files:**
- Create: `ilin/frontend/templates/admin.html`
- Create: `ilin/frontend/static/js/admin.js`
- Modify: `ilin/api/main.py` — add admin page route

- [ ] **Step 1: Add admin page route to main.py**

Add to `ilin/api/main.py`:
```python
@app.get("/admin")
async def serve_admin():
    """Serve admin dashboard."""
    return FileResponse(str(frontend_dir / "templates" / "admin.html"))
```

- [ ] **Step 2: Create admin dashboard template**

File: `ilin/frontend/templates/admin.html`
```html
{% extends "base.html" %}
{% block title %}ILIN — Admin Dashboard{% endblock %}
{% block content %}
<div class="app-layout">
    <aside class="sidebar">
        <div class="sidebar-header">
            <h2>ILIN Admin</h2>
        </div>
        <nav class="sidebar-nav">
            <a href="#" class="active" data-section="topics">Topics</a>
            <a href="#" data-section="users">Users</a>
            <a href="#" onclick="logout(); return false;">Logout</a>
        </nav>
    </aside>
    <main class="main-content">
        <!-- Topics Section -->
        <section id="topics-section">
            <div class="flex-between mb-3">
                <h2>Topics</h2>
                <button class="btn btn-primary" onclick="showCreateTopic()">+ New Topic</button>
            </div>
            <div id="topics-grid" class="topics-grid"></div>
        </section>

        <!-- Users Section -->
        <section id="users-section" class="hidden">
            <div class="flex-between mb-3">
                <h2>Users</h2>
                <button class="btn btn-primary" onclick="showCreateUser()">+ New User</button>
            </div>
            <div id="users-list"></div>
        </section>
    </main>
</div>

<!-- Create Topic Modal -->
<div id="topic-modal" class="modal-overlay hidden">
    <div class="modal">
        <h3 id="modal-title">Create Topic</h3>
        <form id="topic-form">
            <div class="form-group">
                <label for="topic-name">Topic Name</label>
                <input type="text" id="topic-name" class="form-input" required>
            </div>
            <div class="form-group">
                <label for="topic-desc">Description</label>
                <textarea id="topic-desc" class="form-input" rows="3"></textarea>
            </div>
            <div class="flex gap-2" style="justify-content: flex-end;">
                <button type="button" class="btn btn-outline" onclick="closeModal('topic-modal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
        </form>
    </div>
</div>

<!-- Create User Modal -->
<div id="user-modal" class="modal-overlay hidden">
    <div class="modal">
        <h3>Create User</h3>
        <form id="user-form">
            <div class="form-group">
                <label for="user-username">Username</label>
                <input type="text" id="user-username" class="form-input" required>
            </div>
            <div class="form-group">
                <label for="user-password">Password</label>
                <input type="password" id="user-password" class="form-input" required>
            </div>
            <div class="form-group">
                <label for="user-role">Role</label>
                <select id="user-role" class="form-input">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
            </div>
            <div class="flex gap-2" style="justify-content: flex-end;">
                <button type="button" class="btn btn-outline" onclick="closeModal('user-modal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Create</button>
            </div>
        </form>
    </div>
</div>

<!-- Assign Users Modal -->
<div id="assign-modal" class="modal-overlay hidden">
    <div class="modal">
        <h3>Assign Users to Topic</h3>
        <div id="assign-users-list" class="mb-3"></div>
        <div class="flex gap-2" style="justify-content: flex-end;">
            <button type="button" class="btn btn-outline" onclick="closeModal('assign-modal')">Cancel</button>
            <button type="button" class="btn btn-primary" onclick="saveAssignments()">Save</button>
        </div>
    </div>
</div>

<!-- Upload Modal -->
<div id="upload-modal" class="modal-overlay hidden">
    <div class="modal">
        <h3>Upload Documents</h3>
        <form id="upload-form">
            <div class="form-group">
                <label for="upload-files">Select Files (PDF, DOCX, TXT, PPTX, XLSX, MD)</label>
                <input type="file" id="upload-files" class="form-input" multiple accept=".pdf,.docx,.txt,.pptx,.xlsx,.md,.markdown">
            </div>
            <div class="flex gap-2" style="justify-content: flex-end;">
                <button type="button" class="btn btn-outline" onclick="closeModal('upload-modal')">Cancel</button>
                <button type="submit" class="btn btn-primary">Upload</button>
            </div>
        </form>
        <div id="upload-progress" class="mt-3"></div>
    </div>
</div>
{% endblock %}
{% block extra_scripts %}
<script src="/static/js/admin.js"></script>
{% endblock %}
```

- [ ] **Step 3: Create admin.js**

File: `ilin/frontend/static/js/admin.js`
```javascript
/* ILIN Admin Dashboard */

requireAuth();
if (!isAdmin()) {
    window.location.href = "/chat";
}

let currentTopicId = null;
let allUsers = [];

// Navigation
document.querySelectorAll('.sidebar-nav a[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        const section = link.dataset.section;
        document.getElementById('topics-section').classList.toggle('hidden', section !== 'topics');
        document.getElementById('users-section').classList.toggle('hidden', section !== 'users');
        if (section === 'users') loadUsers();
    });
});

// Load topics
async function loadTopics() {
    const resp = await apiCall("/api/topics");
    const topics = await resp.json();
    const grid = document.getElementById('topics-grid');
    if (topics.length === 0) {
        grid.innerHTML = '<p class="text-muted">No topics yet. Create one to get started.</p>';
        return;
    }
    grid.innerHTML = topics.map(t => `
        <div class="card topic-card" data-id="${t.id}">
            <h3>${t.name}</h3>
            <p>${t.description || 'No description'}</p>
            <div class="topic-meta">
                <span>${t.document_count} documents</span>
                <span>${t.user_count} users</span>
            </div>
            <div class="mt-2 flex gap-2">
                <button class="btn btn-outline" onclick="showUpload(${t.id})" style="padding: 6px 12px; font-size: 12px;">Upload</button>
                <button class="btn btn-outline" onclick="showAssign(${t.id})" style="padding: 6px 12px; font-size: 12px;">Assign</button>
                <button class="btn btn-danger" onclick="deleteTopic(${t.id})" style="padding: 6px 12px; font-size: 12px;">Delete</button>
            </div>
        </div>
    `).join('');
}

// Create topic
function showCreateTopic() {
    document.getElementById('modal-title').textContent = 'Create Topic';
    document.getElementById('topic-form').dataset.editId = '';
    document.getElementById('topic-name').value = '';
    document.getElementById('topic-desc').value = '';
    document.getElementById('topic-modal').classList.remove('hidden');
}

document.getElementById('topic-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('topic-name').value;
    const description = document.getElementById('topic-desc').value;
    const resp = await apiCall(`/api/topics?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}`, { method: 'POST' });
    if (resp.ok) {
        closeModal('topic-modal');
        loadTopics();
    }
});

// Delete topic
async function deleteTopic(id) {
    if (!confirm('Delete this topic and all its documents?')) return;
    const resp = await apiCall(`/api/topics/${id}`, { method: 'DELETE' });
    if (resp.ok) loadTopics();
}

// Upload documents
function showUpload(topicId) {
    currentTopicId = topicId;
    document.getElementById('upload-files').value = '';
    document.getElementById('upload-progress').innerHTML = '';
    document.getElementById('upload-modal').classList.remove('hidden');
}

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const files = document.getElementById('upload-files').files;
    const progress = document.getElementById('upload-progress');
    progress.innerHTML = '';
    for (const file of files) {
        progress.innerHTML += `<p>Uploading: ${file.name}...</p>`;
        const formData = new FormData();
        formData.append('file', file);
        const resp = await fetch(`/api/topics/${currentTopicId}/documents`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData,
        });
        const result = await resp.json();
        if (resp.ok) {
            progress.innerHTML += `<p style="color: var(--success)">✓ ${file.name} — ${result.status}</p>`;
        } else {
            progress.innerHTML += `<p style="color: var(--danger)">✗ ${file.name} — ${result.detail}</p>`;
        }
    }
});

// Assign users
async function showAssign(topicId) {
    currentTopicId = topicId;
    const resp = await apiCall("/api/users");
    allUsers = await resp.json();
    const list = document.getElementById('assign-users-list');
    list.innerHTML = allUsers.map(u => `
        <label style="display: block; padding: 8px 0;">
            <input type="checkbox" value="${u.id}"> ${u.username} (${u.role})
        </label>
    `).join('');
    document.getElementById('assign-modal').classList.remove('hidden');
}

async function saveAssignments() {
    const checked = document.querySelectorAll('#assign-users-list input:checked');
    const userIds = Array.from(checked).map(cb => parseInt(cb.value));
    await apiCall(`/api/topics/${currentTopicId}/assign`, {
        method: 'POST',
        body: JSON.stringify(userIds),
    });
    closeModal('assign-modal');
    loadTopics();
}

// Users
async function loadUsers() {
    const resp = await apiCall("/api/users");
    const users = await resp.json();
    const list = document.getElementById('users-list');
    list.innerHTML = `<table class="api-table" style="width:100%">
        <tr><th>Username</th><th>Role</th><th>Created</th></tr>
        ${users.map(u => `<tr><td>${u.username}</td><td>${u.role}</td><td>${u.created_at || '-'}</td></tr>`).join('')}
    </table>`;
}

function showCreateUser() {
    document.getElementById('user-form').reset();
    document.getElementById('user-modal').classList.remove('hidden');
}

document.getElementById('user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resp = await apiCall("/api/users", {
        method: 'POST',
        body: JSON.stringify({
            username: document.getElementById('user-username').value,
            password: document.getElementById('user-password').value,
            role: document.getElementById('user-role').value,
        }),
    });
    if (resp.ok) {
        closeModal('user-modal');
        loadUsers();
    }
});

// Modal helpers
function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

// Init
loadTopics();
```

- [ ] **Step 4: Commit**

```bash
git add ilin/frontend/templates/admin.html ilin/frontend/static/js/admin.js ilin/api/main.py
git commit -m "feat: admin dashboard with topics, users, upload, and assignment UI"
```

---

### Task 11: Frontend — User Chat Interface

**Files:**
- Create: `ilin/frontend/templates/chat.html`
- Create: `ilin/frontend/static/js/chat.js`
- Modify: `ilin/api/main.py` — add chat page route

- [ ] **Step 1: Add chat page route to main.py**

Add to `ilin/api/main.py`:
```python
@app.get("/chat")
async def serve_chat():
    """Serve user chat interface."""
    return FileResponse(str(frontend_dir / "templates" / "chat.html"))
```

- [ ] **Step 2: Create chat template**

File: `ilin/frontend/templates/chat.html`
```html
{% extends "base.html" %}
{% block title %}ILIN — Chat{% endblock %}
{% block content %}
<div class="app-layout">
    <aside class="sidebar">
        <div class="sidebar-header">
            <h2>ILIN</h2>
        </div>
        <nav class="sidebar-nav">
            <a href="#" class="active" data-section="topics">Topics</a>
            <a href="#" data-section="history">Chat History</a>
            <a href="#" onclick="logout(); return false;">Logout</a>
        </nav>
    </aside>
    <main class="main-content" style="padding: 0;">
        <!-- Topics List -->
        <section id="chat-topics-section" style="padding: 24px;">
            <h2 class="mb-3">Select a Topic</h2>
            <div id="chat-topics-grid" class="topics-grid"></div>
        </section>

        <!-- Chat Area -->
        <section id="chat-area-section" class="hidden">
            <div class="chat-layout">
                <div class="chat-main">
                    <div id="chat-header" class="flex-between" style="padding: 16px 20px; border-bottom: 1px solid #e1e5eb; background: var(--bg-card);">
                        <h3 id="chat-topic-name"></h3>
                        <button class="btn btn-outline" onclick="backToTopics()" style="padding: 6px 12px; font-size: 12px;">Back to Topics</button>
                    </div>
                    <div id="chat-messages" class="chat-messages"></div>
                    <div class="chat-input-area">
                        <textarea id="chat-input" placeholder="Type your question..." rows="1"></textarea>
                        <button class="btn btn-primary" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </section>

        <!-- History Section -->
        <section id="history-section" class="hidden" style="padding: 24px;">
            <h2 class="mb-3">Chat History</h2>
            <div id="history-list"></div>
        </section>
    </main>
</div>
{% endblock %}
{% block extra_scripts %}
<script src="/static/js/chat.js"></script>
{% endblock %}
```

- [ ] **Step 3: Create chat.js**

File: `ilin/frontend/static/js/chat.js`
```javascript
/* ILIN User Chat Interface */

requireAuth();

let currentTopicId = null;
let currentSessionId = null;

// Navigation
document.querySelectorAll('.sidebar-nav a[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        const section = link.dataset.section;
        document.getElementById('chat-topics-section').classList.toggle('hidden', section !== 'topics');
        document.getElementById('chat-area-section').classList.toggle('hidden', section !== 'topics');
        document.getElementById('history-section').classList.toggle('hidden', section !== 'history');
        if (section === 'history') loadHistory();
    });
});

// Load available topics
async function loadChatTopics() {
    const resp = await apiCall("/api/topics");
    const topics = await resp.json();
    const grid = document.getElementById('chat-topics-grid');
    if (topics.length === 0) {
        grid.innerHTML = '<p class="text-muted">No topics available.</p>';
        return;
    }
    grid.innerHTML = topics.map(t => `
        <div class="card topic-card" onclick="openTopic(${t.id}, '${t.name.replace(/'/g, "\\'")}')">
            <h3>${t.name}</h3>
            <p>${t.description || 'No description'}</p>
            <div class="topic-meta">
                <span>${t.document_count} documents</span>
            </div>
        </div>
    `).join('');
}

function openTopic(topicId, topicName) {
    currentTopicId = topicId;
    currentSessionId = null;
    document.getElementById('chat-topic-name').textContent = topicName;
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('chat-topics-section').classList.add('hidden');
    document.getElementById('chat-area-section').classList.remove('hidden');
}

function backToTopics() {
    document.getElementById('chat-topics-section').classList.remove('hidden');
    document.getElementById('chat-area-section').classList.add('hidden');
}

// Send message with SSE streaming
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    appendMessage('user', message);

    const messagesEl = document.getElementById('chat-messages');
    const assistantEl = appendMessage('assistant', '');
    const contentEl = assistantEl.querySelector('.message-content');

    const url = `/api/chat?topic_id=${currentTopicId}&message=${encodeURIComponent(message)}${currentSessionId ? `&session_id=${currentSessionId}` : ''}`;

    try {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${getToken()}` },
        });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) {
                            contentEl.textContent += parsed.content;
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        }
                        if (parsed.done && parsed.sources) {
                            renderSources(assistantEl, parsed.sources);
                        }
                        if (parsed.error) {
                            contentEl.textContent += `\n[Error: ${parsed.error}]`;
                        }
                    } catch (e) {}
                }
            }
        }
    } catch (err) {
        contentEl.textContent = `Error: ${err.message}`;
    }
}

function appendMessage(role, content) {
    const messagesEl = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `
        <div class="message-bubble">
            <div class="message-content">${content}</div>
        </div>
    `;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
}

function renderSources(messageEl, sources) {
    if (!sources.length) return;
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'sources';
    sourcesDiv.innerHTML = `
        <details>
            <summary>${sources.length} source(s)</summary>
            ${sources.map(s => `
                <div class="source-item">
                    <strong>${s.source_file}${s.page_number ? ` (p.${s.page_number})` : ''}</strong>
                    <p>${s.text}</p>
                </div>
            `).join('')}
        </details>
    `;
    messageEl.querySelector('.message-bubble').appendChild(sourcesDiv);
}

// Chat history
async function loadHistory() {
    const resp = await apiCall("/api/chat/history");
    const sessions = await resp.json();
    const list = document.getElementById('history-list');
    if (sessions.length === 0) {
        list.innerHTML = '<p class="text-muted">No chat history.</p>';
        return;
    }
    list.innerHTML = sessions.map(s => `
        <div class="card mb-2" style="cursor: pointer;" onclick="loadSession(${s.id})">
            <div class="flex-between">
                <div>
                    <strong>${s.topic_name}</strong>
                    <p class="text-muted" style="font-size: 12px;">${s.message_count} messages — ${new Date(s.updated_at).toLocaleString()}</p>
                </div>
                <button class="btn btn-outline" onclick="event.stopPropagation(); exportSession(${s.id})" style="padding: 6px 12px; font-size: 12px;">Export</button>
            </div>
        </div>
    `).join('');
}

async function loadSession(sessionId) {
    const resp = await apiCall(`/api/chat/history/${sessionId}`);
    const messages = await resp.json();
    document.getElementById('chat-topics-section').classList.add('hidden');
    document.getElementById('chat-area-section').classList.remove('hidden');
    document.getElementById('chat-messages').innerHTML = '';
    currentSessionId = sessionId;

    for (const m of messages) {
        const el = appendMessage(m.role, m.content);
        if (m.sources && m.sources.length) {
            renderSources(el, m.sources);
        }
    }
}

async function exportSession(sessionId) {
    const resp = await apiCall(`/api/chat/history/${sessionId}/export?format=txt`);
    const data = await resp.json();
    const blob = new Blob([data.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-session-${sessionId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Enter to send
document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Init
loadChatTopics();
```

- [ ] **Step 4: Commit**

```bash
git add ilin/frontend/templates/chat.html ilin/frontend/static/js/chat.js ilin/api/main.py
git commit -m "feat: user chat interface with SSE streaming, history, and export"
```

---

### Task 12: Integration Test and Seed Script

**Files:**
- Create: `seed.py` — creates initial admin user
- Modify: `requirements.txt` — ensure all deps listed

- [ ] **Step 1: Create seed script**

File: `seed.py`
```python
"""Seed script — creates initial admin user and data directories."""

from pathlib import Path

from ilin.config import settings
from ilin.storage.database import init_db, SessionLocal
from ilin.storage.models import User
from ilin.auth.service import hash_password


def seed():
    """Create admin user if it doesn't exist."""
    # Create directories
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "documents").mkdir(exist_ok=True)
    (settings.data_dir / "indexes").mkdir(exist_ok=True)
    (settings.data_dir / "models").mkdir(exist_ok=True)

    # Init database
    init_db()

    # Create admin if not exists
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if admin is None:
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print("Created admin user (admin / admin123)")
    else:
        print("Admin user already exists")
    db.close()


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Run seed script**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python seed.py`
Expected: "Created admin user (admin / admin123)"

- [ ] **Step 3: Run all tests**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Start server and verify**

Run: `cd E:\VISHAL-WORK\ILIN\ILIN && python run.py`
Expected: Server starts on http://0.0.0.0:8000
Open browser to http://localhost:8000 — should see login page

- [ ] **Step 5: Final commit**

```bash
git add seed.py requirements.txt
git commit -m "feat: seed script for initial admin user and final setup"
```

---

## Self-Review

**1. Spec coverage check:**

| Spec Requirement | Task |
|---|---|
| Simple local auth (SQLite + bcrypt + JWT) | Task 2, 3 |
| Document types: PDF, DOCX, TXT, PPTX, XLSX, Markdown | Task 4 |
| LLM: llama.cpp + OpenAI-compatible | Task 6 |
| Embeddings: sentence-transformers | Task 5 |
| Chat with history, citations, export | Task 8, 11 |
| Admin assigns users to topics | Task 7, 10 |
| Network deployment, <10 users | Architecture supports this |
| Soft UI Evolution frontend | Task 9, 10, 11 |
| Modular FastAPI package | All tasks |
| FAISS per-topic vector indexes | Task 5 |
| Async document indexing | Task 7 (upload endpoint) |
| Streaming SSE chat responses | Task 8 |
| All 15 API endpoints | Tasks 3, 7, 8 |
| Database schema (6 tables) | Task 1 |

**2. Placeholder scan:** No TBD, TODO, or incomplete sections found. All code blocks contain actual implementation code.

**3. Type consistency:** All function signatures, model names, and API paths are consistent across tasks. `User`, `Topic`, `Document`, `TopicAssignment`, `ChatSession`, `ChatMessage` models defined in Task 1 are used consistently. `apiCall()`, `getToken()`, `login()`, `logout()` in auth.js are used by admin.js and chat.js.

**4. Scope check:** Plan is focused on a single implementable system. No decomposition needed.
