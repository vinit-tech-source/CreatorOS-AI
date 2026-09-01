"""
app/api/dev_auth.py

Development-only authentication bypass endpoint.

IMPORTANT SAFETY NOTES:
  - This module is only registered on the FastAPI application when
    settings.DEV_AUTH_BYPASS is True AND settings.ENVIRONMENT != "production".
  - config.py raises RuntimeError at startup if both conditions are violated.
  - This file must NEVER be imported unconditionally in main.py.
  - Do not call this endpoint from production code paths.

Endpoint:
  GET /api/v1/auth/dev-token
    → Upserts a deterministic development identity in the database.
    → Returns a real signed JWT access token for that identity.
    → The token is valid against all normal backend authorization checks.
    → Workspace ownership, service-layer authz, and all permission rules
      still apply — only the interactive login step is skipped.
"""
import logging
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token, hash_password
from app.models.user import User, UserRole
from app.schemas.response import ApiResponse
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Development"])

# ─────────────────────────────────────────────
# Deterministic dev identity constants
# These values are fixed and well-known — no secrets involved.
# ─────────────────────────────────────────────

_DEV_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_DEV_EMAIL = "dev@localhost"
_DEV_USERNAME = "devuser"
_DEV_FULL_NAME = "Development User"
_DEV_ROLE = UserRole.ADMIN
# Deterministic placeholder hash — the dev user never logs in with a password.
# This is a pre-computed Argon2 hash of the string "dev-password-placeholder".
# It is never used for real authentication.
_DEV_PASSWORD_HASH = hash_password("dev-password-placeholder")


async def _get_db():
    """Yield an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


async def _upsert_dev_user(session: AsyncSession) -> User:
    """
    Return the deterministic dev user, creating it if it does not exist.

    The dev user has a fixed UUID so workspace/resource ownership is stable
    across restarts.  If the user already exists (e.g. from a previous dev
    session) the existing record is returned unchanged.
    """
    result = await session.execute(
        select(User).where(User.id == _DEV_USER_ID)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    # Also check for email collision (e.g. someone registered dev@localhost)
    result = await session.execute(
        select(User).where(User.email == _DEV_EMAIL)
    )
    by_email = result.scalar_one_or_none()
    if by_email is not None:
        logger.warning(
            "dev@localhost email already exists with a different ID — "
            "returning that user instead of creating a new one."
        )
        return by_email

    dev_user = User(
        id=_DEV_USER_ID,
        email=_DEV_EMAIL,
        username=_DEV_USERNAME,
        password_hash=_DEV_PASSWORD_HASH,
        full_name=_DEV_FULL_NAME,
        role=_DEV_ROLE,
        is_active=True,
        is_verified=True,
    )
    session.add(dev_user)
    await session.commit()
    await session.refresh(dev_user)
    logger.info(
        f"Development user created: id={dev_user.id} email={dev_user.email}"
    )
    return dev_user


# ─────────────────────────────────────────────
# GET /auth/dev-token
# ─────────────────────────────────────────────

class _DevTokenResponse(ApiResponse):
    pass


@router.get(
    "/dev-token",
    status_code=status.HTTP_200_OK,
    summary="[DEV ONLY] Get a JWT for the development identity",
    description=(
        "**Development use only.** "
        "Returns a signed JWT access token for the deterministic `dev@localhost` "
        "identity. Only available when `DEV_AUTH_BYPASS=true` in `.env`. "
        "This endpoint is never registered when `ENVIRONMENT=production`."
    ),
    include_in_schema=settings.DEV_AUTH_BYPASS,
)
async def get_dev_token(session: AsyncSession = Depends(_get_db)):
    """
    Upsert the dev user and return a real signed JWT.

    The returned token is identical in structure to a normal login token and
    satisfies all downstream Bearer-token authentication checks.
    """
    logger.warning(
        "⚠ DEV AUTH BYPASS: issuing development token for dev@localhost"
    )
    dev_user = await _upsert_dev_user(session)
    access_token = create_access_token(str(dev_user.id))

    return ApiResponse.ok(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(dev_user.id),
                "email": dev_user.email,
                "username": dev_user.username,
                "full_name": dev_user.full_name,
                "role": dev_user.role.value,
                "is_active": dev_user.is_active,
                "is_verified": dev_user.is_verified,
                "region": dev_user.region,
                "country": dev_user.country,
                "created_at": dev_user.created_at.isoformat() if dev_user.created_at else None,
                "updated_at": dev_user.updated_at.isoformat() if dev_user.updated_at else None,
            },
        },
        message="Development token issued.",
    )
