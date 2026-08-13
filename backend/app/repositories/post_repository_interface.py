import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class AbstractPostRepository(ABC):
    """Abstract interface for the Post repository."""

    @abstractmethod
    async def create(self, data: PostCreate, project_id: uuid.UUID) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, post_id: uuid.UUID) -> Optional[Post]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_project(self, project_id: uuid.UUID) -> list[Post]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, post: Post, data: PostUpdate) -> Post:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, post: Post) -> None:
        raise NotImplementedError
