"""
app/core/exceptions.py

Application-level custom exceptions.
These are raised by the service layer and caught by FastAPI exception handlers.
"""


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


# ─────────────────────────────────────────────
# Authentication Exceptions
# ─────────────────────────────────────────────

class InvalidCredentialsError(AppException):
    """Raised when email/password combination is incorrect."""

    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(message)


class InactiveUserError(AppException):
    """Raised when a user account is inactive."""

    def __init__(self, message: str = "This account has been deactivated.") -> None:
        super().__init__(message)


class InvalidTokenError(AppException):
    """Raised when a JWT token is invalid, expired, or has the wrong type."""

    def __init__(self, message: str = "Invalid or expired token.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# User / Resource Exceptions
# ─────────────────────────────────────────────

class UserNotFoundError(AppException):
    """Raised when a requested user does not exist."""

    def __init__(self, message: str = "User not found.") -> None:
        super().__init__(message)


class EmailAlreadyExistsError(AppException):
    """Raised when attempting to register with an email that is already in use."""

    def __init__(self, message: str = "An account with this email already exists.") -> None:
        super().__init__(message)


class UsernameAlreadyExistsError(AppException):
    """Raised when attempting to register with a username that is already taken."""

    def __init__(self, message: str = "This username is already taken.") -> None:
        super().__init__(message)
