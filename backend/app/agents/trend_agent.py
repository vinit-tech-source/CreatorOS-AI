"""
app/agents/trend_agent.py

Trend Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.trend import trend_prompt_v1
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


async def trend_agent(state: ContentWorkflowState) -> dict:
    """
    Analyze and identify content trends based on strategy and context.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (trends output).
    """
    logger.info("Trend Agent starting execution.")
    
    user_request = state.get("user_request")
    platform = state.get("platform")
    strategy = state.get("strategy")
    
    if not user_request:
        raise ValueError("Missing 'user_request' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not strategy:
        raise ValueError("Missing 'strategy' in workflow state.")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = trend_prompt_v1.build_user_prompt(
        user_request=user_request,
        platform=platform,
        strategy_context=json.dumps(strategy),
        workspace_context=json.dumps(state.get("workspace") or {}),
        brand_kit_context=json.dumps(state.get("brand_kit") or {})
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{trend_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not trend_prompt_v1.output_schema:
            raise ValueError("Trend prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=trend_prompt_v1.output_schema
        )
        
        # Return the dictionary portion to update state
        # The LangGraph state defines 'trends' as Annotated[List[Dict[str, Any]], operator.add]
        # We append a single item (the dictionary containing all TrendOutput fields) to this list.
        return {"trends": [output.model_dump(mode='json')]}

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Trend Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Trend Agent failed with unexpected error: {e}")
        raise
