import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/cubic_db"
    
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    REDIS_URL: str = "redis://localhost:6379"
    
    LOG_LEVEL: str = "INFO"
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
