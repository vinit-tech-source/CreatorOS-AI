"""
app/prompts/strategy.py

Prompts for the Strategy Agent.
"""
from app.prompts.base import PromptDefinition

strategy_prompt_v1 = PromptDefinition(
    prompt_id="strategy_agent",
    version="1.0.0",
    model="gemini",
    status="draft",
    system_instructions="You are an expert Social Media Strategist.",
    user_instructions="Develop a content strategy for {brand_name} on {platform}.",
)
