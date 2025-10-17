import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    database_url: str = "postgresql+asyncpg://postgres:1234@localhost:5432/schedule_db"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long"
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        # Support for multiple env files for easy database switching
        # Order matters: last file has priority
        env_file = ["env.development", "env.docker", "env.local", "env"]
        env_file_encoding = "utf-8"
        # Allow additional fields from env files
        extra = "ignore"


settings = Settings()
