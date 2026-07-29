"""
app/core/exception_handlers.py

Maps application-level exceptions to standardised HTTP responses.
Register these handlers on the FastAPI app instance in main.py.
"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
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
