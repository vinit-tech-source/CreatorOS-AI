from contextlib import asynccontextmanager
import asyncio
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.core.rate_limit import limiter

from app.core.config import settings
from app.core.exception_handlers import (
    brand_kit_already_exists_handler,
    brand_kit_not_found_handler,
    email_exists_handler,
    inactive_user_handler,
    invalid_credentials_handler,
    invalid_status_transition_handler,
    invalid_token_handler,
    media_asset_not_found_handler,
    permission_denied_handler,
    post_not_found_handler,
    project_not_found_handler,
    project_slug_already_exists_handler,
    slug_exists_handler,
    social_account_already_exists_handler,
    social_account_not_found_handler,
    user_not_found_handler,
    username_exists_handler,
    workspace_not_found_handler,
    ai_provider_error_handler,
    ai_validation_error_handler,
)
from app.core.exceptions import (
    BrandKitAlreadyExistsError,
    BrandKitNotFoundError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidStatusTransitionError,
    InvalidTokenError,
    MediaAssetNotFoundError,
    PermissionDeniedError,
    PostNotFoundError,
    ProjectNotFoundError,
    ProjectSlugAlreadyExistsError,
    SlugAlreadyExistsError,
    SocialAccountAlreadyExistsError,
    SocialAccountNotFoundError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
    WorkspaceNotFoundError,
    AIProviderError,
    AIValidationError,
)
from app.core.logging import setup_logging
from app.core.redis import redis_manager
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.workspace import router as workspace_router
from app.api.brand_kit import router as brand_kit_router
from app.api.social_accounts import router as social_accounts_router
from app.api.projects import router as projects_router
from app.api.posts import router as posts_router
from app.api.media import router as media_router
from app.api.ai import router as ai_router
from app.api.content import router as content_router
from app.api.endpoints.oauth import router as oauth_router
from app.api.knowledge import router as knowledge_router
from app.api.automation import router as automation_router

setup_logging()


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    _log = logging.getLogger(__name__)

    # ── Dev auth bypass ──────────────────────────────────────────────────
    if settings.DEV_AUTH_BYPASS:
        _log.warning(
            "\n"
            "  ╔══════════════════════════════════════════════════════╗\n"
            "  ║  ⚠  DEVELOPMENT AUTH BYPASS ENABLED                 ║\n"
            "  ║     GET /api/v1/auth/dev-token is active.            ║\n"
            "  ║     NEVER use this in a production environment.      ║\n"
            "  ╚══════════════════════════════════════════════════════╝"
        )
    # ─────────────────────────────────────────────────────────────────────

    # Application startup
    await redis_manager.connect()
    
    # Initialize response caching
    from app.core.cache import init_cache
    init_cache()

    # Ensure upload directory exists
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Start background token refresh worker
    from app.workers.token_refresh_worker import token_refresh_worker_loop
    token_refresh_task = asyncio.create_task(
        token_refresh_worker_loop(), name="token_refresh_worker"
    )

    yield
    # Application shutdown
    token_refresh_task.cancel()
    await redis_manager.close()


# ─────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered social media content operations platform.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Exception Handlers
# ─────────────────────────────────────────────

app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(InactiveUserError, inactive_user_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_handler)
app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(EmailAlreadyExistsError, email_exists_handler)
app.add_exception_handler(UsernameAlreadyExistsError, username_exists_handler)
app.add_exception_handler(WorkspaceNotFoundError, workspace_not_found_handler)
app.add_exception_handler(SlugAlreadyExistsError, slug_exists_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(BrandKitNotFoundError, brand_kit_not_found_handler)
app.add_exception_handler(BrandKitAlreadyExistsError, brand_kit_already_exists_handler)
app.add_exception_handler(SocialAccountNotFoundError, social_account_not_found_handler)
app.add_exception_handler(SocialAccountAlreadyExistsError, social_account_already_exists_handler)
app.add_exception_handler(ProjectNotFoundError, project_not_found_handler)
app.add_exception_handler(ProjectSlugAlreadyExistsError, project_slug_already_exists_handler)
app.add_exception_handler(PostNotFoundError, post_not_found_handler)
app.add_exception_handler(InvalidStatusTransitionError, invalid_status_transition_handler)
app.add_exception_handler(MediaAssetNotFoundError, media_asset_not_found_handler)
app.add_exception_handler(AIProviderError, ai_provider_error_handler)
app.add_exception_handler(AIValidationError, ai_validation_error_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logger = logging.getLogger("app.main.global_exception_handler")
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected internal server error occurred.", "data": None},
    )

# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────

app.include_router(health_router, prefix=settings.API_V1_STR, tags=["System"])
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(workspace_router, prefix=settings.API_V1_STR)
app.include_router(brand_kit_router, prefix=settings.API_V1_STR)
app.include_router(social_accounts_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(posts_router, prefix=settings.API_V1_STR)
app.include_router(media_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(content_router, prefix=settings.API_V1_STR)
app.include_router(oauth_router, prefix=settings.API_V1_STR)
app.include_router(knowledge_router, prefix=settings.API_V1_STR)
app.include_router(automation_router, prefix=settings.API_V1_STR)

# ── Development auth bypass (conditional) ─────────────────────────────────
# This router is ONLY registered when DEV_AUTH_BYPASS=true.
# config.py already rejects that flag in production at import time.
if settings.DEV_AUTH_BYPASS:
    from app.api.dev_auth import router as dev_auth_router  # noqa: E402
    app.include_router(dev_auth_router, prefix=settings.API_V1_STR)

# ── Static file serving for uploaded media ────────────────────────────────
# Serves files from UPLOAD_DIR at /uploads/<storage_key>
# Must be mounted AFTER all API routers to avoid path conflicts.
_upload_path = Path(settings.UPLOAD_DIR)
_upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_upload_path)), name="uploads")
