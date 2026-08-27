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


class GeneratePostRequest(BaseModel):
    platform: str
    concept: str
    tone: str
    goal: str
    audience: str
    hook: str


class GeneratePostResponse(BaseModel):
    title: str = Field(..., description="A punchy opening hook or title for the post (max 80 chars).")
    caption: str = Field(..., description="The main body of the post, excluding hashtags. Should be highly engaging and tailored to the platform.")
    hashtags: list[str] = Field(..., description="A list of 3-5 relevant hashtags (without the # symbol).")


class GenerateCaptionRequest(BaseModel):
    prompt: str
    platform: str


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


@router.post(
    "/generate-post",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[Any],
    summary="Generate Social Media Post",
)
async def generate_post(
    request: GeneratePostRequest,
    user_id: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
) -> ApiResponse[Any]:
    """
    Generate a full social media post using AI based on structured inputs.
    """
    prompt = f"""
    You are an expert social media manager. Create a highly engaging post for {request.platform}.
    Topic/Concept: {request.concept}
    Target Audience: {request.audience}
    Tone: {request.tone}
    Goal: {request.goal}
    Hook Style: {request.hook}
    
    Ensure the output fits the standard character limits and style of {request.platform}.
    Do NOT include hashtags in the caption body; provide them separately in the hashtags field.
    """
    
    result = await ai_service.generate_structured(
        prompt=prompt,
        response_schema=GeneratePostResponse
    )
    return ApiResponse.ok(data=result.model_dump(), message="Post generated successfully.")


@router.post(
    "/generate-caption",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[Any],
    summary="Generate Caption",
)
async def generate_caption(
    request: GenerateCaptionRequest,
    user_id: str = Depends(get_current_user_id),
    ai_service: AIService = Depends(get_ai_service),
) -> ApiResponse[Any]:
    """
    Quickly generate a caption based on a single prompt.
    """
    prompt = f"""
    Write a highly engaging social media caption for {request.platform} based on this prompt: "{request.prompt}".
    Keep it concise, punchy, and include a couple of relevant hashtags at the end.
    """
    
    result = await ai_service.generate_text(prompt=prompt)
    return ApiResponse.ok(data={"caption": result}, message="Caption generated successfully.")
