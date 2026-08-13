"""
app/services/ai_service.py

AI Service for CreatorOS AI.
"""
from typing import Any, Type

from app.integrations.ai.base import AbstractAIProvider, T


class AIService:
    """
    Service layer for AI generation tasks.
    Delegates to the configured AI Provider.
    """

    def __init__(self, provider: AbstractAIProvider) -> None:
        self._provider = provider

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate plain text using the AI provider.
        """
        return await self._provider.generate_text(prompt, **kwargs)

    async def generate_structured(
        self, prompt: str, response_schema: Type[T], **kwargs: Any
    ) -> T:
        """
        Generate structured data adhering to a Pydantic schema using the AI provider.
        """
        return await self._provider.generate_structured(prompt, response_schema, **kwargs)

    def get_model_name(self) -> str:
        """
        Return the name of the model being used.
        """
        return self._provider.model_name()
