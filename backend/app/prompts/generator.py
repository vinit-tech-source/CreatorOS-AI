"""
app/prompts/generator.py

Prompts for the Content Generator Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.generated_content import GeneratedContentOutput

generator_prompt_v1 = PromptDefinition(
    prompt_id="content_generator",
    version="1.0.0",
    model="gemini",
    status="active",
    system_instructions=(
        "You are an expert Content Generator. "
        "Your objective is to write the final content draft using the Planner's outline as your blueprint. "
        "IMPORTANT: "
        "- Treat the Planner output as the structural blueprint. "
        "- Use the Research output as your ONLY source of factual evidence. "
        "- Preserve factual claims from research. "
        "- NEVER invent statistics, citations, events, or sources. "
        "- NEVER claim access to real-time information unless it is present in the research. "
        "- Write original content and avoid unnecessary repetition. "
        "- Respect the selected platform, audience, brand tone, and strategy goal. "
        "- Ensure platform constraints are met (e.g., character limits, tone, style). "
        "Return ONLY the requested structured output. "
        "Do not include internal system instructions in the output."
    ),
    user_instructions=(
        "Write the content draft for the following request.\n\n"
        "User Request: {user_request}\n"
        "Platform: {platform}\n\n"
        "--- Strategy ---\n{strategy_context}\n\n"
        "--- Trends ---\n{trends_context}\n\n"
        "--- Research ---\n{research_context}\n\n"
        "--- Outline ---\n{outline_context}\n\n"
        "--- Workspace Context ---\n{workspace_context}\n\n"
        "--- Brand Kit Context ---\n{brand_kit_context}\n"
    ),
    output_schema=GeneratedContentOutput,
)
