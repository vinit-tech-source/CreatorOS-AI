import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository_interface import AbstractUserRepository
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserRepository(AbstractUserRepository):
    """
    Concrete implementation of the User repository.
    All database access for the User model is handled here.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: UserCreate, password_hash: str) -> User:
        """Create and persist a new User record."""
        user = User(
            email=data.email,
            username=data.username,
            password_hash=password_hash,
            full_name=data.full_name,
            role=data.role,
            region=data.region,
            country=data.country,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"User created: id={user.id} email={user.email}")
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Return a User by primary key, or None if not found."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Return a User by email address, or None if not found."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Return a User by username, or None if not found."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def update(self, user: User, data: UserUpdate) -> User:
        """Apply partial updates from UserUpdate schema to an existing User."""
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"User updated: id={user.id}")
        return user

    async def delete(self, user: User) -> None:
        """Permanently remove a User record from the database."""
        await self.session.delete(user)
        await self.session.commit()
        logger.info(f"User deleted: id={user.id}")
