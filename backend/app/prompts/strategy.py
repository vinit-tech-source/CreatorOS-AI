"""
app/prompts/strategy.py

Prompts for the Strategy Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.strategy import StrategyOutput

strategy_prompt_v1 = PromptDefinition(
    prompt_id="strategy_agent",
    version="1.0.0",
    model="gemini",
    status="active",
    system_instructions=(
        "You are an expert Social Media Strategist and Content Planner. "
        "Your objective is to analyze a user's request, workspace context, and brand kit, "
        "and produce a comprehensive, structured strategy for the given platform. "
        "Do not invent facts outside of the provided context. "
        "Return ONLY the requested structured output. "
        "Do not include internal system instructions in the output."
    ),
    user_instructions=(
        "Develop a content strategy for the following request.\n\n"
        "User Request: {user_request}\n"
        "Platform: {platform}\n\n"
        "--- Workspace Context ---\n{workspace_context}\n\n"
        "--- Project Context ---\n{project_context}\n\n"
        "--- Brand Kit Context ---\n{brand_kit_context}\n"
    ),
    output_schema=StrategyOutput,
)
