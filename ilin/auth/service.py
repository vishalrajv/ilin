# Developer: Vishal Raj V, Senior Engineer

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
