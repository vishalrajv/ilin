"""Admin API endpoints: topics CRUD, documents, users, assignments."""

# Developer: Vishal Raj V, Senior Engineer

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ilin.api.dependencies import get_current_user, get_db, require_admin
from ilin.auth.models import UserCreate, UserResponse
from ilin.auth.service import hash_password
from ilin.config import settings
from ilin.storage.file_store import (
    ALLOWED_EXTENSIONS,
    delete_file,
    delete_topic_files,
    save_upload_file,
)
from ilin.storage.models import Document, Topic, TopicAssignment, User
from ilin.storage.vector_store import VectorStore


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

    VectorStore(topic_id).delete()
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

    try:
        file_path = save_upload_file(file, topic_id, doc.id)
        doc.file_path = str(file_path)
        doc.file_size = file_path.stat().st_size
        doc.status = "indexing"
        db.commit()

        from ilin.core.rag_engine import RAGEngine

        engine = RAGEngine()
        metadatas, embeddings = engine.index_document(file_path)
        engine.add_to_topic_index(topic_id, metadatas, embeddings)

        doc.status = "ready"
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
    doc = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.topic_id == topic_id)
        .first()
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_file(Path(doc.file_path))

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}


# --- User Assignment ---


@router.post("/topics/{topic_id}/assign")
def assign_users(
    topic_id: int,
    user_ids: list[int] = Body(..., embed=True),
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
            .filter(
                TopicAssignment.topic_id == topic_id,
                TopicAssignment.user_id == uid,
            )
            .first()
        )
        if existing is None:
            assignment = TopicAssignment(topic_id=topic_id, user_id=uid)
            db.add(assignment)
            assigned.append(uid)

    db.commit()
    return {
        "message": f"Assigned {len(assigned)} users to topic",
        "assigned_user_ids": assigned,
    }
