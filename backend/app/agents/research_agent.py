"""
app/agents/research_agent.py

Research Agent for CreatorOS AI.
"""
import json
import logging
from typing import Dict, Any

from app.core.exceptions import AIProviderError, AIValidationError
from app.prompts.research import research_prompt_v1
from app.services.ai_service import AIService
from app.workflows.state import ContentWorkflowState
from app.services.research_retrieval_service import ResearchRetrievalService
from app.mcp.client.client import get_default_mcp_client
from app.services.rag_context_service import RAGContextService

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


async def research_agent(state: ContentWorkflowState) -> dict:
    """
    Synthesize research based on user request, strategy, trends, and supplied sources.
    
    Args:
        state: The current LangGraph workflow state.
        
    Returns:
        dict: The state updates (research output).
    """
    logger.info("Research Agent starting execution.")
    
    user_request = state.get("user_request")
    platform = state.get("platform")
    strategy = state.get("strategy")
    trends = state.get("trends", [])
    
    if not user_request:
        raise ValueError("Missing 'user_request' in workflow state.")
    if not platform:
        raise ValueError("Missing 'platform' in workflow state.")
    if not strategy:
        raise ValueError("Missing 'strategy' in workflow state.")
    if not trends:
        raise ValueError("Missing 'trends' in workflow state.")
        
    # 1. MCP Research Retrieval
    retrieval_service = ResearchRetrievalService(get_default_mcp_client())
    
    # We'll build a controlled query from the user request
    # and select platforms from configuration (hardcoded to standard 3 for this foundation)
    platforms_to_search = ["youtube", "bluesky", "reddit"]
    
    # Ensure research_sources is initialized in state
    if state.get("research_sources") is None:
        state["research_sources"] = []
        
    try:
        sources, metadata = await retrieval_service.search_research_sources(
            query=user_request,
            platforms=platforms_to_search,
            max_results=15
        )
        # Update state with the normalized research items
        state["research_sources"].extend(sources)
        logger.info(f"Research retrieval complete: {len(sources)} items returned. Metadata: {metadata}")
    except Exception as e:
        logger.error(f"Research retrieval failed entirely: {str(e)}")
        # We record the error but don't fail the agent if we have enough context from Strategy/Trends
        # Or we could raise depending on strictness. The prompt says "Raise a controlled research retrieval exception"
        # "If all providers fail: Raise a controlled research retrieval exception."
        from app.mcp.exceptions.exceptions import MCPProviderError
        if isinstance(e, MCPProviderError):
            raise
        raise MCPProviderError(f"Research retrieval failed: {str(e)}")

    # 2. Workspace Knowledge (RAG Retrieval)
    workspace_id = state.get("workspace", {}).get("id")
    if workspace_id:
        # Construct focused query from user request and strategy
        content_goal = strategy.get("content_goal", "")
        rag_query = f"{user_request} {content_goal}".strip()
        
        rag_service = RAGContextService()
        workspace_context = await rag_service.retrieve_agent_context(
            query=rag_query,
            workspace_id=str(workspace_id),
            top_k=5
        )
        state["rag_context"] = workspace_context
        logger.info(f"RAG retrieval complete: {len(workspace_context)} workspace chunks found.")

    ai_service = await _get_service()

    # Build the prompt using the context from state
    prompt_text = research_prompt_v1.build_user_prompt(
        user_request=user_request,
        platform=platform,
        strategy_context=json.dumps(strategy),
        trends_context=json.dumps(trends),
        research_sources_context=json.dumps(state.get("research_sources") or []),
        workspace_rag_context=json.dumps(state.get("rag_context") or []),
        workspace_context=json.dumps(state.get("workspace") or {}),
        brand_kit_context=json.dumps(state.get("brand_kit") or {})
    )
    
    # Combine system and user instructions
    full_prompt = f"System:\n{research_prompt_v1.system_instructions}\n\nUser:\n{prompt_text}"

    try:
        if not research_prompt_v1.output_schema:
            raise ValueError("Research prompt is missing an output_schema.")
            
        output = await ai_service.generate_structured(
            prompt=full_prompt,
            response_schema=research_prompt_v1.output_schema
        )
        
        # Return the dictionary portion to update state
        update_dict = {"research": [output.model_dump()]}
        if state.get("rag_context") is not None:
            update_dict["rag_context"] = state["rag_context"]
        if state.get("research_sources") is not None:
            update_dict["research_sources"] = state["research_sources"]
            
        return update_dict

    except (AIProviderError, AIValidationError) as e:
        logger.error(f"Research Agent failed due to AI error: {e}")
        # Re-raise to allow the workflow retry mechanism or supervisor to handle it
        raise
    except Exception as e:
        logger.error(f"Research Agent failed with unexpected error: {e}")
        raise
