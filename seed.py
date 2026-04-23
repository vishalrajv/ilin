"""Seed script - creates initial admin user and data directories."""

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

    # RAG Document Ingestion Loop
    from ilin.core.rag_engine import RAGEngine
    source_docs = settings.data_dir / "source_docs"
    if source_docs.exists():
        print("Starting RAG document ingestion...")
        engine = RAGEngine()
        topic_id = 1
        for file_path in source_docs.rglob("*"):
            if file_path.is_file():
                try:
                    metadatas, embeddings = engine.index_document(file_path)
                    if embeddings is not None and len(embeddings) > 0:
                        engine.add_to_topic_index(topic_id, metadatas, embeddings)
                        print(f"Successfully indexed {file_path.name}")
                except Exception as e:
                    print(f"Error indexing {file_path.name}: {e}")
    else:
        print("No source_docs directory found. Skipping ingestion.")


if __name__ == "__main__":
    seed()
