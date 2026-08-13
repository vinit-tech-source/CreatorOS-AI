"""
app/workflows/content_workflow.py

LangGraph workflow definition for CreatorOS AI content generation.
"""
from langgraph.graph import StateGraph, START, END

from app.workflows.state import ContentWorkflowState


def placeholder_node(state: ContentWorkflowState) -> dict:
    """
    A minimal placeholder node to verify the graph state.
    """
    # Append a metadata marker to indicate processing
    current_metadata = state.get("metadata", {})
    return {"metadata": {**current_metadata, "processed_by": "placeholder_node"}}


def build_content_workflow() -> StateGraph:
    """
    Build and compile the LangGraph workflow.
    """
    workflow = StateGraph(ContentWorkflowState)
    
    workflow.add_node("placeholder", placeholder_node)
    
    workflow.add_edge(START, "placeholder")
    workflow.add_edge("placeholder", END)
    
    return workflow.compile()


# We can expose a compiled graph singleton if needed
content_graph = build_content_workflow()
