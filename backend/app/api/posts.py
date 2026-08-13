"""
app/api/posts.py

Content Post API endpoints for CreatorOS AI.
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_post_service
from app.schemas.response import ApiResponse
from app.schemas.post import (
    PostCreate,
    PostResponse,
    PostUpdate,
)
from app.services.post_service import PostService

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
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: PostService = Depends(get_post_service),
) -> ApiResponse[list[PostResponse]]:
    posts = await service.list_posts(
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
