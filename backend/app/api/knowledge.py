import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_knowledge_service
from app.schemas.knowledge import KnowledgeSourceCreate, KnowledgeSourceResponse
from app.schemas.response import ApiResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/knowledge",
    tags=["Knowledge Base"],
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[KnowledgeSourceResponse],
    summary="Add Knowledge Source",
)
async def create_knowledge_source(
    workspace_id: uuid.UUID,
    data: KnowledgeSourceCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> ApiResponse[KnowledgeSourceResponse]:
    source = await knowledge_service.create_knowledge_source(
        workspace_id=workspace_id,
        data=data,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=source, message="Knowledge source added and processed.")

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[List[KnowledgeSourceResponse]],
    summary="List Knowledge Sources",
)
async def list_knowledge_sources(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> ApiResponse[List[KnowledgeSourceResponse]]:
    sources = await knowledge_service.list_knowledge_sources(
        workspace_id=workspace_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=sources)

@router.delete(
    "/{knowledge_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete Knowledge Source",
)
async def delete_knowledge_source(
    workspace_id: uuid.UUID,
    knowledge_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> ApiResponse[None]:
    await knowledge_service.delete_knowledge_source(
        workspace_id=workspace_id,
        knowledge_id=knowledge_id,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=None, message="Knowledge source deleted successfully.")
