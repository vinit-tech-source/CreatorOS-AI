from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exception_handlers import (
    brand_kit_already_exists_handler,
    brand_kit_not_found_handler,
    email_exists_handler,
    inactive_user_handler,
    invalid_credentials_handler,
    invalid_token_handler,
    permission_denied_handler,
    slug_exists_handler,
    user_not_found_handler,
    username_exists_handler,
    workspace_not_found_handler,
)
from app.core.exceptions import (
    BrandKitAlreadyExistsError,
    BrandKitNotFoundError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    PermissionDeniedError,
    SlugAlreadyExistsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
    WorkspaceNotFoundError,
)
from app.core.logging import setup_logging
from app.core.redis import redis_manager
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.workspace import router as workspace_router
from app.api.brand_kit import router as brand_kit_router

setup_logging()


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup
    await redis_manager.connect()
    yield
    # Application shutdown
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
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

# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────

app.include_router(health_router, prefix=settings.API_V1_STR, tags=["System"])
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(workspace_router, prefix=settings.API_V1_STR)
app.include_router(brand_kit_router, prefix=settings.API_V1_STR)
