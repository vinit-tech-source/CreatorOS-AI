"""
app/integrations/ai/gemini_client.py

Gemini implementation of the AbstractAIProvider.
"""
import logging
from typing import Any, Type

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.exceptions import AIProviderError, AIValidationError
from app.integrations.ai.base import AbstractAIProvider, T

logger = logging.getLogger(__name__)


class GeminiClient(AbstractAIProvider):
    """
    Gemini provider implementation using the google-genai SDK.
    """

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            # We don't raise immediately here so the app can start without AI
            # but we log a warning. The error will happen on generation.
            logger.warning("GEMINI_API_KEY is not set.")
            self._client = None
        else:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
        self._model = settings.GEMINI_MODEL

    def _get_client(self) -> genai.Client:
        if self._client is None:
            raise AIProviderError("AI configuration is missing API key.")
        return self._client

    def model_name(self) -> str:
        return self._model

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        client = self._get_client()
        
        # Merge config defaults with kwargs
        temperature = kwargs.get("temperature", settings.GEMINI_TEMPERATURE)
        max_output_tokens = kwargs.get("max_output_tokens", settings.GEMINI_MAX_OUTPUT_TOKENS)
        
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        try:
            # We use the async client 'aio'
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            if not response.text:
                raise AIProviderError("Empty response from AI provider.")
            return response.text
        except Exception as e:
            logger.error("Gemini text generation failed.")
            # We never log the API key or raw provider internal state directly to users
            raise AIProviderError(f"AI text generation failed: {type(e).__name__}") from e

    async def generate_structured(
        self, prompt: str, response_schema: Type[T], **kwargs: Any
    ) -> T:
        client = self._get_client()
        
        temperature = kwargs.get("temperature", settings.GEMINI_TEMPERATURE)
        max_output_tokens = kwargs.get("max_output_tokens", settings.GEMINI_MAX_OUTPUT_TOKENS)
        
        # Tell Gemini to return JSON adhering to the Pydantic schema
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        try:
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            if not response.text:
                raise AIProviderError("Empty structured response from AI provider.")
                
            json_text = response.text
        except Exception as e:
            logger.error("Gemini structured generation failed.")
            raise AIProviderError(f"AI structured generation failed: {type(e).__name__}") from e

        # Validate with Pydantic
        try:
            # google-genai returns a JSON string when response_mime_type is JSON
            parsed = response_schema.model_validate_json(json_text)
            return parsed
        except ValidationError as e:
            logger.error("AI output failed schema validation.")
            raise AIValidationError("The generated AI response did not match the required schema.") from e
