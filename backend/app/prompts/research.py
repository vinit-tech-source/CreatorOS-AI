"""
app/prompts/research.py

Prompts for the Research Agent.
"""
from app.prompts.base import PromptDefinition

research_prompt_v1 = PromptDefinition(
    prompt_id="research_agent",
    version="1.0.0",
    model="gemini",
    status="draft",
    system_instructions="You are an expert Content Researcher.",
    user_instructions="Research the latest trends for {topic}.",
)
