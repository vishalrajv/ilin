"""Pytest fixtures for API and database testing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ilin.storage.database import Base, get_db
from ilin.storage.models import User
from ilin.auth.service import hash_password


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
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
    from fastapi import FastAPI

    from ilin.api.admin_router import router as admin_router
    from ilin.api.auth_router import router as auth_router

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(admin_router)

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
