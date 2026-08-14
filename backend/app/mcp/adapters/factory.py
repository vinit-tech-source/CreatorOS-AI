"""
app/mcp/adapters/factory.py

Factory for creating Social MCP Adapters.
"""
from typing import Optional
from app.mcp.adapters.social_base import SocialAdapter
from app.mcp.adapters.fake_social_adapter import FakeSocialAdapter
from app.mcp.adapters.bluesky_social_adapter import BlueskySocialAdapter
from app.models.social_account import SocialAccount

def get_social_adapter(account: SocialAccount) -> SocialAdapter:
    """
    Instantiate the correct SocialAdapter for the given account.
    Passes encrypted tokens down to the adapter securely.
    """
    platform_str = account.platform.value if hasattr(account.platform, 'value') else str(account.platform)
    platform_str = platform_str.upper()
    
    if platform_str == "BLUESKY":
        return BlueskySocialAdapter(
            access_token_encrypted=account.access_token_encrypted,
            refresh_token_encrypted=account.refresh_token_encrypted,
            platform_user_id=account.platform_user_id
        )
        
    # Default to fake adapter for unimplemented platforms during foundation phase
    return FakeSocialAdapter(platform=platform_str)
