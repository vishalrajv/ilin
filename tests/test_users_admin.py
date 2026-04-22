"""Tests for user management admin endpoints."""

from tests.conftest import TEST_DB_URL


def _get_token(client, username, password):
    """Helper to get JWT token for a user."""
    resp = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    return resp.json()["access_token"]


def test_delete_user_success(client, admin_user, regular_user):
    """Admin can delete a regular user."""
    token = _get_token(client, "admin", "admin123")
    response = client.delete(
        f"/api/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted"


def test_delete_user_self_protection(client, admin_user):
    """Admin cannot delete themselves."""
    token = _get_token(client, "admin", "admin123")
    response = client.delete(
        f"/api/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    # This should fail. According to the plan, we need to implement this protection.
    # Currently it might return 200 because it's not implemented.
    assert response.status_code == 400
    assert "cannot delete yourself" in response.json()["detail"].lower()


def test_delete_user_forbidden(client, regular_user, admin_user):
    """Regular user cannot delete users."""
    token = _get_token(client, "testuser", "user123")
    response = client.delete(
        f"/api/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_delete_user_cleanup_assignments(client, admin_user, regular_user, db_session):
    """Deleting a user cleans up their topic assignments."""
    from ilin.storage.models import Topic, TopicAssignment
    
    token = _get_token(client, "admin", "admin123")
    
    # Create a topic
    topic = Topic(name="Test Topic", created_by=admin_user.id)
    db_session.add(topic)
    db_session.commit()
    
    # Assign user to topic
    assignment = TopicAssignment(topic_id=topic.id, user_id=regular_user.id)
    db_session.add(assignment)
    db_session.commit()
    
    # Verify assignment exists
    assert db_session.query(TopicAssignment).filter_by(user_id=regular_user.id).count() == 1
    
    # Delete user
    response = client.delete(
        f"/api/users/{regular_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    
    # Verify assignment is gone
    assert db_session.query(TopicAssignment).filter_by(user_id=regular_user.id).count() == 0


def test_delete_user_not_found(client, admin_user):
    """Admin gets 404 for non-existent user."""
    token = _get_token(client, "admin", "admin123")
    response = client.delete(
        "/api/users/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_update_user_success(client, admin_user, regular_user):
    """Admin can update a user's username and role."""
    token = _get_token(client, "admin", "admin123")
    response = client.patch(
        f"/api/users/{regular_user.id}",
        json={"username": "updated_user", "role": "admin"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updated_user"
    assert data["role"] == "admin"


def test_update_user_password(client, admin_user, regular_user):
    """Admin can update a user's password."""
    token = _get_token(client, "admin", "admin123")
    response = client.patch(
        f"/api/users/{regular_user.id}",
        json={"password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    
    # Verify new password works
    login_resp = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "newpassword123"}
    )
    assert login_resp.status_code == 200


def test_update_user_duplicate_username(client, admin_user, regular_user):
    """Cannot update to an existing username."""
    token = _get_token(client, "admin", "admin123")
    response = client.patch(
        f"/api/users/{regular_user.id}",
        json={"username": "admin"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


def test_update_user_forbidden(client, regular_user, admin_user):
    """Regular user cannot update users."""
    token = _get_token(client, "testuser", "user123")
    response = client.patch(
        f"/api/users/{admin_user.id}",
        json={"username": "hacked_admin"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_update_user_not_found(client, admin_user):
    """Admin gets 404 for non-existent user."""
    token = _get_token(client, "admin", "admin123")
    response = client.patch(
        "/api/users/99999",
        json={"username": "nobody"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_create_user_success(client, admin_user):
    """Admin can create a new user."""
    token = _get_token(client, "admin", "admin123")
    response = client.post(
        "/api/users",
        json={"username": "new_entity", "password": "securepassword123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_entity"
    assert data["role"] == "user"


def test_create_user_duplicate(client, admin_user, regular_user):
    """Cannot create user with existing username."""
    token = _get_token(client, "admin", "admin123")
    response = client.post(
        "/api/users",
        json={"username": "testuser", "password": "password123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409
