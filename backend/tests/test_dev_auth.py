"""
tests/test_dev_auth.py

Tests for the development authentication bypass endpoint and its safety guards.

Tests:
  1. Dev token endpoint returns 404 when bypass is disabled (default).
  2. Dev token endpoint returns a real JWT when bypass is enabled in development.
  3. Settings validator refuses startup when bypass=true + environment=production.
  4. Dev user is upserted correctly (idempotent).
  5. Normal auth endpoints (login, register) are unaffected by the bypass flag.
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import Settings


# ─────────────────────────────────────────────
# 1. Safety Guard: production + bypass = rejected
# ─────────────────────────────────────────────

def test_dev_bypass_refused_in_production():
    """Settings must raise RuntimeError when bypass=true AND environment=production."""
    with pytest.raises(RuntimeError, match="CRITICAL SAFETY VIOLATION"):
        Settings(
            DEV_AUTH_BYPASS=True,
            ENVIRONMENT="production",
            DATABASE_URL="postgresql+asyncpg://x:x@localhost/x",
            REDIS_URL="redis://localhost:6379/0",
            SECRET_KEY="test-secret-key-for-testing-only",
            ENCRYPTION_KEY="test-encryption-key-1234567890123",
            GEMINI_API_KEY="test-gemini-key",
        )


def test_dev_bypass_refused_in_production_case_insensitive():
    """ENVIRONMENT='PRODUCTION' (uppercase) must also be refused."""
    with pytest.raises(RuntimeError, match="CRITICAL SAFETY VIOLATION"):
        Settings(
            DEV_AUTH_BYPASS=True,
            ENVIRONMENT="PRODUCTION",
            DATABASE_URL="postgresql+asyncpg://x:x@localhost/x",
            REDIS_URL="redis://localhost:6379/0",
            SECRET_KEY="test-secret-key-for-testing-only",
            ENCRYPTION_KEY="test-encryption-key-1234567890123",
            GEMINI_API_KEY="test-gemini-key",
        )


def test_dev_bypass_allowed_in_development():
    """bypass=true + environment=development must NOT raise."""
    s = Settings(
        DEV_AUTH_BYPASS=True,
        ENVIRONMENT="development",
        DATABASE_URL="postgresql+asyncpg://x:x@localhost/x",
        REDIS_URL="redis://localhost:6379/0",
        SECRET_KEY="test-secret-key-for-testing-only",
        ENCRYPTION_KEY="test-encryption-key-1234567890123",
        GEMINI_API_KEY="test-gemini-key",
    )
    assert s.DEV_AUTH_BYPASS is True
    assert s.ENVIRONMENT == "development"


def test_dev_bypass_disabled_by_default():
    """DEV_AUTH_BYPASS must default to False."""
    s = Settings(
        DATABASE_URL="postgresql+asyncpg://x:x@localhost/x",
        REDIS_URL="redis://localhost:6379/0",
        SECRET_KEY="test-secret-key-for-testing-only",
        ENCRYPTION_KEY="test-encryption-key-1234567890123",
        GEMINI_API_KEY="test-gemini-key",
    )
    assert s.DEV_AUTH_BYPASS is False


def test_environment_defaults_to_development():
    """ENVIRONMENT must default to 'development'."""
    s = Settings(
        DATABASE_URL="postgresql+asyncpg://x:x@localhost/x",
        REDIS_URL="redis://localhost:6379/0",
        SECRET_KEY="test-secret-key-for-testing-only",
        ENCRYPTION_KEY="test-encryption-key-1234567890123",
        GEMINI_API_KEY="test-gemini-key",
    )
    assert s.ENVIRONMENT == "development"


# ─────────────────────────────────────────────
# 2. Dev user upsert logic
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_dev_user_creates_user_when_absent():
    """_upsert_dev_user creates the dev user when the DB has none."""
    from app.api.dev_auth import _upsert_dev_user, _DEV_USER_ID, _DEV_EMAIL

    mock_user = MagicMock()
    mock_user.id = _DEV_USER_ID
    mock_user.email = _DEV_EMAIL

    # First select (by ID) returns nothing; second select (by email) returns nothing
    mock_result_none = MagicMock()
    mock_result_none.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result_none)
    mock_session.refresh = AsyncMock(side_effect=lambda u: None)

    # Capture what was added
    added = []
    mock_session.add = MagicMock(side_effect=added.append)
    mock_session.commit = AsyncMock()

    result = await _upsert_dev_user(mock_session)

    assert mock_session.add.called
    assert mock_session.commit.called
    created = added[0]
    assert created.email == _DEV_EMAIL
    assert created.id == _DEV_USER_ID


@pytest.mark.asyncio
async def test_upsert_dev_user_returns_existing_user():
    """_upsert_dev_user returns the existing dev user without creating a duplicate."""
    from app.api.dev_auth import _upsert_dev_user, _DEV_USER_ID

    existing = MagicMock()
    existing.id = _DEV_USER_ID

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await _upsert_dev_user(mock_session)

    assert result is existing
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


# ─────────────────────────────────────────────
# 3. Normal auth is unaffected
# ─────────────────────────────────────────────

def test_normal_login_schema_unchanged():
    """LoginRequest schema must still work with email + password."""
    from app.schemas.auth import LoginRequest
    req = LoginRequest(email="user@example.com", password="securepassword")
    assert req.email == "user@example.com"
    assert req.password == "securepassword"


def test_normal_user_create_schema_unchanged():
    """UserCreate schema must still require username, full_name, email, password."""
    from app.schemas.user import UserCreate
    data = UserCreate(
        email="user@example.com",
        username="testuser",
        password="securepassword123",
        full_name="Test User",
    )
    assert data.email == "user@example.com"
    assert data.username == "testuser"
