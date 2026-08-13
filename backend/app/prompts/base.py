"""
app/prompts/base.py

Reusable prompt versioning and abstractions.
"""
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field


class PromptDefinition(BaseModel):
    """
    Metadata and content for an AI prompt.
    """
    prompt_id: str = Field(..., description="Unique identifier for the prompt (e.g., 'content_generator').")
    version: str = Field(..., description="Semantic version string (e.g., '1.0.0').")
    model: str = Field(..., description="The preferred model (e.g., 'gemini').")
    status: str = Field("draft", description="Status of the prompt ('draft', 'active', 'deprecated').")
    
    system_instructions: str = Field(..., description="The core system prompt guiding the agent's persona.")
    user_instructions: str = Field(..., description="The template for the user prompt. Can contain format placeholders.")
    
    output_schema: Optional[Type[BaseModel]] = Field(
        None, description="The Pydantic schema required for structured output, if any."
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional arbitrary metadata for tracking."
    )

    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        Populate the user_instructions template with the given context.
        """
        return self.user_instructions.format(**kwargs)
