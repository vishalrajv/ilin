"""Authentication API endpoints: login, logout, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ilin.api.dependencies import get_current_user
from ilin.auth.models import LoginRequest, TokenResponse, UserResponse
from ilin.auth.service import create_jwt, verify_password
from ilin.storage.database import get_db
from ilin.storage.models import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == request.username).first()

    # FIXED: Separate checks - critical for SQLAlchemy objects
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not verify_password(request.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_jwt(
        user_id=int(user.id), username=str(user.username), role=str(user.role)
    )
    return TokenResponse(
        access_token=token, username=str(user.username), role=str(user.role)
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint. Client should discard token. Server-side invalidation optional."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user info."""
    return UserResponse(
        id=int(current_user.id),
        username=str(current_user.username),
        role=str(current_user.role),
        created_at=str(current_user.created_at)
        if current_user.created_at is not None
        else None,
    )
