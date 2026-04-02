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


def _get_token(client, username, password):
    """Helper to get JWT token for a user."""
    resp = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
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
    topic_resp = client.post(
        "/api/topics?name=Private+Topic",
        headers={"Authorization": f"Bearer {token}"},
    )
    topic_id = topic_resp.json()["id"]

    # Assign regular_user to topic
    client.post(
        f"/api/topics/{topic_id}/assign",
        json={"user_ids": [regular_user.id]},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Regular user should see the topic
    user_token = _get_token(client, "testuser", "user123")
    response = client.get(
        "/api/topics", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    topics = response.json()
    assert any(t["name"] == "Private Topic" for t in topics)


def test_delete_topic(client, admin_user):
    """Admin can delete topics."""
    token = _get_token(client, "admin", "admin123")
    topic_resp = client.post(
        "/api/topics?name=Delete+Me",
        headers={"Authorization": f"Bearer {token}"},
    )
    topic_id = topic_resp.json()["id"]

    response = client.delete(
        f"/api/topics/{topic_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
