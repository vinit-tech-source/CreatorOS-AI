"""
app/agents/seo_agent.py

SEO Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.seo import seo_prompt_v1
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


async def seo_agent(state: ContentWorkflowState) -> dict:
    """
    Optimize the final content draft for SEO/discoverability.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (optimized_content and seo output).
    """
    logger.info("SEO Agent starting execution.")
    
    draft = state.get("draft")
    optimized_content = state.get("optimized_content")
    fact_check = state.get("fact_check")
    platform = state.get("platform")
    
    # Priority: optimized_content from Brand Voice, then draft
    content_to_optimize = optimized_content if optimized_content else (draft.get("content") if draft else None)
    
    if not content_to_optimize:
        raise ValueError("Missing 'draft' or 'optimized_content' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not fact_check:
        raise ValueError("Missing 'fact_check' in workflow state.")
        
    # Validation: Do not optimize if Fact Check FAILED
    overall_status = fact_check.get("overall_status")
    if overall_status == "FAILED":
        logger.warning("Fact Check FAILED. SEO Agent will bypass optimization.")
        return {
            "seo": {
                "optimized_content": content_to_optimize,
                "seo_score": 0.0,
                "primary_keywords": [],
                "secondary_keywords": [],
                "recommendations": ["Optimization blocked pending fact check review."],
                "changes": ["Skipped optimization due to FAILED fact check status."]
            }
        }
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = seo_prompt_v1.build_user_prompt(
        platform=platform,
        content_context=json.dumps(content_to_optimize),
        strategy_context=json.dumps(state.get("strategy") or {}),
        trends_context=json.dumps(state.get("trends") or []),
        research_context=json.dumps(state.get("research") or []),
        fact_check_context=json.dumps(fact_check)
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{seo_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not seo_prompt_v1.output_schema:
            raise ValueError("SEO prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=seo_prompt_v1.output_schema
        )
        
        # Platform Constraint Validation
        actual_char_count = len(output.optimized_content)
        content_type = draft.get("content_type", "").upper() if draft else ""
        
        if platform.upper() == "X":
            if content_type != "THREAD" and actual_char_count > 280:
                raise AIValidationError(
                    f"Platform constraint violation: SEO optimized X post exceeds 280 characters "
                    f"(actual: {actual_char_count})."
                )

        return {
            "optimized_content": output.optimized_content,
            "seo": output.model_dump(mode='json')
        }

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"SEO Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"SEO Agent failed with unexpected error: {e}")
        raise
