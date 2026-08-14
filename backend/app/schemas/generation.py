"""
app/schemas/generation.py

Pydantic schemas for the AI Content Generation workflow.
"""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class ContentGenerateRequest(BaseModel):
    """Schema for requesting a new content generation via AI."""
    workspace_id: uuid.UUID = Field(..., description="The workspace ID to validate against.")
    project_id: uuid.UUID = Field(..., description="The project ID to associate with.")
    platform: str = Field(..., min_length=1, description="Target social platform.")
    content_type: str = Field(..., min_length=1, description="Type of content (e.g., short_post, article).")
    user_request: str = Field(..., min_length=1, description="The user's prompt or requirements.")
    
    audience: Optional[str] = Field(None, description="Target audience.")
    tone: Optional[str] = Field(None, description="Desired tone of voice.")
    language: Optional[str] = Field("English", description="Target language.")
    additional_instructions: Optional[str] = Field(None, description="Any extra instructions.")


class HashtagResult(BaseModel):
    tag: str
    isNiche: bool
    relevanceScore: int


class ImagePromptResult(BaseModel):
    visualStyle: str
    composition: str
    aspectRatio: str
    lighting: str
    colorPalette: str
    altText: str
    prompt: str


class BrandVoiceResult(BaseModel):
    score: int
    isCompliant: bool
    issues: List[str]
    changesMade: List[str]


class FactCheckIssue(BaseModel):
    claim: str
    status: str
    explanation: str
    confidence: float
    evidence: Optional[str] = None


class FactCheckResult(BaseModel):
    status: str
    issues: List[FactCheckIssue]


class SeoResult(BaseModel):
    score: int
    primaryKeywords: List[str]
    secondaryKeywords: List[str]
    recommendations: List[str]


class GenerationResultResponse(BaseModel):
    """Strict structured schema returned to the frontend."""
    title: str = Field(default="")
    content: str = Field(default="")
    platform: str
    contentType: str
    hashtags: List[HashtagResult] = Field(default_factory=list)
    cta: str = Field(default="")
    imagePrompt: Optional[ImagePromptResult] = None
    brandVoice: Optional[BrandVoiceResult] = None
    factCheck: Optional[FactCheckResult] = None
    seo: Optional[SeoResult] = None
