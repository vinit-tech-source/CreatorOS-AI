"""
tests/test_ai_service.py

Unit tests for AI provider and service.
"""
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel, Field, ValidationError

from app.core.exceptions import AIProviderError, AIValidationError
from app.integrations.ai.base import AbstractAIProvider
from app.services.ai_service import AIService


class DummySchema(BaseModel):
    title: str = Field(...)
    score: int = Field(...)


class MockAIProvider(AbstractAIProvider):
    def __init__(self):
        self.text_result = "Test text response."
        self.structured_result = DummySchema(title="Test", score=100)
        self.should_timeout = False
        self.should_fail = False
        self.should_fail_validation = False

    def model_name(self) -> str:
        return "mock-model"

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        if self.should_fail or self.should_timeout:
            raise AIProviderError("Mock provider failure.")
        return self.text_result

    async def generate_structured(
        self, prompt: str, response_schema: type[BaseModel], **kwargs: Any
    ) -> BaseModel:
        if self.should_fail or self.should_timeout:
            raise AIProviderError("Mock provider failure.")
        if self.should_fail_validation:
            raise AIValidationError("Mock validation failure.")
        return self.structured_result


@pytest.mark.asyncio
async def test_generate_text_success():
    provider = MockAIProvider()
    service = AIService(provider=provider)
    result = await service.generate_text("Hello")
    assert result == "Test text response."


@pytest.mark.asyncio
async def test_generate_structured_success():
    provider = MockAIProvider()
    service = AIService(provider=provider)
    result = await service.generate_structured("Hello", DummySchema)
    assert isinstance(result, DummySchema)
    assert result.title == "Test"
    assert result.score == 100


@pytest.mark.asyncio
async def test_generate_text_provider_failure():
    provider = MockAIProvider()
    provider.should_fail = True
    service = AIService(provider=provider)
    with pytest.raises(AIProviderError):
        await service.generate_text("Hello")


@pytest.mark.asyncio
async def test_generate_structured_provider_failure():
    provider = MockAIProvider()
    provider.should_fail = True
    service = AIService(provider=provider)
    with pytest.raises(AIProviderError):
        await service.generate_structured("Hello", DummySchema)


@pytest.mark.asyncio
async def test_generate_structured_validation_failure():
    provider = MockAIProvider()
    provider.should_fail_validation = True
    service = AIService(provider=provider)
    with pytest.raises(AIValidationError):
        await service.generate_structured("Hello", DummySchema)


def test_get_model_name():
    provider = MockAIProvider()
    service = AIService(provider=provider)
    assert service.get_model_name() == "mock-model"
