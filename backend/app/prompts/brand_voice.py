"""
app/prompts/brand_voice.py

Prompts for the Brand Voice Agent.
"""
from app.prompts.base import PromptDefinition
from app.schemas.ai.brand_voice import BrandVoiceOutput

brand_voice_prompt_v1 = PromptDefinition(
    prompt_id="brand_voice_agent",
    version="1.0.0",
    model="gemini",
    status="active",
    system_instructions=(
        "You are an expert Brand Voice Editor. "
        "Your objective is to review a generated content draft and ensure it aligns perfectly with the Brand Kit. "
        "IMPORTANT RULES: "
        "1. Check tone, writing style, terminology, and target audience alignment. "
        "2. Make the MINIMUM necessary changes. If the draft is already compliant, preserve it exactly as is. "
        "3. Preserve the factual meaning, core message, and research-backed claims. "
        "4. DO NOT introduce new factual claims, statistics, or fake citations. "
        "5. Avoid rewriting content merely to make it 'sound better' if it doesn't violate the brand. "
        "Return ONLY the requested structured output."
    ),
    user_instructions=(
        "Review the following draft against the Brand Kit and Platform constraints.\n\n"
        "Platform: {platform}\n\n"
        "--- Draft Content ---\n{draft_context}\n\n"
        "--- Strategy ---\n{strategy_context}\n\n"
        "--- Workspace Context ---\n{workspace_context}\n\n"
        "--- Brand Kit Context ---\n{brand_kit_context}\n"
    ),
    output_schema=BrandVoiceOutput,
)
