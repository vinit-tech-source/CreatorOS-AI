from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CreatorOS AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = ""

    # Security config
    SECRET_KEY: str = "changeme_in_production"
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
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT: int = 60
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.7

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
