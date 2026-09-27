"""
app/api/workspace.py

Workspace API endpoints for CreatorOS AI.

Endpoints:
  POST    /api/v1/workspaces           — Create a new workspace
  GET     /api/v1/workspaces           — List all workspaces owned by the user
  GET     /api/v1/workspaces/{id}      — Get a workspace by ID
  PATCH   /api/v1/workspaces/{id}      — Update a workspace
  DELETE  /api/v1/workspaces/{id}      — Delete a workspace
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from app.api.deps import get_current_user_id, get_workspace_service, get_analytics_service
from app.schemas.response import ApiResponse
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.schemas.analytics import AnalyticsSummary, PostAnalyticsResponse
from app.services.workspace_service import WorkspaceService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


# ─────────────────────────────────────────────
# POST /workspaces
# ─────────────────────────────────────────────

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[WorkspaceResponse],
    summary="Create a new workspace",
    description="Create a new workspace for the authenticated user. Slug must be unique.",
)
async def create_workspace(
    data: WorkspaceCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> ApiResponse[WorkspaceResponse]:
    workspace = await workspace_service.create_workspace(data, owner_id=user_id)
    return ApiResponse.ok(data=workspace, message="Workspace created successfully.")


# ─────────────────────────────────────────────
# GET /workspaces
# ─────────────────────────────────────────────

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[List[WorkspaceResponse]],
    summary="List workspaces",
    description="List all workspaces owned by the authenticated user.",
)
async def list_workspaces(
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> ApiResponse[List[WorkspaceResponse]]:
    workspaces = await workspace_service.list_workspaces(owner_id=user_id)
    return ApiResponse.ok(data=workspaces)


# ─────────────────────────────────────────────
# GET /workspaces/{workspace_id}
# ─────────────────────────────────────────────

@router.get(
    "/{workspace_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[WorkspaceResponse],
    summary="Get a workspace",
    description="Retrieve a single workspace by its UUID.",
)
async def get_workspace(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> ApiResponse[WorkspaceResponse]:
    workspace = await workspace_service.get_workspace(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=workspace)


# ─────────────────────────────────────────────
# PATCH /workspaces/{workspace_id}
# ─────────────────────────────────────────────

@router.patch(
    "/{workspace_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[WorkspaceResponse],
    summary="Update a workspace",
    description="Apply partial updates to a workspace. Only the owner can perform this action.",
)
async def update_workspace(
    workspace_id: uuid.UUID,
    data: WorkspaceUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> ApiResponse[WorkspaceResponse]:
    workspace = await workspace_service.update_workspace(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=workspace, message="Workspace updated successfully.")


# ─────────────────────────────────────────────
# DELETE /workspaces/{workspace_id}
# ─────────────────────────────────────────────

@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete a workspace",
    description="Permanently delete a workspace. Only the owner can perform this action.",
)
async def delete_workspace(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> ApiResponse[None]:
    await workspace_service.delete_workspace(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Workspace deleted successfully.")

# ─────────────────────────────────────────────
# GET /workspaces/{workspace_id}/analytics/summary
# ─────────────────────────────────────────────

@router.get(
    "/{workspace_id}/analytics/summary",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[AnalyticsSummary],
    summary="Get Workspace Analytics Summary",
    description="Retrieve aggregated analytics for a workspace.",
)
@cache(expire=60)
async def get_workspace_analytics_summary(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[AnalyticsSummary]:
    # Check if user has access to workspace
    await workspace_service.get_workspace(workspace_id=workspace_id, requesting_user_id=user_id)
    summary = await analytics_service.get_workspace_summary(workspace_id=workspace_id)
    return ApiResponse.ok(data=summary)


# ─────────────────────────────────────────────
# GET /workspaces/{workspace_id}/analytics/posts
# ─────────────────────────────────────────────

@router.get(
    "/{workspace_id}/analytics/posts",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[List[PostAnalyticsResponse]],
    summary="List Workspace Posts Analytics",
    description="Retrieve analytics for all posts in a workspace.",
)
async def list_workspace_posts_analytics(
    workspace_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
    user_id: uuid.UUID = Depends(get_current_user_id),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[List[PostAnalyticsResponse]]:
    # Check if user has access to workspace
    await workspace_service.get_workspace(workspace_id=workspace_id, requesting_user_id=user_id)
    posts_analytics = await analytics_service.analytics_repo.list_snapshots_by_workspace(workspace_id, limit, offset)
    return ApiResponse.ok(data=posts_analytics)

