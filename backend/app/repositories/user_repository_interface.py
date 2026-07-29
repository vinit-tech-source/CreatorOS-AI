import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class AbstractUserRepository(ABC):
    """Abstract interface for the User repository."""

    @abstractmethod
    async def create(self, data: UserCreate, password_hash: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User, data: UserUpdate) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: User) -> None:
        raise NotImplementedError
