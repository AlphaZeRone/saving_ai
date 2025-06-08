from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets

class Settings(BaseSettings):
    # App config
    APP_NAME: str = "AI Help Saving and Money Learning"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    POSTGRES_USER: str = "devuser"
    POSTGRES_PASSWORD: str = "devpass"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "saving_ai_dev"
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode = "before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            schema = "postgresql",
            username = values.data.get("POSTGRES_USER"),
            password = values.data.get("POSTGRES_PASSWORD"),
            host = values.data.get("POSTGRES_SERVER"),
            port = int(values.data.get("POSTGRES_PORT")),
            path = values.data.get("POSTGRES_DB")
        )
    
    REDIS_URL: str = "redis:/localhost:6379/0"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = {
        "http://localhost:3000",
        "http://localhost:8000"
    }

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = True,
        extra = "ignore"
    )

settings = Settings()