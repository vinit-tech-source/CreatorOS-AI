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


# ─────────────────────────────────────────────
# Workspace Exceptions
# ─────────────────────────────────────────────

class WorkspaceNotFoundError(AppException):
    """Raised when a requested workspace does not exist."""

    def __init__(self, message: str = "Workspace not found.") -> None:
        super().__init__(message)


class SlugAlreadyExistsError(AppException):
    """Raised when attempting to create a workspace with a slug that is already taken."""

    def __init__(self, message: str = "A workspace with this slug already exists.") -> None:
        super().__init__(message)


class PermissionDeniedError(AppException):
    """Raised when a user attempts an action they are not authorised to perform."""

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# Brand Kit Exceptions
# ─────────────────────────────────────────────

class BrandKitNotFoundError(AppException):
    """Raised when a requested Brand Kit does not exist."""

    def __init__(self, message: str = "Brand Kit not found.") -> None:
        super().__init__(message)


class BrandKitAlreadyExistsError(AppException):
    """Raised when attempting to create a Brand Kit for a workspace that already has one."""

    def __init__(self, message: str = "A Brand Kit already exists for this workspace.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# Social Account Exceptions
# ─────────────────────────────────────────────

class SocialAccountNotFoundError(AppException):
    """Raised when a requested social account does not exist."""

    def __init__(self, message: str = "Social account not found.") -> None:
        super().__init__(message)


class SocialAccountAlreadyExistsError(AppException):
    """Raised when a social account with the same platform and platform_user_id already exists for the workspace."""

    def __init__(self, message: str = "A social account with this platform user ID already exists for this workspace.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# Project Exceptions
# ─────────────────────────────────────────────

class ProjectNotFoundError(AppException):
    """Raised when a requested project does not exist."""

    def __init__(self, message: str = "Project not found.") -> None:
        super().__init__(message)


class ProjectSlugAlreadyExistsError(AppException):
    """Raised when attempting to create a project with a slug that is already taken in the workspace."""

    def __init__(self, message: str = "A project with this slug already exists in this workspace.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# Post Exceptions
# ─────────────────────────────────────────────

class PostNotFoundError(AppException):
    """Raised when a requested post does not exist."""

    def __init__(self, message: str = "Post not found.") -> None:
        super().__init__(message)


class InvalidStatusTransitionError(AppException):
    """Raised when attempting an invalid status transition."""

    def __init__(self, message: str = "Invalid status transition.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# MediaAsset Exceptions
# ─────────────────────────────────────────────

class MediaAssetNotFoundError(AppException):
    """Raised when a requested media asset does not exist."""

    def __init__(self, message: str = "Media asset not found.") -> None:
        super().__init__(message)


# ─────────────────────────────────────────────
# AI Exceptions
# ─────────────────────────────────────────────

class AIProviderError(AppException):
    """Raised when the AI provider API returns an error or times out."""

    def __init__(self, message: str = "AI provider encountered an error.") -> None:
        super().__init__(message)


class AIValidationError(AppException):
    """Raised when the AI response fails structured validation."""

    def __init__(self, message: str = "AI response failed validation.") -> None:
        super().__init__(message)
