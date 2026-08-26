"""
app/agents/content_generator_agent.py

Content Generator Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.generator import generator_prompt_v1
from app.services.ai_service import AIService
from app.workflows.state import ContentWorkflowState

logger = logging.getLogger(__name__)

# Global AI Service instance to avoid repeated instantiation
_ai_service_instance: AIService | None = None


async def _get_service() -> AIService:
    """Retrieve or initialize the AI Service."""
    global _ai_service_instance
    if _ai_service_instance is None:
        from app.api.deps import get_ai_provider
        provider = await get_ai_provider()
        _ai_service_instance = AIService(provider)
    return _ai_service_instance


def _calculate_word_count(text: str) -> int:
    return len(text.split())


async def content_generator_agent(state: ContentWorkflowState) -> dict:
    """
    Generate the content draft based on the outline, research, strategy, and trends.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (draft output).
    """
    logger.info("Content Generator Agent starting execution.")
    
    user_request = state.get("user_request")
    platform = state.get("platform")
    strategy = state.get("strategy")
    trends = state.get("trends", [])
    research = state.get("research", [])
    outline = state.get("outline")
    
    if not user_request:
        raise ValueError("Missing 'user_request' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not strategy:
        raise ValueError("Missing 'strategy' in workflow state.")
    if not trends:
        raise ValueError("Missing 'trends' in workflow state.")
    if not research:
        raise ValueError("Missing 'research' in workflow state.")
    if not outline:
        raise ValueError("Missing 'outline' in workflow state.")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = generator_prompt_v1.build_user_prompt(
        user_request=user_request,
        platform=platform,
        research_context=json.dumps(state.get("research", [])),
        workspace_rag_context=json.dumps(state.get("rag_context", [])),
        strategy_context=json.dumps(strategy),
        trends_context=json.dumps(trends),
        outline_context=json.dumps(outline),
        brand_kit_context=json.dumps(state.get("brand_kit") or {})
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{generator_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not generator_prompt_v1.output_schema:
            raise ValueError("Generator prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=generator_prompt_v1.output_schema
        )
        
        # Recalculate word and character counts deterministically
        actual_char_count = len(output.content)
        actual_word_count = _calculate_word_count(output.content)
        
        output.character_count = actual_char_count
        output.word_count = actual_word_count

        # Platform Constraint Validation
        if platform.upper() == "X":
            if output.content_type.upper() != "THREAD" and actual_char_count > 280:
                raise AIValidationError(
                    f"Platform constraint violation: X post exceeds 280 characters "
                    f"(actual: {actual_char_count})."
                )

        return {"draft": output.model_dump(mode='json')}

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Content Generator Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Content Generator Agent failed with unexpected error: {e}")
        raise
