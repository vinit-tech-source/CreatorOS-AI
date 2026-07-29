"""
app/services/auth_service.py

Authentication business logic for CreatorOS AI.

Responsibilities:
  - User registration
  - Credential verification (login)
  - Token refresh
  - Current-user resolution

Does NOT handle:
  - FastAPI request/response
  - Database session management (injected via repository)
  - OAuth / social login
"""
import logging
import uuid

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AccessTokenResponse, AuthResponse, TokenPair
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    """
    Handles all authentication-related business logic.

    Depends on UserRepository for data access.
    Raises application-level exceptions; the API layer maps these to HTTP responses.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self._repo = user_repository

    # ─────────────────────────────────────────────
    # Registration
    # ─────────────────────────────────────────────

    async def register_user(self, data: UserCreate) -> UserResponse:
        """
        Register a new user account.

        Steps:
          1. Ensure the email is not already registered.
          2. Ensure the username is not already taken.
          3. Hash the plain-text password.
          4. Persist the user via the repository.
          5. Return the sanitised user response (no password hash).

        Args:
            data: Validated UserCreate schema containing email, username,
                  plain-text password, full_name, and role.

        Returns:
            UserResponse for the newly created user.

        Raises:
            EmailAlreadyExistsError:    If the email is already registered.
            UsernameAlreadyExistsError: If the username is already taken.
        """
        # 1 — Email uniqueness check
        existing_by_email = await self._repo.get_by_email(data.email)
        if existing_by_email is not None:
            logger.warning(f"Registration failed — email already in use: {data.email}")
            raise EmailAlreadyExistsError()

        # 2 — Username uniqueness check
        existing_by_username = await self._repo.get_by_username(data.username)
        if existing_by_username is not None:
            logger.warning(f"Registration failed — username taken: {data.username}")
            raise UsernameAlreadyExistsError()

        # 3 — Hash password
        password_hash = hash_password(data.password)

        # 4 — Persist
        user: User = await self._repo.create(data, password_hash)

        logger.info(f"New user registered: id={user.id} email={user.email}")

        # 5 — Return safe response (password_hash excluded by schema)
        return UserResponse.model_validate(user)

    # ─────────────────────────────────────────────
    # Login
    # ─────────────────────────────────────────────

    async def authenticate_user(
        self, email: str, password: str
    ) -> AuthResponse:
        """
        Authenticate a user with email and password.

        Steps:
          1. Look up the user by email.
          2. Verify the plain-text password against the stored hash.
          3. Confirm the account is active.
          4. Issue an access token and a refresh token.
          5. Return both tokens alongside the user profile.

        Args:
            email:    The user's email address.
            password: The plain-text password.

        Returns:
            AuthResponse containing the user profile and token pair.

        Raises:
            InvalidCredentialsError: If no user matches the email or the password
                                     is incorrect.
            InactiveUserError:       If the account has been deactivated.
        """
        # 1 — Lookup
        user = await self._repo.get_by_email(email)
        if user is None:
            logger.warning(f"Login failed — email not found: {email}")
            raise InvalidCredentialsError()

        # 2 — Password verification
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed — wrong password for: {email}")
            raise InvalidCredentialsError()

        # 3 — Active check
        if not user.is_active:
            logger.warning(f"Login blocked — inactive account: id={user.id}")
            raise InactiveUserError()

        # 4 — Issue tokens
        subject = str(user.id)
        access_token = create_access_token(subject)
        refresh_token = create_refresh_token(subject)

        logger.info(f"User authenticated: id={user.id} email={user.email}")

        # 5 — Compose response
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
        )

    # ─────────────────────────────────────────────
    # Token Refresh
    # ─────────────────────────────────────────────

    async def refresh_access_token(self, refresh_token: str) -> AccessTokenResponse:
        """
        Exchange a valid refresh token for a new access token.

        Steps:
          1. Decode and validate the refresh token (signature, expiry, type).
          2. Load the corresponding user from the repository.
          3. Verify the account is still active.
          4. Issue and return a new access token.

        Args:
            refresh_token: The JWT refresh token string.

        Returns:
            AccessTokenResponse with the newly issued access token.

        Raises:
            InvalidTokenError:  If the refresh token is invalid or expired.
            UserNotFoundError:  If the user referenced by the token no longer exists.
            InactiveUserError:  If the user account has been deactivated.
        """
        # 1 — Decode refresh token
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError as exc:
            raise InvalidTokenError(str(exc)) from exc

        subject: str | None = payload.get("sub")
        if not subject:
            raise InvalidTokenError("Token is missing the 'sub' claim.")

        # 2 — Load user
        try:
            user_id = uuid.UUID(subject)
        except ValueError as exc:
            raise InvalidTokenError("Token subject is not a valid UUID.") from exc

        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User referenced by token no longer exists.")

        # 3 — Active check
        if not user.is_active:
            raise InactiveUserError()

        # 4 — New access token
        new_access_token = create_access_token(str(user.id))

        logger.info(f"Access token refreshed for user: id={user.id}")

        return AccessTokenResponse(access_token=new_access_token)

    # ─────────────────────────────────────────────
    # Current User Resolution
    # ─────────────────────────────────────────────

    async def get_current_user(self, user_id: uuid.UUID) -> UserResponse:
        """
        Retrieve and return the currently authenticated user.

        This method accepts an already-validated user ID (extracted from a decoded
        access token by the API dependency layer) and fetches the full user record.

        Args:
            user_id: The UUID of the authenticated user.

        Returns:
            UserResponse for the authenticated user.

        Raises:
            UserNotFoundError: If no user exists with the given ID.
            InactiveUserError: If the account has been deactivated.
        """
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if not user.is_active:
            raise InactiveUserError()

        return UserResponse.model_validate(user)
