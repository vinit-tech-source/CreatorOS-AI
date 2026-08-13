"""
app/agents/image_prompt_agent.py

Image Prompt Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.image_prompt import image_prompt_v1
from app.services.ai_service import AIService
from app.workflows.state import ContentWorkflowState

logger = logging.getLogger(__name__)

# Global AI Service instance to avoid repeated instantiation
_ai_service_instance: AIService | None = None

# Centralized configuration for recommended aspect ratios per platform
PLATFORM_ASPECT_RATIOS = {
    "X": "16:9",
    "LINKEDIN": "16:9",
    "INSTAGRAM": "1:1",
    "THREADS": "1:1",
    "FACEBOOK": "16:9"
}

ALLOWED_ASPECT_RATIOS = {"16:9", "1:1", "4:5", "9:16", "3:2", "2:3"}


async def _get_service() -> AIService:
    """Retrieve or initialize the AI Service."""
    global _ai_service_instance
    if _ai_service_instance is None:
        from app.api.deps import get_ai_provider
        provider = await get_ai_provider()
        _ai_service_instance = AIService(provider)
    return _ai_service_instance


async def image_prompt_agent(state: ContentWorkflowState) -> dict:
    """
    Generate an image prompt based on the final content.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (image_prompt output).
    """
    logger.info("Image Prompt Agent starting execution.")
    
    draft = state.get("draft")
    optimized_content = state.get("optimized_content")
    platform = state.get("platform")
    fact_check = state.get("fact_check")
    
    # Priority: optimized_content from SEO/Brand Voice, then draft
    content_to_prompt = optimized_content if optimized_content else (draft.get("content") if draft else None)
    
    if not content_to_prompt:
        raise ValueError("Missing 'draft' or 'optimized_content' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not fact_check:
        raise ValueError("Missing 'fact_check' in workflow state.")
        
    overall_status = fact_check.get("overall_status")
    if overall_status != "PASSED":
        raise ValueError(f"Fact check status '{overall_status}' is not PASSED. Image Prompt Agent should not have been called.")
        
    # Extract only safe visual context from Brand Kit
    brand_kit = state.get("brand_kit") or {}
    safe_brand_kit = {
        "brand_name": brand_kit.get("brand_name", ""),
        "primary_color": brand_kit.get("primary_color", ""),
        "secondary_color": brand_kit.get("secondary_color", ""),
        "accent_color": brand_kit.get("accent_color", ""),
        "default_tone": brand_kit.get("default_tone", "")
    }
    
    # Determine recommended aspect ratio
    recommended_aspect_ratio = PLATFORM_ASPECT_RATIOS.get(platform.upper(), "16:9")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = image_prompt_v1.build_user_prompt(
        platform=platform,
        recommended_aspect_ratio=recommended_aspect_ratio,
        content_context=json.dumps(content_to_prompt),
        brand_kit_context=json.dumps(safe_brand_kit),
        hashtags_context=json.dumps(state.get("hashtags") or []),
        strategy_context=json.dumps({
            "strategy": state.get("strategy") or {},
            "project": state.get("project") or {}
        })
    )
    
    full_prompt = f"System:\n{image_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=image_prompt_v1.output_schema
        )
        
        # Unsafe check (Basic mock check for now - a real system might use a safety moderation API)
        # Using a deterministic rejection based on certain keywords for illustration
        unsafe_keywords = ["malware", "explicit", "extremist", "bomb"]
        prompt_lower = output.prompt.lower()
        if any(keyword in prompt_lower for keyword in unsafe_keywords):
            raise AIValidationError("Unsafe prompt request detected.")
            
        # Aspect ratio validation
        if output.aspect_ratio not in ALLOWED_ASPECT_RATIOS:
            raise AIValidationError(f"Invalid aspect ratio '{output.aspect_ratio}'. Must be one of {ALLOWED_ASPECT_RATIOS}")

        return {
            "image_prompt": output.model_dump()
        }

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Image Prompt Agent failed due to AI/validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Image Prompt Agent failed with unexpected error: {e}")
        raise
