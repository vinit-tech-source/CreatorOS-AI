"""
app/core/exception_handlers.py

Maps application-level exceptions to standardised HTTP responses.
Register these handlers on the FastAPI app instance in main.py.
"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    BrandKitAlreadyExistsError,
    BrandKitNotFoundError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    PermissionDeniedError,
    ProjectNotFoundError,
    ProjectSlugAlreadyExistsError,
    SlugAlreadyExistsError,
    SocialAccountAlreadyExistsError,
    SocialAccountNotFoundError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
    WorkspaceNotFoundError,
)

logger = logging.getLogger(__name__)


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "data": None, "message": message},
    )


async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return _error_response(401, exc.message)


async def inactive_user_handler(
    request: Request, exc: InactiveUserError
) -> JSONResponse:
    return _error_response(403, exc.message)


async def invalid_token_handler(
    request: Request, exc: InvalidTokenError
) -> JSONResponse:
    return _error_response(401, exc.message)


async def user_not_found_handler(
    request: Request, exc: UserNotFoundError
) -> JSONResponse:
    return _error_response(404, exc.message)


async def email_exists_handler(
    request: Request, exc: EmailAlreadyExistsError
) -> JSONResponse:
    return _error_response(409, exc.message)


async def username_exists_handler(
    request: Request, exc: UsernameAlreadyExistsError
) -> JSONResponse:
    return _error_response(409, exc.message)


async def workspace_not_found_handler(
    request: Request, exc: WorkspaceNotFoundError
) -> JSONResponse:
    return _error_response(404, exc.message)


async def slug_exists_handler(
    request: Request, exc: SlugAlreadyExistsError
) -> JSONResponse:
    return _error_response(409, exc.message)


async def permission_denied_handler(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    return _error_response(403, exc.message)


async def brand_kit_not_found_handler(
    request: Request, exc: BrandKitNotFoundError
) -> JSONResponse:
    return _error_response(404, exc.message)


async def brand_kit_already_exists_handler(
    request: Request, exc: BrandKitAlreadyExistsError
) -> JSONResponse:
    return _error_response(409, exc.message)


async def social_account_not_found_handler(
    request: Request, exc: SocialAccountNotFoundError
) -> JSONResponse:
    return _error_response(404, exc.message)


async def social_account_already_exists_handler(
    request: Request, exc: SocialAccountAlreadyExistsError
) -> JSONResponse:
    return _error_response(409, exc.message)


async def project_not_found_handler(
    request: Request, exc: ProjectNotFoundError
) -> JSONResponse:
    return _error_response(404, exc.message)


async def project_slug_already_exists_handler(
    request: Request, exc: ProjectSlugAlreadyExistsError
) -> JSONResponse:
    return _error_response(409, exc.message)
