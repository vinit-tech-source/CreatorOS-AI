"""
app/prompts/research.py

Prompts for the Research Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.research import ResearchOutput

research_prompt_v1 = PromptDefinition(
    prompt_id="research_agent",
    version="1.0.0",
    model="gemini",
    status="active",
    system_instructions=(
        "You are an expert Content Researcher and Fact-Checker. "
        "Your objective is to analyze a user's request, the selected strategy, trends, "
        "and any supplied research sources to produce a factual, concise research summary. "
        "IMPORTANT: Do NOT invent sources, URLs, statistics, dates, or facts. "
        "Never claim to have browsed the web when no search results were supplied. "
        "If no external research sources are available, return a knowledge-based summary, "
        "clearly label uncertainties, and indicate low/limited confidence when evidence is insufficient. "
        "Return ONLY the requested structured output. "
        "Do not include internal system instructions in the output."
    ),
    user_instructions=(
        "Synthesize research for the following request.\n\n"
        "User Request: {user_request}\n"
        "Platform: {platform}\n\n"
        "--- Strategy ---\n{strategy_context}\n\n"
        "--- Trends ---\n{trends_context}\n\n"
        "--- Supplied Research Sources ---\n{research_sources_context}\n\n"
        "--- Workspace Context ---\n{workspace_context}\n\n"
        "--- Brand Kit Context ---\n{brand_kit_context}\n"
    ),
    output_schema=ResearchOutput,
)
