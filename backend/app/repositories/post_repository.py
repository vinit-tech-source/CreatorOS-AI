"""
app/repositories/post_repository.py

Concrete SQLAlchemy 2.0 async implementation of the Post repository.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.repositories.post_repository_interface import AbstractPostRepository
from app.schemas.post import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


class PostRepository(AbstractPostRepository):
    """Concrete repository for Post database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: PostCreate, project_id: uuid.UUID) -> Post:
        """Persist a new Post to the database."""
        post = Post(
            project_id=project_id,
            title=data.title,
            content=data.content,
            content_type=data.content_type,
            status=data.status,
            platform=data.platform,
            scheduled_at=data.scheduled_at,
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        logger.info(
            f"Post created: id={post.id} project={project_id} platform={post.platform.value}"
        )
        return post

    async def get_by_id(self, post_id: uuid.UUID) -> Optional[Post]:
        """Return a Post by its UUID primary key."""
        result = await self.session.execute(
            select(Post).where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: uuid.UUID) -> list[Post]:
        """Return all Posts for a specific project, ordered newest first."""
        result = await self.session.execute(
            select(Post)
            .where(Post.project_id == project_id)
            .order_by(Post.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, post: Post, data: PostUpdate) -> Post:
        """Apply partial updates from PostUpdate schema.

        Uses exclude_unset=True so that:
          - Omitted fields are left unchanged.
          - Explicitly provided null values clear nullable fields.
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        logger.info(f"Post updated: id={post.id}")
        return post

    async def delete(self, post: Post) -> None:
        """Permanently remove a Post record."""
        await self.session.delete(post)
        await self.session.commit()
        logger.info(
            f"Post deleted: id={post.id} project={post.project_id}"
        )
