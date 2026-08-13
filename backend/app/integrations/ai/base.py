"""
app/integrations/ai/base.py

Abstract interface for AI providers (e.g., Gemini, OpenAI, Anthropic).
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AbstractAIProvider(ABC):
    """
    Protocol for interacting with an AI provider.
    """

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a text response from the model based on a prompt.
        
        Args:
            prompt: The text prompt.
            kwargs: Provider-specific overrides (e.g., temperature).
            
        Returns:
            The generated text string.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_structured(
        self, prompt: str, response_schema: Type[T], **kwargs: Any
    ) -> T:
        """
        Generate a structured response adhering to a Pydantic schema.
        
        Args:
            prompt: The text prompt.
            response_schema: A Pydantic BaseModel class defining the expected output.
            kwargs: Provider-specific overrides.
            
        Returns:
            An instance of the response_schema populated with the generated data.
        """
        raise NotImplementedError

    @abstractmethod
    def model_name(self) -> str:
        """
        Return the underlying model name configured for this provider.
        """
        raise NotImplementedError
