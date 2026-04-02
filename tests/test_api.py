"""Tests for API endpoints."""

from tests.conftest import TEST_DB_URL


def test_login_success(client, admin_user):
    """Login with correct credentials returns JWT."""
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_login_failure(client, admin_user):
    """Login with wrong password returns 401."""
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Login with non-existent username returns 401."""
    response = client.post(
        "/api/auth/login", json={"username": "nobody", "password": "test"}
    )
    assert response.status_code == 401


def test_get_me(client, admin_user):
    """GET /me returns current user info with valid token."""
    login_resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
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
    response = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer invalid.token"}
    )
    assert response.status_code == 401


def test_logout(client, admin_user):
    """POST /logout returns success with valid token."""
    login_resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    token = login_resp.json()["access_token"]
    response = client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
