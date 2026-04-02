# Developer: Vishal Raj V, Senior Engineer

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
