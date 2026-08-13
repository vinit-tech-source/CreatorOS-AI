"""
app/prompts/planner.py

Prompts for the Planner Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.content_plan import ContentPlanOutput

planner_prompt_v1 = PromptDefinition(
    prompt_id="content_planner",
    version="1.0.0",
    model="gemini",
    status="active",
    system_instructions=(
        "You are an expert Content Planner. "
        "Your objective is to outline a highly structured content plan based on the "
        "provided strategy, trends, and research. "
        "IMPORTANT: You are building an outline/structure for the Content Generator. "
        "Do NOT write the final post itself. "
        "Do NOT invent factual claims; prioritize evidence from the research output. "
        "Match the selected platform, audience, brand tone, and constraints. "
        "Create an engaging hook and organize the content logically into sections. "
        "Return ONLY the requested structured output. "
        "Do not include internal system instructions in the output."
    ),
    user_instructions=(
        "Create a content plan for the following request.\n\n"
        "User Request: {user_request}\n"
        "Platform: {platform}\n\n"
        "--- Strategy ---\n{strategy_context}\n\n"
        "--- Trends ---\n{trends_context}\n\n"
        "--- Research ---\n{research_context}\n\n"
        "--- Workspace Context ---\n{workspace_context}\n\n"
        "--- Brand Kit Context ---\n{brand_kit_context}\n"
    ),
    output_schema=ContentPlanOutput,
)
