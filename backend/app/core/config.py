from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "CreatorOS AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database and Redis dummy values for now
    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
