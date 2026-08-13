"""
app/api/deps.py

Reusable FastAPI dependency functions.

Provides:
  - Database session injection
  - Repository injections (User, Workspace)
  - Service injections (Auth, Workspace)
  - Bearer token extraction and validation (current user ID)
"""
import uuid
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import AsyncSessionLocal
from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.repositories.user_repository_interface import AbstractUserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.workspace_repository_interface import AbstractWorkspaceRepository
from app.repositories.brand_kit_repository import BrandKitRepository
from app.repositories.brand_kit_repository_interface import AbstractBrandKitRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.repositories.social_account_repository_interface import AbstractSocialAccountRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_repository_interface import AbstractProjectRepository
from app.repositories.post_repository import PostRepository
from app.repositories.post_repository_interface import AbstractPostRepository
from app.repositories.media_asset_repository import MediaAssetRepository
from app.repositories.media_asset_repository_interface import AbstractMediaAssetRepository
from app.services.auth_service import AuthService
from app.services.workspace_service import WorkspaceService
from app.services.brand_kit_service import BrandKitService
from app.services.social_account_service import SocialAccountService
from app.services.project_service import ProjectService
from app.services.post_service import PostService
from app.services.media_asset_service import MediaAssetService
from app.integrations.ai.base import AbstractAIProvider
from app.integrations.ai.gemini_client import GeminiClient
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

# OAuth2-compatible Bearer scheme — populates Swagger "Authorize" button
bearer_scheme = HTTPBearer(auto_error=True)


# ─────────────────────────────────────────────
# Database Session
# ─────────────────────────────────────────────

async def get_db():
    """Yield an async SQLAlchemy session, closing it after the request."""
    async with AsyncSessionLocal() as session:
        yield session


# ─────────────────────────────────────────────
# Repository
# ─────────────────────────────────────────────

async def get_user_repository(
    db=Depends(get_db),
) -> UserRepository:
    """Construct a UserRepository bound to the current request's DB session."""
    return UserRepository(db)


async def get_workspace_repository(
    db=Depends(get_db),
) -> AbstractWorkspaceRepository:
    """Construct a WorkspaceRepository bound to the current request's DB session."""
    return WorkspaceRepository(db)


# ─────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────

async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Construct an AuthService with the injected UserRepository."""
    return AuthService(repo)


async def get_workspace_service(
    repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceService:
    """Construct a WorkspaceService with the injected WorkspaceRepository."""
    return WorkspaceService(repo)


async def get_brand_kit_repository(
    db=Depends(get_db),
) -> AbstractBrandKitRepository:
    """Construct a BrandKitRepository bound to the current request's DB session."""
    return BrandKitRepository(db)


async def get_brand_kit_service(
    bk_repo: AbstractBrandKitRepository = Depends(get_brand_kit_repository),
    ws_repo: AbstractWorkspaceRepository = Depends(get_workspace_repository),
) -> BrandKitService:
    """Construct a BrandKitService with injected BrandKit and Workspace repositories."""
    return BrandKitService(brand_kit_repository=bk_repo, workspace_repository=ws_repo)


async def get_social_account_repository(
    db=Depends(get_db),
) -> AbstractSocialAccountRepository:
    """Construct a SocialAccountRepository bound to the current DB session."""
    return SocialAccountRepository(db)


async def get_social_account_service(
    sa_repo: AbstractSocialAccountRepository = Depends(get_social_account_repository),
    ws_repo: AbstractWorkspaceRepository = Depends(get_workspace_repository),
) -> SocialAccountService:
    """Construct a SocialAccountService with injected repos."""
    return SocialAccountService(
        social_account_repository=sa_repo, workspace_repository=ws_repo
    )


async def get_project_repository(
    db=Depends(get_db),
) -> AbstractProjectRepository:
    """Construct a ProjectRepository bound to the current DB session."""
    return ProjectRepository(db)


async def get_project_service(
    proj_repo: AbstractProjectRepository = Depends(get_project_repository),
    ws_repo: AbstractWorkspaceRepository = Depends(get_workspace_repository),
) -> ProjectService:
    """Construct a ProjectService with injected repos."""
    return ProjectService(
        project_repository=proj_repo, workspace_repository=ws_repo
    )


async def get_post_repository(
    db=Depends(get_db),
) -> AbstractPostRepository:
    """Construct a PostRepository bound to the current DB session."""
    return PostRepository(db)


async def get_post_service(
    post_repo: AbstractPostRepository = Depends(get_post_repository),
    proj_repo: AbstractProjectRepository = Depends(get_project_repository),
    ws_repo: AbstractWorkspaceRepository = Depends(get_workspace_repository),
) -> PostService:
    """Construct a PostService with injected repos."""
    return PostService(
        post_repository=post_repo,
        project_repository=proj_repo,
        workspace_repository=ws_repo,
    )


async def get_media_asset_repository(
    db=Depends(get_db),
) -> AbstractMediaAssetRepository:
    """Construct a MediaAssetRepository bound to the current DB session."""
    return MediaAssetRepository(db)


async def get_media_asset_service(
    media_repo: AbstractMediaAssetRepository = Depends(get_media_asset_repository),
    post_repo: AbstractPostRepository = Depends(get_post_repository),
    proj_repo: AbstractProjectRepository = Depends(get_project_repository),
    ws_repo: AbstractWorkspaceRepository = Depends(get_workspace_repository),
) -> MediaAssetService:
    """Construct a MediaAssetService with injected repos."""
    return MediaAssetService(
        media_repo=media_repo,
        post_repo=post_repo,
        project_repo=proj_repo,
        ws_repo=ws_repo,
    )


async def get_ai_provider() -> AbstractAIProvider:
    """Construct the configured AI provider."""
    return GeminiClient()


async def get_ai_service(
    provider: AbstractAIProvider = Depends(get_ai_provider),
) -> AIService:
    """Construct an AIService with injected provider."""
    return AIService(provider=provider)


# ─────────────────────────────────────────────
# Current User
# ─────────────────────────────────────────────

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> uuid.UUID:
    """
    Extract and validate the Bearer access token from the Authorization header.

    Returns:
        The authenticated user's UUID extracted from the token 'sub' claim.

    Raises:
        HTTP 401 if the token is missing, invalid, expired, or has the wrong type.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject: str | None = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing the 'sub' claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return uuid.UUID(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is not a valid UUID.",
            headers={"WWW-Authenticate": "Bearer"},
        )
