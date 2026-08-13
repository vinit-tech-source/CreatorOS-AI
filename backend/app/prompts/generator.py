"""
app/prompts/generator.py

Prompts for the Content Generator Agent.
"""
from app.prompts.base import PromptDefinition

generator_prompt_v1 = PromptDefinition(
    prompt_id="generator_agent",
    version="1.0.0",
    model="gemini",
    status="draft",
    system_instructions="You are an expert Copywriter.",
    user_instructions="Write a draft for {topic} based on the outline: {outline}.",
)
