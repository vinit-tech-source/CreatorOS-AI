"""
app/mcp/adapters/factory.py

Factory for creating Social MCP Adapters.
Routes each platform to its concrete adapter implementation.
Falls back to FakeSocialAdapter for unimplemented or disabled platforms.
"""
from typing import Optional
from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.adapters.fake_social_adapter import FakeSocialAdapter
from app.mcp.adapters.bluesky_social_adapter import BlueskySocialAdapter
from app.models.social_account import SocialAccount

from app.core.config import settings


def get_social_adapter(account: SocialAccount) -> SocialAdapter:
    """
    Instantiate the correct SocialAdapter for the given social account.

    In DEV_AUTH_BYPASS mode, always returns FakeSocialAdapter to allow testing
    without real API credentials.

    In production, routes each platform to its real adapter implementation.
    Falls back to FakeSocialAdapter for platforms without an adapter yet.
    """
    platform_str = account.platform.value if hasattr(account.platform, "value") else str(account.platform)
    platform_str = platform_str.upper()

    # Dev bypass — use fake adapter for all platforms
    if settings.DEV_AUTH_BYPASS:
        return FakeSocialAdapter(platform=platform_str)

    common_kwargs = {
        "access_token_encrypted": account.access_token_encrypted,
        "refresh_token_encrypted": account.refresh_token_encrypted,
        "platform_user_id": account.platform_user_id,
    }

    if platform_str == "BLUESKY":
        return BlueskySocialAdapter(
            access_token_encrypted=account.access_token_encrypted,
            refresh_token_encrypted=account.refresh_token_encrypted,
            platform_user_id=account.platform_user_id,
        )

    if platform_str == "X":
        from app.mcp.adapters.twitter_social_adapter import TwitterSocialAdapter
        return TwitterSocialAdapter(**common_kwargs)

    if platform_str == "LINKEDIN":
        from app.mcp.adapters.linkedin_social_adapter import LinkedInSocialAdapter
        return LinkedInSocialAdapter(**common_kwargs)

    if platform_str == "INSTAGRAM":
        from app.mcp.adapters.instagram_social_adapter import InstagramSocialAdapter
        return InstagramSocialAdapter(**common_kwargs)

    # Fallback for FACEBOOK, THREADS, and future platforms
    import logging
    logging.getLogger(__name__).warning(
        f"No real adapter implemented for platform '{platform_str}'. Using FakeSocialAdapter."
    )
    return FakeSocialAdapter(platform=platform_str)
