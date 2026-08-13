"""
app/agents/content_planner_agent.py

Content Planner Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.planner import planner_prompt_v1
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


async def content_planner_agent(state: ContentWorkflowState) -> dict:
    """
    Outline a highly structured content plan based on strategy, trends, and research.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (outline output).
    """
    logger.info("Content Planner Agent starting execution.")
    
    user_request = state.get("user_request")
    platform = state.get("platform")
    strategy = state.get("strategy")
    trends = state.get("trends", [])
    research = state.get("research", [])
    
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
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = planner_prompt_v1.build_user_prompt(
        user_request=user_request,
        platform=platform,
        strategy_context=json.dumps(strategy),
        trends_context=json.dumps(trends),
        research_context=json.dumps(research),
        workspace_context=json.dumps(state.get("workspace") or {}),
        brand_kit_context=json.dumps(state.get("brand_kit") or {})
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{planner_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not planner_prompt_v1.output_schema:
            raise ValueError("Planner prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=planner_prompt_v1.output_schema
        )
        
        # Return the dictionary portion to update state
        # The LangGraph state defines 'outline' as Optional[Dict[str, Any]]
        return {"outline": output.model_dump()}

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Content Planner Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Content Planner Agent failed with unexpected error: {e}")
        raise
