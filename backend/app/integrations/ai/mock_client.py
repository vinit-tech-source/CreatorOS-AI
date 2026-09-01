"""
app/integrations/ai/mock_client.py

Mock AI Provider for development and testing.
Returns intelligent, context-aware dummy responses without calling external APIs (Gemini/Groq),
preserving API quota and allowing offline testing.
"""
import re
import logging
from typing import Any, Type

from pydantic import BaseModel
from app.integrations.ai.base import AbstractAIProvider, T

logger = logging.getLogger(__name__)


class MockAIClient(AbstractAIProvider):
    """
    Mock AI Provider that returns realistic dummy social media content
    without making external API requests.
    """

    def __init__(self, model: str = "mock-creator-ai-v1") -> None:
        self._model = model
        logger.info("MockAIClient active. External Gemini API calls are bypassed to save API quota.")

    def model_name(self) -> str:
        return self._model

    def _extract_field(self, prompt: str, field_name: str, default: str = "") -> str:
        match = re.search(rf"{field_name}:\s*([^\n\r]+)", prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return default

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate contextual dummy text based on prompt keywords.
        """
        platform = "social media"
        for p in ["Twitter", "X", "LinkedIn", "Instagram", "TikTok", "YouTube", "Facebook"]:
            if p.lower() in prompt.lower():
                platform = p
                break

        # Extract core topic if available
        topic_match = re.search(r'prompt:\s*"([^"]+)"', prompt, re.IGNORECASE)
        topic = topic_match.group(1) if topic_match else "growing your audience"

        if "Twitter" in platform or "X" in platform:
            return (
                f"Most creators overcomplicate {topic}.\n\n"
                f"Here is the 3-step playbook that actually works:\n"
                f"1. Focus on high-signal ideas\n"
                f"2. Engage with 10 peers daily\n"
                f"3. Iterate based on analytics\n\n"
                f"Which step are you prioritizing this week? 👇"
            )
        elif "LinkedIn" in platform:
            return (
                f"The biggest mistake I see professionals make with {topic}:\n\n"
                f"They focus on output instead of outcome.\n\n"
                f"Here are 3 frameworks that changed my perspective:\n"
                f"• Consistency beats sporadic brilliance every time.\n"
                f"• Build assets, not just one-off tasks.\n"
                f"• Authenticity will always outlast trends.\n\n"
                f"What has been your biggest learning curve recently? Let's discuss below."
            )
        else:
            return (
                f"Here is the secret formula to master {topic} in 2026! 🚀\n\n"
                f"✨ 1. Define your core value proposition\n"
                f"✨ 2. Build in public and share raw progress\n"
                f"✨ 3. Double down on what works\n\n"
                f"Save this for your next creation session! 🔖"
            )

    async def generate_structured(
        self, prompt: str, response_schema: Type[T], **kwargs: Any
    ) -> T:
        """
        Generate realistic structured mock responses matching the requested Pydantic schema.
        """
        field_names = set(response_schema.model_fields.keys())

        # If schema is GeneratePostResponse (title, caption, hashtags)
        if {"title", "caption", "hashtags"}.issubset(field_names):
            platform = self._extract_field(prompt, "for", "social media")
            concept = self._extract_field(prompt, "Topic/Concept", "scaling your creative work")
            tone = self._extract_field(prompt, "Tone", "Professional")
            goal = self._extract_field(prompt, "Goal", "Grow audience")

            # Clean topic
            topic_clean = re.sub(r'\(Location:[^)]+\)', '', concept).strip()
            if len(topic_clean) > 40:
                topic_short = topic_clean[:35].rsplit(' ', 1)[0]
            else:
                topic_short = topic_clean or "Growing Your Audience"

            # Check if location is mentioned
            loc_match = re.search(r'Location:\s*([^\)]+)', concept, re.IGNORECASE)
            location = loc_match.group(1).strip() if loc_match else ""

            # Dynamic Title
            if "viral" in goal.lower() or "provocative" in tone.lower():
                title = f"The Unspoken Truth About {topic_short}"
            elif "educat" in goal.lower() or "how" in concept.lower():
                title = f"How to Master {topic_short} in 2026"
            else:
                title = f"The 3-Step Strategy for {topic_short}"

            # Dynamic Caption tailored by platform limit
            if any(x in platform.lower() for x in ["twitter", "x"]):
                # Keep under 260 chars for X/Twitter
                loc_text = f" from {location.split(',')[0]}" if location else ""
                caption = (
                    f"Most creators fail at {topic_short} because they lack a system{loc_text}.\n\n"
                    f"The 3-step formula:\n"
                    f"1. Hook attention in 3s\n"
                    f"2. Give 80% actionable value\n"
                    f"3. End with 1 clear action\n\n"
                    f"Which step do you focus on today? 👇"
                )
            elif "linkedin" in platform.lower():
                caption = (
                    f"A lot of creators struggle with {topic_short}.\n\n"
                    f"After analyzing hundreds of successful case studies, here are 3 rules that never fail:\n\n"
                    f"1. Clarity beats complexity — if a 12-year-old can't understand it, rephrase.\n"
                    f"2. Engagement is a two-way street — reply to comments like they are real conversations.\n"
                    f"3. Consistency builds trust faster than sporadic viral hits.\n\n"
                    f"What is the single most valuable lesson you've learned on this journey? Share your thoughts."
                )
            else:
                caption = (
                    f"Stop scrolling! Here is everything you need to know about {topic_short} 🚀\n\n"
                    f"📌 Rule 1: Master the opening hook.\n"
                    f"📌 Rule 2: Provide undeniable value in the first 10 seconds.\n"
                    f"📌 Rule 3: Always give your audience a reason to save and share.\n\n"
                    f"Save this post so you don't lose it later! 🔖"
                )

            # Dynamic hashtags
            base_tags = ["creator", "growth", "strategy"]
            # Add topic words as tags
            words = [re.sub(r'[^a-zA-Z0-9]', '', w).lower() for w in topic_clean.split() if len(w) >= 4]
            unique_tags = []
            for w in words[:2] + base_tags:
                if w and w not in unique_tags:
                    unique_tags.append(w)

            if location:
                city_tag = re.sub(r'[^a-zA-Z0-9]', '', location.split(',')[0]).lower()
                if city_tag and city_tag not in unique_tags:
                    unique_tags.insert(0, city_tag)

            return response_schema(
                title=title,
                caption=caption,
                hashtags=unique_tags[:5]
            )

        # Handle TestStructuredResponse
        if {"summary", "sentiment"}.issubset(field_names):
            return response_schema(
                summary="Development test generation successful (Mock Provider).",
                sentiment="Positive"
            )

        # Generic fallback for any other schema
        dummy_data = {}
        for field, info in response_schema.model_fields.items():
            ann = str(info.annotation)
            if "str" in ann:
                dummy_data[field] = f"Mock {field}"
            elif "int" in ann:
                dummy_data[field] = 100
            elif "float" in ann:
                dummy_data[field] = 95.5
            elif "bool" in ann:
                dummy_data[field] = True
            elif "list" in ann:
                dummy_data[field] = ["sample-1", "sample-2"]
            elif "dict" in ann:
                dummy_data[field] = {"key": "value"}
            else:
                dummy_data[field] = None

        return response_schema(**dummy_data)
