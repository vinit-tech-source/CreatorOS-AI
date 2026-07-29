"""
app/core/security.py

JWT token creation/decoding and Argon2 password hashing utilities.
No business logic, no database access, no FastAPI dependencies.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Password Hashing (Argon2)
# ─────────────────────────────────────────────

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using Argon2id.

    Args:
        password: The plain-text password to hash.

    Returns:
        The Argon2 hashed password string.
    """
    return _ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against an Argon2 hash.

    Args:
        password:        The plain-text password to verify.
        hashed_password: The stored Argon2 hash.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return _ph.verify(hashed_password, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


# ─────────────────────────────────────────────
# JWT Token Creation
# ─────────────────────────────────────────────

def _build_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """
    Internal helper: build and sign a JWT with standard claims.

    Args:
        subject:       The subject of the token (usually the user's UUID as a string).
        token_type:    Either "access" or "refresh".
        expires_delta: How long until the token expires.

    Returns:
        A signed JWT string.
    """
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: The subject (user UUID string).

    Returns:
        Signed JWT access token string.
    """
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _build_token(subject, token_type="access", expires_delta=expires)


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Args:
        subject: The subject (user UUID string).

    Returns:
        Signed JWT refresh token string.
    """
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _build_token(subject, token_type="refresh", expires_delta=expires)


# ─────────────────────────────────────────────
# JWT Token Decoding
# ─────────────────────────────────────────────

def _decode_token(token: str, expected_type: str) -> dict[str, Any]:
    """
    Internal helper: decode and validate a JWT, enforcing the expected token type.

    Args:
        token:         The JWT string to decode.
        expected_type: The expected "type" claim value ("access" or "refresh").

    Returns:
        The decoded token payload as a dictionary.

    Raises:
        ValueError: If the token is invalid, expired, or the type does not match.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        logger.warning(f"JWT decode failed: {exc}")
        raise ValueError("Invalid or expired token.") from exc

    if payload.get("type") != expected_type:
        raise ValueError(
            f"Token type mismatch: expected '{expected_type}', "
            f"got '{payload.get('type')}'."
        )

    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT access token string.

    Returns:
        The decoded payload dictionary (includes "sub", "iat", "exp", "type").

    Raises:
        ValueError: If the token is invalid, expired, or not an access token.
    """
    return _decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT refresh token.

    Args:
        token: The JWT refresh token string.

    Returns:
        The decoded payload dictionary (includes "sub", "iat", "exp", "type").

    Raises:
        ValueError: If the token is invalid, expired, or not a refresh token.
    """
    return _decode_token(token, expected_type="refresh")
