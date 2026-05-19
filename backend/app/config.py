from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Awash Bank Issue Tracker"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "awash-bank-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours (bank working day)
    DATABASE_URL: str = "sqlite+aiosqlite:///./awash_tracker.db"

    # Bank departments / teams
    DEPARTMENTS: list = [
        "Project Management",
        "Business Analysis",
        "Quality Assurance",
        "DevOps",
        "Development",
        "Security",
        "Infrastructure",
        "Core Banking",
        "Digital Banking",
        "Compliance",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
