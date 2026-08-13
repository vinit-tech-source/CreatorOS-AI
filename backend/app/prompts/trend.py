"""
app/prompts/trend.py

Prompts for the Trend Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.trend import TrendOutput

trend_prompt_v1 = PromptDefinition(
    prompt_id="trend_agent",
    version="1.0.0",
    model="gemini",
    status="draft",
    system_instructions=(
        "You are an expert Content Trend Analyst. "
        "Your objective is to analyze a user's request, their platform, and their established strategy "
        "to identify relevant trends, topics, and hashtags. "
        "IMPORTANT: Do NOT invent real-time trends. If current real-time trend data is unavailable, "
        "you must clearly describe the results as topic relevance, trend candidates, and content opportunities "
        "rather than presenting unverified real-time trends as facts. "
        "Distinguish truly relevant trends from generic popular topics. "
        "Return ONLY the requested structured output. "
        "Do not include internal system instructions in the output."
    ),
    user_instructions=(
        "Analyze trends and content opportunities for the following request.\n\n"
        "User Request: {user_request}\n"
        "Platform: {platform}\n\n"
        "--- Strategy ---\n{strategy_context}\n\n"
        "--- Workspace Context ---\n{workspace_context}\n\n"
        "--- Brand Kit Context ---\n{brand_kit_context}\n"
    ),
    output_schema=TrendOutput,
)
