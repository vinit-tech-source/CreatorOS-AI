"""
app/schemas/response.py

Standardized API response envelope used by all endpoints.
"""
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Wrapper returned by every endpoint.

    Attributes:
        success: True on 2xx responses, False on errors.
        data:    The payload for successful responses (None on errors).
        message: Optional human-readable message.
    """
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None

    @classmethod
    def ok(cls, data: T, message: Optional[str] = None) -> "ApiResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, message: str) -> "ApiResponse[None]":
        return cls(success=False, data=None, message=message)
