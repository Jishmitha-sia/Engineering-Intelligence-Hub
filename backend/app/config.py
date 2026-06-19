"""
Configuration management for Engineering Intelligence Hub.

Uses Pydantic Settings for environment variable management and validation.
"""

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


def parse_csv_list(value: str) -> List[str]:
    """Parse comma-separated environment values into a list."""
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    # Application Settings
    APP_NAME: str = "Engineering Intelligence Hub"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Database Settings
    DATABASE_URL: str = (
        "postgresql+asyncpg://engineering_hub:engineering_hub@localhost:5432/engineering_hub"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # Authentication Settings
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PASSWORD_MIN_LENGTH: int = 8

    # Security Settings (comma-separated in .env)
    ALLOWED_HOSTS: str = "http://localhost:3000,http://127.0.0.1:3000"
    CORS_ORIGINS: str = "*"

    # File Upload Settings
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    ALLOWED_FILE_TYPES: str = ".pdf,.docx,.txt,.md"

    # AI/ML Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    DEFAULT_LLM: str = "qwen3:8b"
    EMBEDDING_DIMENSION: int = 384

    # Document Processing Settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    MAX_CHUNKS_PER_DOCUMENT: int = 10000

    # Search Settings
    DEFAULT_SEARCH_LIMIT: int = 20
    MAX_SEARCH_LIMIT: int = 100
    SIMILARITY_THRESHOLD: float = 0.5
    RERANK_TOP_K: int = 5

    # Rate Limiting Settings
    RATE_LIMIT_UNAUTHENTICATED: str = "10/minute"
    RATE_LIMIT_AUTHENTICATED: str = "100/minute"
    RATE_LIMIT_UPLOADS: str = "20/hour"

    # Monitoring Settings
    ENABLE_LOGGING: bool = True
    ENABLE_PROMETHEUS: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_RETENTION_DAYS: int = 7

    # Background Task Settings
    TASK_RETRY_MAX_ATTEMPTS: int = 3
    TASK_RETRY_DELAY: int = 5

    # GitHub Settings
    GITHUB_TIMEOUT: int = 300
    GITHUB_TEMP_DIR: str = "./tmp/github"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v

    @model_validator(mode="after")
    def validate_production_jwt_secret(self) -> "Settings":
        if (
            self.ENVIRONMENT == "production"
            and self.JWT_SECRET_KEY == "your-secret-key-change-this-in-production"
        ):
            raise ValueError("JWT_SECRET_KEY must be changed for production")
        return self

    @field_validator("UPLOAD_DIR", "GITHUB_TEMP_DIR")
    @classmethod
    def create_directories(cls, v: str) -> str:
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    @property
    def allowed_hosts_list(self) -> List[str]:
        return parse_csv_list(self.ALLOWED_HOSTS)

    @property
    def cors_origins_list(self) -> List[str]:
        return parse_csv_list(self.CORS_ORIGINS)

    @property
    def allowed_file_types_list(self) -> List[str]:
        return parse_csv_list(self.ALLOWED_FILE_TYPES)


settings = Settings()


def get_database_url() -> str:
    return settings.DATABASE_URL


def get_cors_origins() -> List[str]:
    if settings.ENVIRONMENT == "production":
        return settings.cors_origins_list
    # Explicit origins are required when allow_credentials=True.
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def is_development() -> bool:
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    return settings.ENVIRONMENT == "production"
