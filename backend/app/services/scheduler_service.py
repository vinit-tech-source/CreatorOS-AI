"""
app/services/scheduler_service.py

Service for managing the scheduling of content posts.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.exceptions import (
    PostNotFoundError,
    ProjectNotFoundError,
    InvalidStatusTransitionError,
    PermissionDeniedError,
)
from app.models.post import Post, PostStatus, SchedulingStatus
from app.models.project import Project
from app.models.social_account import SocialAccount
from app.schemas.post import PostResponse, PostSchedule, PostUpdate
from app.repositories.post_repository_interface import AbstractPostRepository
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(
        self,
        post_repo: AbstractPostRepository,
        project_repo: AbstractProjectRepository,
        workspace_repo: AbstractWorkspaceRepository,
    ) -> None:
        self._post_repo = post_repo
        self._project_repo = project_repo
        self._workspace_repo = workspace_repo

    async def _assert_project_ownership(
        self, project_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        workspace = await self._workspace_repo.get_by_id(project.workspace_id)
        if not workspace:
            raise ProjectNotFoundError()

        if workspace.owner_id != requesting_user_id:
            raise ProjectNotFoundError()

    async def schedule_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        schedule_data: PostSchedule,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        """Schedules an approved post for publication."""
        await self._assert_project_ownership(project_id, requesting_user_id)
        post = await self._post_repo.get_by_id(post_id)
        if not post or post.project_id != project_id:
            raise PostNotFoundError()
            
        if post.status != PostStatus.APPROVED:
            raise InvalidStatusTransitionError(f"Only APPROVED posts can be scheduled. Current status: {post.status.value}")
            
        if schedule_data.scheduled_at <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be in the future.")
            
        data = PostUpdate(
            scheduled_at=schedule_data.scheduled_at,
            timezone=schedule_data.timezone,
            scheduling_status=SchedulingStatus.SCHEDULED,
            status=PostStatus.SCHEDULED
        )
        updated = await self._post_repo.update(post, data)
        return PostResponse.model_validate(updated)

    async def reschedule_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        schedule_data: PostSchedule,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        """Reschedules an already scheduled post."""
        await self._assert_project_ownership(project_id, requesting_user_id)
        post = await self._post_repo.get_by_id(post_id)
        if not post or post.project_id != project_id:
            raise PostNotFoundError()
            
        if post.status not in [PostStatus.SCHEDULED, PostStatus.FAILED]:
            raise InvalidStatusTransitionError(f"Cannot reschedule post in status: {post.status.value}")
            
        if schedule_data.scheduled_at <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be in the future.")
            
        data = PostUpdate(
            scheduled_at=schedule_data.scheduled_at,
            timezone=schedule_data.timezone,
            scheduling_status=SchedulingStatus.SCHEDULED,
            status=PostStatus.SCHEDULED,
            scheduled_attempts=0, # reset attempts on manual reschedule
            failure_reason=None
        )
        updated = await self._post_repo.update(post, data)
        return PostResponse.model_validate(updated)

    async def cancel_schedule(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        """Cancels a scheduled post, reverting to APPROVED."""
        await self._assert_project_ownership(project_id, requesting_user_id)
        post = await self._post_repo.get_by_id(post_id)
        if not post or post.project_id != project_id:
            raise PostNotFoundError()
            
        if post.status != PostStatus.SCHEDULED:
            raise InvalidStatusTransitionError(f"Cannot cancel schedule for post in status: {post.status.value}")
            
        data = PostUpdate(
            scheduled_at=None,
            timezone=None,
            scheduling_status=SchedulingStatus.CANCELLED,
            status=PostStatus.APPROVED
        )
        updated = await self._post_repo.update(post, data)
        return PostResponse.model_validate(updated)

    async def list_scheduled_posts(
        self,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> list[PostResponse]:
        """Lists all scheduled posts for a project."""
        await self._assert_project_ownership(project_id, requesting_user_id)
        posts = await self._post_repo.list_by_project(project_id)
        
        scheduled = [p for p in posts if p.status == PostStatus.SCHEDULED]
        return [PostResponse.model_validate(p) for p in scheduled]

    async def get_due_posts(self, limit: int = 10) -> list[PostResponse]:
        """Gets due posts. Called internally by the worker, no user validation needed."""
        # Using the new repo method, though we actually want them returned as models
        posts = await self._post_repo.get_due_posts(limit=limit)
        # Note: Worker needs the actual DB objects or IDs, so we return PostResponse for consistency with service
        return [PostResponse.model_validate(p) for p in posts]

    async def claim_due_post(self, post_id: uuid.UUID) -> bool:
        """
        Atomically claim a post for processing using database-level locking.
        Returns True if claimed successfully, False if already claimed or not found.
        """
        async with AsyncSessionLocal() as session:
            stmt = select(Post).where(
                Post.id == post_id,
                Post.scheduling_status == SchedulingStatus.SCHEDULED,
                Post.status == PostStatus.SCHEDULED
            ).with_for_update(skip_locked=True)
            
            result = await session.execute(stmt)
            post = result.scalar_one_or_none()
            
            if not post:
                return False
                
            post.scheduling_status = SchedulingStatus.PROCESSING
            post.last_attempt_at = datetime.now(timezone.utc)
            post.scheduled_attempts += 1
            await session.commit()
            return True

    async def mark_completed(self, post_id: uuid.UUID) -> None:
        """Mark a post as successfully published."""
        async with AsyncSessionLocal() as session:
            stmt = select(Post).where(Post.id == post_id)
            result = await session.execute(stmt)
            post = result.scalar_one_or_none()
            if post:
                post.scheduling_status = SchedulingStatus.COMPLETED
                post.status = PostStatus.PUBLISHED
                post.published_at = datetime.now(timezone.utc)
                await session.commit()
                
    async def mark_failed(self, post_id: uuid.UUID, reason: str, retry: bool = False, max_retries: int = 3) -> None:
        """Mark a post as failed, potentially queuing it for retry."""
        async with AsyncSessionLocal() as session:
            stmt = select(Post).where(Post.id == post_id)
            result = await session.execute(stmt)
            post = result.scalar_one_or_none()
            if post:
                post.failure_reason = reason
                if retry and post.scheduled_attempts < max_retries:
                    # Retry: put it back to SCHEDULED
                    post.scheduling_status = SchedulingStatus.SCHEDULED
                    # We might add exponential backoff here by updating scheduled_at
                    # e.g., post.scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=5 * post.scheduled_attempts)
                else:
                    post.scheduling_status = SchedulingStatus.FAILED
                    post.status = PostStatus.FAILED
                await session.commit()
