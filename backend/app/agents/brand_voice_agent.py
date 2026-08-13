"""
app/agents/brand_voice_agent.py

Brand Voice Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.brand_voice import brand_voice_prompt_v1
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


async def brand_voice_agent(state: ContentWorkflowState) -> dict:
    """
    Review and optionally revise the content draft against the Brand Kit.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (optimized_content and brand_voice).
    """
    logger.info("Brand Voice Agent starting execution.")
    
    draft = state.get("draft")
    platform = state.get("platform")
    brand_kit = state.get("brand_kit")
    strategy = state.get("strategy")
    
    if not draft:
        raise ValueError("Missing 'draft' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not brand_kit:
        raise ValueError("Missing 'brand_kit' in workflow state.")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = brand_voice_prompt_v1.build_user_prompt(
        platform=platform,
        draft_context=json.dumps(draft),
        strategy_context=json.dumps(strategy or {}),
        workspace_context=json.dumps(state.get("workspace") or {}),
        brand_kit_context=json.dumps(brand_kit)
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{brand_voice_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not brand_voice_prompt_v1.output_schema:
            raise ValueError("Brand Voice prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=brand_voice_prompt_v1.output_schema
        )
        
        # Platform Constraint Validation
        actual_char_count = len(output.revised_content)
        content_type = draft.get("content_type", "").upper()
        
        if platform.upper() == "X":
            if content_type != "THREAD" and actual_char_count > 280:
                raise AIValidationError(
                    f"Platform constraint violation: Revised X post exceeds 280 characters "
                    f"(actual: {actual_char_count})."
                )

        return {
            "optimized_content": output.revised_content,
            "brand_voice": output.model_dump()
        }

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Brand Voice Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Brand Voice Agent failed with unexpected error: {e}")
        raise
