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
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_jwt(user_id=user.id, username=user.username, role=user.role)
    return TokenResponse(access_token=token, username=user.username, role=user.role)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint. Client should discard token. Server-side invalidation optional."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user info."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        created_at=str(current_user.created_at) if current_user.created_at else None,
    )
