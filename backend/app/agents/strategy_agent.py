"""
app/agents/strategy_agent.py

Strategy Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.strategy import strategy_prompt_v1
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


async def strategy_agent(state: ContentWorkflowState) -> dict:
    """
    Determine the content strategy based on the input context.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (strategy output).
    """
    logger.info("Strategy Agent starting execution.")
    
    user_request = state.get("user_request")
    platform = state.get("platform")
    
    if not user_request:
        raise ValueError("Missing 'user_request' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = strategy_prompt_v1.build_user_prompt(
        user_request=user_request,
        platform=platform,
        workspace_context=json.dumps(state.get("workspace") or {}),
        project_context=json.dumps(state.get("project") or {}),
        brand_kit_context=json.dumps(state.get("brand_kit") or {})
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{strategy_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not strategy_prompt_v1.output_schema:
            raise ValueError("Strategy prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=strategy_prompt_v1.output_schema
        )
        
        # Return only the dictionary portion to update state
        return {"strategy": output.model_dump()}

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Strategy Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Strategy Agent failed with unexpected error: {e}")
        raise
