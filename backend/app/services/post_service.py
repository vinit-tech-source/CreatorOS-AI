"""
app/services/post_service.py

Post business logic for CreatorOS AI.

Responsibilities:
  - Create, read, update, delete Content Posts.
  - Enforce workspace ownership boundaries via Project.
  - Enforce valid state transitions for Posts.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.exceptions import (
    InvalidStatusTransitionError,
    PostNotFoundError,
    ProjectNotFoundError,
)
from app.models.post import PostStatus
from app.repositories.post_repository_interface import AbstractPostRepository
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.schemas.post import (
    PostCreate,
    PostResponse,
    PostUpdate,
)
from app.core.database import AsyncSessionLocal
from app.models.approval_log import ApprovalLog, ApprovalAction

logger = logging.getLogger(__name__)


# Define valid transitions (From -> List of valid To states)
# If a state is not in the keys, it's considered terminal or allows no outbound transitions.
VALID_TRANSITIONS = {
    PostStatus.DRAFT: [PostStatus.PENDING_REVIEW, PostStatus.ARCHIVED],
    PostStatus.PENDING_REVIEW: [PostStatus.APPROVED, PostStatus.REJECTED, PostStatus.DRAFT, PostStatus.ARCHIVED],
    PostStatus.APPROVED: [PostStatus.SCHEDULED, PostStatus.PUBLISHED, PostStatus.DRAFT, PostStatus.ARCHIVED],
    PostStatus.REJECTED: [PostStatus.DRAFT, PostStatus.ARCHIVED],
    PostStatus.SCHEDULED: [PostStatus.PUBLISHED, PostStatus.FAILED, PostStatus.DRAFT, PostStatus.ARCHIVED],
    PostStatus.PUBLISHED: [PostStatus.ARCHIVED],
    PostStatus.FAILED: [PostStatus.DRAFT, PostStatus.ARCHIVED],
    PostStatus.ARCHIVED: [PostStatus.DRAFT], # Allow unarchiving to draft
}


class PostService:
    """
    Handles Post business logic.
    """

    def __init__(
        self,
        post_repository: AbstractPostRepository,
        project_repository: AbstractProjectRepository,
        workspace_repository: AbstractWorkspaceRepository,
    ) -> None:
        self._post_repo = post_repository
        self._project_repo = project_repository
        self._ws_repo = workspace_repository

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    async def _assert_project_ownership(
        self, project_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        """
        Verify that the project exists, its workspace exists, and the workspace is owned
        by the requesting user.
        Raises ProjectNotFoundError if any check fails to prevent info leakage.
        """
        project = await self._project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError()

        workspace = await self._ws_repo.get_by_id(project.workspace_id)
        if workspace is None or workspace.owner_id != requesting_user_id:
            logger.warning(
                f"Post operation denied: user={requesting_user_id} does not own "
                f"workspace={project.workspace_id} for project={project_id}"
            )
            # Re-raise ProjectNotFoundError to avoid leaking workspace ownership details
            raise ProjectNotFoundError()

    def _validate_status_transition(self, current: PostStatus, new: PostStatus) -> None:
        """Check if a transition from current to new status is allowed."""
        if current == new:
            return  # No change

        allowed_next_states = VALID_TRANSITIONS.get(current, [])
        if new not in allowed_next_states:
            raise InvalidStatusTransitionError(
                f"Cannot transition post status from {current.value} to {new.value}."
            )

    async def _log_approval(
        self,
        post_id: uuid.UUID,
        workspace_id: uuid.UUID,
        actor_id: uuid.UUID,
        action: ApprovalAction,
        prev_status: PostStatus,
        new_status: PostStatus,
    ) -> None:
        async with AsyncSessionLocal() as session:
            log = ApprovalLog(
                post_id=post_id,
                workspace_id=workspace_id,
                actor_user_id=actor_id,
                action=action,
                previous_status=prev_status,
                new_status=new_status,
            )
            session.add(log)
            await session.commit()

    # ─────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────

    async def create_post(
        self,
        project_id: uuid.UUID,
        data: PostCreate,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        """
        Create a new Content Post in the project.
        """
        await self._assert_project_ownership(project_id, requesting_user_id)

        post = await self._post_repo.create(data, project_id)
        return PostResponse.model_validate(post)

    # ─────────────────────────────────────────────
    # Read (Single)
    # ─────────────────────────────────────────────

    async def get_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        """
        Retrieve details of a specific post.
        """
        await self._assert_project_ownership(project_id, requesting_user_id)

        post = await self._post_repo.get_by_id(post_id)
        if post is None or post.project_id != project_id:
            raise PostNotFoundError()

        return PostResponse.model_validate(post)

    # ─────────────────────────────────────────────
    # Read (List)
    # ─────────────────────────────────────────────

    async def list_posts(
        self,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> list[PostResponse]:
        """
        List all posts for the project.
        """
        await self._assert_project_ownership(project_id, requesting_user_id)

        posts = await self._post_repo.list_by_project(project_id)
        return [PostResponse.model_validate(p) for p in posts]

    async def list_pending_review_posts(
        self,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> list[PostResponse]:
        """
        List all posts for the project that are pending review.
        """
        await self._assert_project_ownership(project_id, requesting_user_id)

        posts = await self._post_repo.list_by_project(project_id)
        pending_posts = [p for p in posts if p.status == PostStatus.PENDING_REVIEW]
        return [PostResponse.model_validate(p) for p in pending_posts]

    # ─────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────

    async def update_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        data: PostUpdate,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        """
        Apply partial updates to a post, validating state transitions.
        """
        await self._assert_project_ownership(project_id, requesting_user_id)

        post = await self._post_repo.get_by_id(post_id)
        if post is None or post.project_id != project_id:
            raise PostNotFoundError()

        if data.status is not None:
            self._validate_status_transition(post.status, data.status)

        updated = await self._post_repo.update(post, data)
        return PostResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Approval
    # ─────────────────────────────────────────────

    async def submit_for_review(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        await self._assert_project_ownership(project_id, requesting_user_id)
        post = await self._post_repo.get_by_id(post_id)
        if post is None or post.project_id != project_id:
            raise PostNotFoundError()
            
        self._validate_status_transition(post.status, PostStatus.PENDING_REVIEW)
        
        project = await self._project_repo.get_by_id(project_id)
        
        prev_status = post.status
        data = PostUpdate(status=PostStatus.PENDING_REVIEW, approval_status="SUBMITTED")
        updated = await self._post_repo.update(post, data)
        
        await self._log_approval(post_id, project.workspace_id, requesting_user_id, ApprovalAction.SUBMIT, prev_status, PostStatus.PENDING_REVIEW)
        return PostResponse.model_validate(updated)

    async def approve_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        await self._assert_project_ownership(project_id, requesting_user_id)
        post = await self._post_repo.get_by_id(post_id)
        if post is None or post.project_id != project_id:
            raise PostNotFoundError()
            
        self._validate_status_transition(post.status, PostStatus.APPROVED)
        
        project = await self._project_repo.get_by_id(project_id)
        
        prev_status = post.status
        data = PostUpdate(
            status=PostStatus.APPROVED, 
            approval_status="APPROVED", 
            approved_by=requesting_user_id, 
            approved_at=datetime.now(timezone.utc)
        )
        updated = await self._post_repo.update(post, data)
        
        await self._log_approval(post_id, project.workspace_id, requesting_user_id, ApprovalAction.APPROVE, prev_status, PostStatus.APPROVED)
        return PostResponse.model_validate(updated)

    async def reject_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        reason: str,
        requesting_user_id: uuid.UUID,
    ) -> PostResponse:
        await self._assert_project_ownership(project_id, requesting_user_id)
        post = await self._post_repo.get_by_id(post_id)
        if post is None or post.project_id != project_id:
            raise PostNotFoundError()
            
        self._validate_status_transition(post.status, PostStatus.REJECTED)
        
        project = await self._project_repo.get_by_id(project_id)
        
        prev_status = post.status
        data = PostUpdate(
            status=PostStatus.REJECTED, 
            approval_status="REJECTED", 
            rejection_reason=reason
        )
        updated = await self._post_repo.update(post, data)
        
        await self._log_approval(post_id, project.workspace_id, requesting_user_id, ApprovalAction.REJECT, prev_status, PostStatus.REJECTED)
        return PostResponse.model_validate(updated)

    # ─────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────

    async def delete_post(
        self,
        project_id: uuid.UUID,
        post_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        """
        Delete a post permanently.
        """
        await self._assert_project_ownership(project_id, requesting_user_id)

        post = await self._post_repo.get_by_id(post_id)
        if post is None or post.project_id != project_id:
            raise PostNotFoundError()

        await self._post_repo.delete(post)
