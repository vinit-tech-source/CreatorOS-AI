"""
app/api/posts.py

Content Post API endpoints for CreatorOS AI.
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_post_service, get_scheduler_service, get_analytics_service, get_project_service
from app.schemas.response import ApiResponse
from app.schemas.post import (
    PostCreate,
    PostResponse,
    PostUpdate,
    PostReject,
    PostSchedule,
)
from app.schemas.analytics import PostAnalyticsResponse
from app.services.post_service import PostService
from app.services.project_service import ProjectService
from app.services.scheduler_service import SchedulerService
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/projects/{project_id}/posts",
    tags=["Posts"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[PostResponse],
    summary="Create Post",
    description="Create a new Content Post within a project.",
)
async def create_post(
    project_id: uuid.UUID,
    data: PostCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[PostResponse]:
    post = await service.create_post(
        project_id=project_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post created successfully.")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[PostResponse]],
    summary="List Posts",
    description="List all Content Posts in the project.",
)
async def list_posts(
    project_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[list[PostResponse]]:
    posts = await service.list_posts(
        project_id=project_id,
        requesting_user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return ApiResponse.ok(data=posts)


@router.get(
    "/scheduled",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[PostResponse]],
    summary="List Scheduled Posts",
    description="List all scheduled posts in the project.",
)
async def list_scheduled_posts(
    project_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SchedulerService = Depends(get_scheduler_service),
) -> ApiResponse[list[PostResponse]]:
    posts = await service.list_scheduled_posts(
        project_id=project_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=posts)


@router.get(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Get Post",
    description="Retrieve details of a specific Content Post.",
)
async def get_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[PostResponse]:
    post = await service.get_post(
        project_id=project_id,
        post_id=post_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post)


@router.patch(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Update Post",
    description="Apply partial updates to a Content Post.",
)
async def update_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    data: PostUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[PostResponse]:
    post = await service.update_post(
        project_id=project_id,
        post_id=post_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post updated successfully.")


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Post",
    description="Permanently delete a Content Post.",
)
async def delete_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[None]:
    await service.delete_post(
        project_id=project_id,
        post_id=post_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Post deleted successfully.")


@router.get(
    "/status/pending-review",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[PostResponse]],
    summary="List Posts Pending Review",
    description="List all posts that are pending review in the project.",
)
async def list_pending_review_posts(
    project_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[list[PostResponse]]:
    posts = await service.list_pending_review_posts(
        project_id=project_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=posts)


@router.post(
    "/{post_id}/submit-review",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Submit Post for Review",
    description="Transitions a DRAFT post to PENDING_REVIEW.",
)
async def submit_post_for_review(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[PostResponse]:
    post = await service.submit_for_review(
        project_id=project_id,
        post_id=post_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post submitted for review.")


@router.post(
    "/{post_id}/approve",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Approve Post",
    description="Approves a PENDING_REVIEW post.",
)
async def approve_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[PostResponse]:
    post = await service.approve_post(
        project_id=project_id,
        post_id=post_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post approved.")


@router.post(
    "/{post_id}/reject",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Reject Post",
    description="Rejects a PENDING_REVIEW post.",
)
async def reject_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    data: PostReject,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[PostResponse]:
    post = await service.reject_post(
        project_id=project_id,
        post_id=post_id,
        reason=data.rejection_reason,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post rejected.")


@router.post(
    "/{post_id}/schedule",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Schedule Post",
    description="Schedules an APPROVED post for publication.",
)
async def schedule_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    data: PostSchedule,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SchedulerService = Depends(get_scheduler_service),
) -> ApiResponse[PostResponse]:
    post = await service.schedule_post(
        project_id=project_id,
        post_id=post_id,
        schedule_data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post scheduled.")


@router.patch(
    "/{post_id}/schedule",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Reschedule Post",
    description="Reschedules a previously scheduled post.",
)
async def reschedule_post(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    data: PostSchedule,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SchedulerService = Depends(get_scheduler_service),
) -> ApiResponse[PostResponse]:
    post = await service.reschedule_post(
        project_id=project_id,
        post_id=post_id,
        schedule_data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Post rescheduled.")


@router.delete(
    "/{post_id}/schedule",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[PostResponse],
    summary="Cancel Schedule",
    description="Cancels a scheduled post.",
)
async def cancel_schedule(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: SchedulerService = Depends(get_scheduler_service),
) -> ApiResponse[PostResponse]:
    post = await service.cancel_schedule(
        project_id=project_id,
        post_id=post_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=post, message="Schedule cancelled.")

@router.get(
    "/{post_id}/analytics",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[PostAnalyticsResponse]],
    summary="Get Post Analytics",
    description="Retrieve analytics history for a specific post.",
)
async def get_post_analytics(
    project_id: uuid.UUID,
    post_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    project_service: ProjectService = Depends(get_project_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[list[PostAnalyticsResponse]]:
    project = await project_service.get_project(project_id=project_id, requesting_user_id=user_id)
    analytics = await analytics_service.get_post_analytics(post_id=post_id, workspace_id=project.workspace_id)
    return ApiResponse.ok(data=analytics)
