"""
app/workflows/content_workflow.py

LangGraph workflow definition for CreatorOS AI content generation.
"""
from langgraph.graph import StateGraph, START, END

from app.workflows.state import ContentWorkflowState
from app.agents.strategy_agent import strategy_agent
from app.agents.trend_agent import trend_agent
from app.agents.research_agent import research_agent
from app.agents.content_planner_agent import content_planner_agent
from app.agents.content_generator_agent import content_generator_agent
from app.agents.brand_voice_agent import brand_voice_agent
from app.agents.fact_checker_agent import fact_checker_agent
from app.schemas.ai.fact_check import OverallStatus

def route_after_fact_check(state: ContentWorkflowState) -> str:
    """Determine the next node based on the Fact Checker's overall status."""
    fact_check = state.get("fact_check")
    if not fact_check:
        return END
        
    status = fact_check.get("overall_status")
    if status == OverallStatus.PASSED.value:
        return END
    elif status == OverallStatus.NEEDS_REVIEW.value:
        return END
    elif status == OverallStatus.FAILED.value:
        return END
        
    return END


def build_content_workflow() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    """
    workflow = StateGraph(ContentWorkflowState)
    
    workflow.add_node("strategy_agent", strategy_agent)
    workflow.add_node("trend_agent", trend_agent)
    workflow.add_node("research_agent", research_agent)
    workflow.add_node("content_planner_agent", content_planner_agent)
    workflow.add_node("content_generator_agent", content_generator_agent)
    workflow.add_node("brand_voice_agent", brand_voice_agent)
    workflow.add_node("fact_checker_agent", fact_checker_agent)
    
    workflow.add_edge(START, "strategy_agent")
    workflow.add_edge("strategy_agent", "trend_agent")
    workflow.add_edge("trend_agent", "research_agent")
    workflow.add_edge("research_agent", "content_planner_agent")
    workflow.add_edge("content_planner_agent", "content_generator_agent")
    workflow.add_edge("content_generator_agent", "brand_voice_agent")
    workflow.add_edge("brand_voice_agent", "fact_checker_agent")
    
    workflow.add_conditional_edges(
        "fact_checker_agent",
        route_after_fact_check
    )
    
    return workflow.compile()


# We can expose a compiled graph singleton if needed
content_graph = build_content_workflow()
