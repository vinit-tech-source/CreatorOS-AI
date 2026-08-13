"""
app/api/ai.py

Development endpoints for testing the AI provider integration.
"""
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user_id, get_ai_service
from app.schemas.response import ApiResponse
from app.services.ai_service import AIService

router = APIRouter(
    prefix="/ai",
    tags=["AI (Development)"],
)


class TestPromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    structured: bool = Field(False, description="If true, requests a structured response.")


class TestStructuredResponse(BaseModel):
    summary: str = Field(..., description="A short summary of the input prompt.")
    sentiment: str = Field(..., description="The sentiment of the prompt (Positive, Negative, Neutral).")


@router.post(
    "/test-generation",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[Any],
    summary="Test AI Generation",
    description="Development endpoint to test the configured AI provider. Requires authentication.",
)
async def test_generation(
    request: TestPromptRequest,
    user_id: str = Depends(get_current_user_id),  # Just to ensure it's protected
    ai_service: AIService = Depends(get_ai_service),
) -> ApiResponse[Any]:
    """
    Test endpoint for AI generation.
    DO NOT USE IN PRODUCTION.
    """
    if request.structured:
        result = await ai_service.generate_structured(
            prompt=request.prompt,
            response_schema=TestStructuredResponse
        )
        return ApiResponse.ok(data=result.model_dump(), message="Structured generation successful.")
    else:
        result = await ai_service.generate_text(prompt=request.prompt)
        return ApiResponse.ok(data={"text": result}, message="Text generation successful.")
