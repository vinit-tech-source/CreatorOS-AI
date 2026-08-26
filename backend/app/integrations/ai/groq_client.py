import json
import logging
from typing import Any, Type, TypeVar
from pydantic import BaseModel
from groq import AsyncGroq
from app.integrations.ai.base import AbstractAIProvider
from app.core.exceptions import AIProviderError, AIValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class GroqClient(AbstractAIProvider):
    """
    Implementation of AbstractAIProvider for Groq API.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        timeout: int = 60,
    ):
        if not api_key:
            raise ValueError("Groq API key is required.")
        self.api_key = api_key
        self._model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.timeout = timeout
        
        self.client = AsyncGroq(api_key=self.api_key, timeout=self.timeout)

    def model_name(self) -> str:
        return self._model_name

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        try:
            temp = kwargs.get("temperature", self.temperature)
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=self.max_output_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq text generation failed: {e}")
            raise AIProviderError(f"Groq text generation failed: {type(e).__name__}") from e

    async def generate_structured(self, prompt: str, response_schema: Type[T], **kwargs: Any) -> T:
        try:
            schema_json = json.dumps(response_schema.model_json_schema())
            system_prompt = (
                f"You are a structured data extraction assistant. "
                f"You MUST output valid JSON exactly matching this JSON Schema:\n{schema_json}\n"
                f"Return ONLY the JSON object. Do NOT wrap it in markdown quotes."
            )
            
            temp = kwargs.get("temperature", self.temperature)
            
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=self.max_output_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content or "{}"
            
            try:
                parsed_data = response_schema.model_validate_json(content)
                return parsed_data
            except Exception as e:
                logger.error(f"Failed to parse or validate Groq output: {e}\nContent: {content}")
                raise AIValidationError(f"Invalid structured output: {e}") from e

        except AIValidationError:
            raise
        except Exception as e:
            logger.error(f"Groq structured generation failed: {e}")
            raise AIProviderError(f"Groq structured generation failed: {type(e).__name__}") from e
