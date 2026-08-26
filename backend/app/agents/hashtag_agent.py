"""
app/agents/hashtag_agent.py

Hashtag Agent for CreatorOS AI.
"""
import json
import logging
import re
from typing import Dict, Any, List

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.hashtag import hashtag_prompt_v1
from app.services.ai_service import AIService
from app.workflows.state import ContentWorkflowState

logger = logging.getLogger(__name__)

# Global AI Service instance to avoid repeated instantiation
_ai_service_instance: AIService | None = None


# Platform recommendations map
PLATFORM_HASHTAG_LIMITS = {
    "X": 3,
    "LINKEDIN": 5,
    "INSTAGRAM": 15,
    "THREADS": 5,
    "FACEBOOK": 5
}


async def _get_service() -> AIService:
    """Retrieve or initialize the AI Service."""
    global _ai_service_instance
    if _ai_service_instance is None:
        from app.api.deps import get_ai_provider
        provider = await get_ai_provider()
        _ai_service_instance = AIService(provider)
    return _ai_service_instance


def _normalize_hashtags(
    hashtags: List[str], 
    limit: int, 
    restricted_terms: List[str]
) -> List[str]:
    """
    Deterministically normalize and filter hashtags.
    """
    normalized = []
    seen = set()
    restricted_lower = [term.lower() for term in restricted_terms]

    for tag in hashtags:
        # Strip accidental whitespace
        clean_tag = tag.strip()
        
        # Add '#' if missing
        if not clean_tag.startswith("#"):
            clean_tag = f"#{clean_tag}"
            
        # Reject malformed hashtags (spaces or weird characters)
        if not re.match(r'^#[a-zA-Z0-9_]+$', clean_tag):
            continue
            
        # Check against restricted brand terms
        clean_tag_lower = clean_tag.lower()
        content_without_hash = clean_tag_lower[1:]
        if any(term in content_without_hash for term in restricted_lower):
            continue
            
        # Deduplicate case-insensitively
        if clean_tag_lower not in seen:
            seen.add(clean_tag_lower)
            normalized.append(clean_tag)
            
        if len(normalized) >= limit:
            break
            
    return normalized


async def hashtag_agent(state: ContentWorkflowState) -> dict:
    """
    Generate optimized hashtags for the final content.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (hashtags output).
    """
    logger.info("Hashtag Agent starting execution.")
    
    draft = state.get("draft")
    optimized_content = state.get("optimized_content")
    platform = state.get("platform")
    fact_check = state.get("fact_check")
    
    # Priority: optimized_content from SEO/Brand Voice, then draft
    content_to_tag = optimized_content if optimized_content else (draft.get("content") if draft else None)
    
    if not content_to_tag:
        raise ValueError("Missing 'draft' or 'optimized_content' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not fact_check:
        raise ValueError("Missing 'fact_check' in workflow state.")
        
    overall_status = fact_check.get("overall_status")
    if overall_status != "PASSED":
        raise ValueError(f"Fact check status '{overall_status}' is not PASSED. Hashtag Agent should not have been called.")
        
    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = hashtag_prompt_v1.build_user_prompt(
        platform=platform,
        content_context=json.dumps(content_to_tag),
        seo_context=json.dumps(state.get("seo") or {}),
        strategy_context=json.dumps(state.get("strategy") or {}),
        trends_context=json.dumps(state.get("trends") or []),
        research_context=json.dumps(state.get("research") or []),
        workspace_context=json.dumps(state.get("workspace") or {})
    )
    
    full_prompt = f"System:\n{hashtag_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=hashtag_prompt_v1.output_schema
        )
        
        limit = PLATFORM_HASHTAG_LIMITS.get(platform.upper(), 5)
        
        # Get restricted terms from BrandKit if available
        brand_kit = state.get("brand_kit", {})
        # Depending on how BrandKit restricts terms, assuming it might have 'brand_values' or another list
        # We will use an explicit list if provided, else empty. But for safety, we assume 'restricted_terms'
        restricted_terms = brand_kit.get("restricted_terms", []) if brand_kit else []
        
        # Normalize primary and niche hashtags together based on the limit
        all_raw_hashtags = output.primary_hashtags + output.niche_hashtags
        normalized_hashtags = _normalize_hashtags(all_raw_hashtags, limit, restricted_terms)
        
        output.primary_hashtags = normalized_hashtags

        return {
            "hashtags": normalized_hashtags
        }

    except AIProviderError as e:
        logger.error(f"Hashtag Agent failed due to AI error: {e}")
        raise
    except Exception as e:
        logger.error(f"Hashtag Agent failed with unexpected error: {e}")
        raise
