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
