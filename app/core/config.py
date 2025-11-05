import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""
    database_url: str = "postgresql+asyncpg://postgres:1234@localhost:5432/schedule_db"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long"
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Admin basic-auth credentials (for non-Google admin login)
    ADMIN_USERNAME: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_FIRST_NAME: Optional[str] = None
    ADMIN_LAST_NAME: Optional[str] = None

    # CORS
    # Comma-separated list of allowed origins, required when allow_credentials=True
    # Defaults target localhost in common cases (docker/nginx on :80)
    CORS_ALLOW_ORIGINS: str = (
        "http://localhost,http://localhost:80,"
        "http://127.0.0.1,http://127.0.0.1:80"
    )
    
    class Config:
        # In Docker-first setup we rely on real environment variables provided
        # by docker-compose (env_file) and do not auto-load local files.
        # Keeping extra=ignore to tolerate unexpected vars.
        extra = "ignore"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in (self.CORS_ALLOW_ORIGINS or "").split(",") if o.strip()]


settings = Settings()
