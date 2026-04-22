# Developer: Vishal Raj V, Senior Engineer

"""Pydantic models for authentication request/response schemas."""

from pydantic import BaseModel, Field, field_validator


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

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: str = "user"

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username is alphanumeric with underscores only and lowercase."""
        if not v.islower():
            raise ValueError('Username must be lowercase')
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate role is either 'user' or 'admin'."""
        if v not in {'user', 'admin'}:
            raise ValueError('Role must be either "user" or "admin"')
        return v


class UserResponse(BaseModel):
    """User info response."""

    id: int
    username: str
    role: str
    created_at: str | None = None

    model_config = {"from_attributes": True}
