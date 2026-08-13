"""
app/workflows/content_workflow.py

LangGraph workflow definition for CreatorOS AI content generation.
"""
from langgraph.graph import StateGraph, START, END

from app.workflows.state import ContentWorkflowState
from app.agents.strategy_agent import strategy_agent


def build_content_workflow() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    """
    workflow = StateGraph(ContentWorkflowState)
    
    workflow.add_node("strategy_agent", strategy_agent)
    
    workflow.add_edge(START, "strategy_agent")
    workflow.add_edge("strategy_agent", END)
    
    return workflow.compile()


# We can expose a compiled graph singleton if needed
content_graph = build_content_workflow()
