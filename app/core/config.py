import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    database_url: str = "postgresql+asyncpg://postgres:1234@localhost:5432/schedule_db"
    
    class Config:
        env_file = ".env"


settings = Settings()
