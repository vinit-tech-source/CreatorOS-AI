"""
app/api/auth.py

Authentication API endpoints for CreatorOS AI.

Endpoints:
  POST  /api/v1/auth/register  — Create a new user account
  POST  /api/v1/auth/login     — Authenticate and receive tokens
  POST  /api/v1/auth/refresh   — Exchange a refresh token for a new access token
  GET   /api/v1/auth/me        — Return the currently authenticated user
"""
import uuid

from fastapi import APIRouter, Depends, status, Request

from app.core.rate_limit import limiter

from app.api.deps import get_auth_service, get_current_user_id
from app.schemas.auth import AccessTokenResponse, AuthResponse, LoginRequest
from app.schemas.response import ApiResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─────────────────────────────────────────────
# POST /auth/register
# ─────────────────────────────────────────────

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[UserResponse],
    summary="Register a new user",
    description=(
        "Create a new user account. "
        "Returns the created user profile (password excluded). "
        "Returns **409** if the email or username is already in use."
    ),
)
async def register(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[UserResponse]:
    user = await auth_service.register_user(data)
    return ApiResponse.ok(data=user, message="Account created successfully.")


# ─────────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────────

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[AuthResponse],
    summary="Login with email and password",
    description=(
        "Authenticate with a registered email and password. "
        "Returns an access token, a refresh token, and the user profile. "
        "Returns **401** on invalid credentials and **403** if the account is inactive."
    ),
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[AuthResponse]:
    result = await auth_service.authenticate_user(data.email, data.password)
    return ApiResponse.ok(data=result, message="Login successful.")


# ─────────────────────────────────────────────
# POST /auth/refresh
# ─────────────────────────────────────────────

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[AccessTokenResponse],
    summary="Refresh access token",
    description=(
        "Exchange a valid refresh token for a new short-lived access token. "
        "Returns **401** if the refresh token is invalid or expired."
    ),
)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[AccessTokenResponse]:
    result = await auth_service.refresh_access_token(refresh_token)
    return ApiResponse.ok(data=result, message="Access token refreshed.")


# ─────────────────────────────────────────────
# GET /auth/me
# ─────────────────────────────────────────────

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserResponse],
    summary="Get current user",
    description=(
        "Return the profile of the currently authenticated user. "
        "Requires a valid Bearer access token in the Authorization header. "
        "Returns **401** if the token is missing or invalid, "
        "**403** if the account is inactive."
    ),
)
async def get_me(
    user_id: uuid.UUID = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[UserResponse]:
    user = await auth_service.get_current_user(user_id)
    return ApiResponse.ok(data=user)


# ─────────────────────────────────────────────
# PATCH /auth/me
# ─────────────────────────────────────────────

@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserResponse],
    summary="Update current user",
    description=(
        "Update profile information and preferences for the currently authenticated user. "
        "Allows updating region, country, full_name, and username."
    ),
)
async def update_me(
    data: UserUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[UserResponse]:
    user = await auth_service.update_current_user(user_id, data)
    return ApiResponse.ok(data=user, message="Profile updated successfully.")




