"""
app/api/projects.py

Content Project API endpoints for CreatorOS AI.
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_project_service
from app.schemas.response import ApiResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects",
    tags=["Projects"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ProjectResponse],
    summary="Create Project",
    description="Create a new Content Project within a workspace.",
)
async def create_project(
    workspace_id: uuid.UUID,
    data: ProjectCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[ProjectResponse]:
    project = await service.create_project(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=project, message="Project created successfully.")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[ProjectResponse]],
    summary="List Projects",
    description="List all Content Projects in the workspace.",
)
async def list_projects(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[list[ProjectResponse]]:
    projects = await service.list_projects(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=projects)


@router.get(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ProjectResponse],
    summary="Get Project",
    description="Retrieve details of a specific Content Project.",
)
async def get_project(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[ProjectResponse]:
    project = await service.get_project(
        workspace_id=workspace_id,
        project_id=project_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=project)


@router.patch(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ProjectResponse],
    summary="Update Project",
    description="Apply partial updates to a Content Project.",
)
async def update_project(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    data: ProjectUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[ProjectResponse]:
    project = await service.update_project(
        workspace_id=workspace_id,
        project_id=project_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=project, message="Project updated successfully.")


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Project",
    description="Permanently delete a Content Project.",
)
async def delete_project(
    workspace_id: uuid.UUID,
    project_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service),
) -> ApiResponse[None]:
    await service.delete_project(
        workspace_id=workspace_id,
        project_id=project_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Project deleted successfully.")
