"""
app/api/endpoints/oauth.py

Provider-neutral OAuth endpoints for connecting social accounts.
"""
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user_id, get_social_account_service
from app.services.social_account_service import SocialAccountService
from app.services.oauth.oauth_service import OAuthService
from app.schemas.oauth import OAuthAuthorization

router = APIRouter(prefix="/oauth", tags=["oauth"])


async def get_oauth_service(
    sa_service: SocialAccountService = Depends(get_social_account_service)
) -> OAuthService:
    """Dependency injection for OAuthService."""
    # In a real app, providers would be configured and registered here or at app startup.
    # For MVP foundation, we just instantiate the service.
    return OAuthService(social_account_service=sa_service)


@router.get(
    "/workspaces/{workspace_id}/social-accounts/{platform}/connect",
    response_model=OAuthAuthorization,
    summary="Start OAuth connection flow"
)
async def connect_social_account(
    workspace_id: uuid.UUID,
    platform: str,
    redirect_uri: str = Query(..., description="The callback URI for the OAuth flow"),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Initiate the OAuth flow for connecting a social account to a workspace.
    Requires workspace ownership (handled downstream, but implicitly protected by state).
    """
    # The OAuthService generates state tied to this workspace and platform
    return await oauth_service.get_authorization_url(
        workspace_id=workspace_id,
        platform=platform,
        redirect_uri=redirect_uri
    )


@router.get(
    "/{platform}/callback",
    status_code=status.HTTP_200_OK,
    summary="Handle OAuth callback"
)
async def oauth_callback(
    platform: str,
    state: str = Query(..., description="The state parameter from the OAuth provider"),
    code: str = Query(..., description="The authorization code from the OAuth provider"),
    redirect_uri: str = Query(..., description="The original redirect URI used to request the code"),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Handle the OAuth callback from the provider.
    Exchanges the code for tokens, retrieves the account profile, and securely creates
    the SocialAccount in the database.
    """
    await oauth_service.handle_callback(
        state=state,
        code=code,
        redirect_uri=redirect_uri,
        requesting_user_id=current_user_id
    )
    return {"status": "success", "message": f"Successfully connected {platform} account."}
