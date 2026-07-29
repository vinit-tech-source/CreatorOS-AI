"""
app/schemas/auth.py

Pydantic schemas for authentication request/response payloads.
No database access. No business logic.
"""
from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


# ─────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


# ─────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────

class TokenPair(BaseModel):
    """A pair of access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Full authentication response returned after login or registration."""
    user: UserResponse
    tokens: TokenPair


class AccessTokenResponse(BaseModel):
    """Returned when a refresh token is exchanged for a new access token."""
    access_token: str
    token_type: str = "bearer"
