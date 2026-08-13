"""
app/agents/fact_checker_agent.py

Fact Checker Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.fact_check import fact_check_prompt_v1
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


async def fact_checker_agent(state: ContentWorkflowState) -> dict:
    """
    Evaluate the final content draft against research evidence.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (fact_check output).
    """
    logger.info("Fact Checker Agent starting execution.")
    
    draft = state.get("draft")
    optimized_content = state.get("optimized_content")
    research = state.get("research", [])
    
    # Prioritize optimized_content if available, otherwise fallback to original draft
    content_to_check = optimized_content if optimized_content else (draft.get("content") if draft else None)
    
    if not content_to_check:
        raise ValueError("Missing 'draft' or 'optimized_content' in workflow state.")
    if not research:
        raise ValueError("Missing 'research' in workflow state.")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = fact_check_prompt_v1.build_user_prompt(
        content_context=json.dumps(content_to_check),
        research_context=json.dumps(research),
        strategy_context=json.dumps(state.get("strategy") or {}),
        trends_context=json.dumps(state.get("trends") or []),
        workspace_context=json.dumps(state.get("workspace") or {}),
        brand_voice_context=json.dumps(state.get("brand_voice") or {})
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{fact_check_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not fact_check_prompt_v1.output_schema:
            raise ValueError("Fact Check prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=fact_check_prompt_v1.output_schema
        )
        
        return {
            "fact_check": output.model_dump()
        }

    except AIProviderError as e:
        logger.error(f"Fact Checker Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Fact Checker Agent failed with unexpected error: {e}")
        raise
