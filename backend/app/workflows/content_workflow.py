"""
app/workflows/content_workflow.py

LangGraph workflow definition for CreatorOS AI content generation.
"""
from langgraph.graph import StateGraph, START, END

from app.workflows.state import ContentWorkflowState
from app.agents.strategy_agent import strategy_agent
from app.agents.trend_agent import trend_agent
from app.agents.research_agent import research_agent


def build_content_workflow() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    """
    workflow = StateGraph(ContentWorkflowState)
    
    workflow.add_node("strategy_agent", strategy_agent)
    workflow.add_node("trend_agent", trend_agent)
    workflow.add_node("research_agent", research_agent)
    
    workflow.add_edge(START, "strategy_agent")
    workflow.add_edge("strategy_agent", "trend_agent")
    workflow.add_edge("trend_agent", "research_agent")
    workflow.add_edge("research_agent", END)
    
    return workflow.compile()


# We can expose a compiled graph singleton if needed
content_graph = build_content_workflow()
