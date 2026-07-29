"""
app/api/deps.py

Reusable FastAPI dependency functions.

Provides:
  - Database session injection
  - UserRepository injection
  - AuthService injection
  - Bearer token extraction and validation (current user ID)
"""
import uuid
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import AsyncSessionLocal
from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# OAuth2-compatible Bearer scheme — populates Swagger "Authorize" button
bearer_scheme = HTTPBearer(auto_error=True)


# ─────────────────────────────────────────────
# Database Session
# ─────────────────────────────────────────────

async def get_db():
    """Yield an async SQLAlchemy session, closing it after the request."""
    async with AsyncSessionLocal() as session:
        yield session


# ─────────────────────────────────────────────
# Repository
# ─────────────────────────────────────────────

async def get_user_repository(
    db=Depends(get_db),
) -> UserRepository:
    """Construct a UserRepository bound to the current request's DB session."""
    return UserRepository(db)


# ─────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────

async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Construct an AuthService with the injected UserRepository."""
    return AuthService(repo)


# ─────────────────────────────────────────────
# Current User
# ─────────────────────────────────────────────

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> uuid.UUID:
    """
    Extract and validate the Bearer access token from the Authorization header.

    Returns:
        The authenticated user's UUID extracted from the token 'sub' claim.

    Raises:
        HTTP 401 if the token is missing, invalid, expired, or has the wrong type.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject: str | None = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing the 'sub' claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return uuid.UUID(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is not a valid UUID.",
            headers={"WWW-Authenticate": "Bearer"},
        )
