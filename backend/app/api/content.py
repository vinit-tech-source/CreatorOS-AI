"""
app/api/content.py

API endpoints for generating content using AI workflows.
"""
import uuid

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user_id, get_content_generation_service
from app.schemas.response import ApiResponse
from app.schemas.content import ContentGenerateRequest, ContentGenerateResponse
from app.services.content_generation_service import ContentGenerationService

router = APIRouter(
    prefix="/content",
    tags=["Content Generation"],
)


@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ContentGenerateResponse],
    summary="Generate AI Content",
    description="Invokes the LangGraph workflow to generate content based on the project and workspace context.",
)
async def generate_content(
    request: ContentGenerateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ContentGenerationService = Depends(get_content_generation_service),
) -> ApiResponse[ContentGenerateResponse]:
    result = await service.generate_content(
        request=request,
        requesting_user_id=user_id,
    )
    return ApiResponse.ok(data=result, message="Content generated successfully.")
