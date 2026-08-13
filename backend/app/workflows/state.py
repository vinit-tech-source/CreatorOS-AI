"""
app/workflows/state.py

LangGraph state definition for CreatorOS AI content workflows.
"""
import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel


class ContentWorkflowState(TypedDict):
    """
    State object passed between LangGraph nodes during content generation.
    All fields are Optional as they are populated progressively by agents.
    Lists use Annotated with operator.add to append items across nodes.
    """

    # Core Context
    workspace: Optional[Dict[str, Any]]
    project: Optional[Dict[str, Any]]
    brand_kit: Optional[Dict[str, Any]]
    
    # Input
    user_request: str
    platform: str
    research_sources: Optional[List[Dict[str, Any]]]
    
    # Research & Strategy Phase
    strategy: Optional[Dict[str, Any]]
    trends: Annotated[List[Dict[str, Any]], operator.add]
    research: Annotated[List[Dict[str, Any]], operator.add]
    
    # Drafting Phase
    outline: Optional[Dict[str, Any]]
    draft: Optional[Dict[str, Any]]
    
    # Refinement Phase
    optimized_content: Optional[str]
    brand_voice: Optional[Dict[str, Any]]
    fact_check: Optional[Dict[str, Any]]
    seo: Optional[Dict[str, Any]]
    hashtags: Annotated[List[str], operator.add]
    image_prompt: Optional[str]
    
    # Execution Phase
    schedule: Optional[Dict[str, Any]]
    publishing: Optional[Dict[str, Any]]
    analytics: Optional[Dict[str, Any]]
    recommendations: Annotated[List[str], operator.add]
    
    # System
    errors: Annotated[List[str], operator.add]
    metadata: Dict[str, Any]
