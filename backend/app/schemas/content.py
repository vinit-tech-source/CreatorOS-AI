"""
app/schemas/content.py

Pydantic schemas for AI Content Generation requests and responses.
"""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class ContentGenerateRequest(BaseModel):
    workspace_id: uuid.UUID
    project_id: uuid.UUID
    platform: str
    content_type: str
    user_request: str
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    language: str = "English"
    additional_instructions: Optional[str] = None


class HashtagSchema(BaseModel):
    tag: str
    isNiche: bool
    relevanceScore: int


class ImagePromptSchema(BaseModel):
    visualStyle: str
    composition: str
    aspectRatio: str
    lighting: str
    colorPalette: str
    altText: str
    prompt: str


class BrandVoiceSchema(BaseModel):
    score: int
    isCompliant: bool
    issues: List[str]
    changesMade: List[str]


class FactCheckIssueSchema(BaseModel):
    claim: str
    status: str
    explanation: str
    confidence: float
    evidence: Optional[str] = None


class FactCheckSchema(BaseModel):
    status: str
    issues: List[FactCheckIssueSchema]


class SEOSchema(BaseModel):
    score: int
    primaryKeywords: List[str]
    secondaryKeywords: List[str]
    recommendations: List[str]


class ContentGenerateResponse(BaseModel):
    title: str
    content: str
    platform: str
    contentType: str
    hashtags: List[HashtagSchema]
    cta: str
    imagePrompt: ImagePromptSchema
    brandVoice: BrandVoiceSchema
    factCheck: FactCheckSchema
    seo: SEOSchema
