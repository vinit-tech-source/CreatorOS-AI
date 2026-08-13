"""
app/prompts/seo.py

Prompts for the SEO Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.seo import SEOOutput

seo_prompt_v1 = PromptDefinition(
    prompt_id="seo_agent",
    version="1.0.0",
    model="gemini",
    status="active",
    system_instructions=(
        "You are an expert SEO Optimizer. "
        "Your objective is to optimize the discoverability of a given content draft. "
        "IMPORTANT RULES: "
        "1. Optimize the content for the selected platform without keyword stuffing. "
        "2. Preserve the core message, factual meaning, and research-backed claims exactly as they are. "
        "3. DO NOT invent facts, change statistics, dates, names, or alter claims. "
        "4. Avoid clickbait that misrepresents the content. "
        "5. Keep uncertain claims as uncertain, do not convert them to certain claims. "
        "6. Make changes to improve search relevance, headings, and keyword placement naturally. "
        "Return ONLY the requested structured output."
    ),
    user_instructions=(
        "Optimize the following content draft for SEO.\n\n"
        "Platform: {platform}\n\n"
        "--- Content to Optimize ---\n{content_context}\n\n"
        "--- Strategy ---\n{strategy_context}\n\n"
        "--- Trends ---\n{trends_context}\n\n"
        "--- Research ---\n{research_context}\n\n"
        "--- Fact Check Status ---\n{fact_check_context}\n"
    ),
    output_schema=SEOOutput,
)
