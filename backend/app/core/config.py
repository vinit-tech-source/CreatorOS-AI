import logging

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator
from typing import Self

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    PROJECT_NAME: str = "CreatorOS AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Runtime environment — used for safety guards
    # Values: "development" | "staging" | "production"
    ENVIRONMENT: str = "development"

    # ── Development Auth Bypass ───────────────────────────────────────────────
    # When true, exposes GET /auth/dev-token which issues a real JWT for a
    # deterministic dev@localhost identity WITHOUT interactive login.
    #
    # SAFETY: Automatically refused if ENVIRONMENT=production.
    # DEFAULT: false — must be explicitly enabled in .env.
    # ─────────────────────────────────────────────────────────────────────────
    DEV_AUTH_BYPASS: bool = False

    # CORS
    ALLOWED_ORIGINS: list[str] = []

    # Database
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = ""

    # Security config
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # MCP Configuration
    MCP_ENABLED: bool = True
    MCP_DEFAULT_TIMEOUT: int = 30
    MCP_MAX_TOOL_CALLS: int = 5
    MCP_LOG_TOOL_CALLS: bool = True
    
    # Provider Flags (Prepared for future MCP integration)
    # Optional: Research Provider Flags (MCP)
    YOUTUBE_ENABLED: bool = False
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_MAX_RESULTS: int = 10
    
    BLUESKY_ENABLED: bool = False
    BLUESKY_CLIENT_ID: str = ""
    BLUESKY_CLIENT_SECRET: str = ""
    BLUESKY_REDIRECT_URI: str = ""
    
    REDDIT_ENABLED: bool = False
    
    # RAG Settings
    RAG_ENABLED: bool = True
    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_MAX_CONTEXT_TOKENS: int = 4000
    RAG_MIN_SCORE: float = 0.5
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    
    GOOGLE_TRENDS_ENABLED: bool = False
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Encryption
    ENCRYPTION_KEY: str = ""

    # AI Configuration
    USE_MOCK_AI: bool = True  # When True, uses dynamic local dummy generator to preserve Gemini API quota
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_TIMEOUT: int = 60
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.7
    
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def _refuse_bypass_in_production(self) -> Self:
        """
        Safety guard: refuse to start if DEV_AUTH_BYPASS is enabled
        while ENVIRONMENT is set to production.
        Fail closed — never allow a bypass token endpoint in production.
        """
        if self.DEV_AUTH_BYPASS and self.ENVIRONMENT.lower() == "production":
            raise RuntimeError(
                "CRITICAL SAFETY VIOLATION: DEV_AUTH_BYPASS=true is not "
                "permitted when ENVIRONMENT=production. "
                "Set DEV_AUTH_BYPASS=false before deploying to production."
            )
        return self

    @model_validator(mode="after")
    def _check_production_config(self) -> Self:
        """
        Validate that all required production secrets and configurations are present.
        """
        if self.ENVIRONMENT.lower() == "production":
            if not self.SECRET_KEY or self.SECRET_KEY == "changeme_in_production":
                raise RuntimeError("CRITICAL SAFETY VIOLATION: SECRET_KEY must be set in production.")
            if not self.ENCRYPTION_KEY:
                raise RuntimeError("CRITICAL SAFETY VIOLATION: ENCRYPTION_KEY must be set in production.")
            if not self.DATABASE_URL:
                raise RuntimeError("CRITICAL SAFETY VIOLATION: DATABASE_URL must be set in production.")
            if not self.REDIS_URL:
                raise RuntimeError("CRITICAL SAFETY VIOLATION: REDIS_URL must be set in production.")
            if not self.GEMINI_API_KEY:
                raise RuntimeError("CRITICAL SAFETY VIOLATION: GEMINI_API_KEY must be set in production.")
            if "*" in self.ALLOWED_ORIGINS:
                raise RuntimeError("CRITICAL SAFETY VIOLATION: Wildcard ALLOWED_ORIGINS='*' is not permitted in production.")
        return self


settings = Settings()
