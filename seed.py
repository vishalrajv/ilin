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


if __name__ == "__main__":
    seed()
