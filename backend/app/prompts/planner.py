"""
app/prompts/planner.py

Prompts for the Planner Agent.
"""
from app.prompts.base import PromptDefinition

planner_prompt_v1 = PromptDefinition(
    prompt_id="planner_agent",
    version="1.0.0",
    model="gemini",
    status="draft",
    system_instructions="You are an expert Content Planner.",
    user_instructions="Create an outline for {topic}.",
)
