import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings  # Note: pydantic-settings, not pydantic


class AppSettings(BaseSettings):
    """Application configuration loaded from environment variables.
    
    Priority: Environment Variables > .env file > Defaults
    """
    
    # ---------- APP METADATA ----------
    APP_NAME: str = "AI Contract Intelligence API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development | staging | production
    
    # ---------- PATHS (Auto-resolved) ----------
    # Base directory (project root)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "data"
    
    @property
    def ASSETS_DIR(self) -> Path:
        return self.BASE_DIR / "assets"
    
    @property
    def MODELS_DIR(self) -> Path:
        return self.BASE_DIR / "models"  # Agar models folder ho toh
    
    # ---------- REDIS / CELERY (CRITICAL FOR DOCKER) ----------
    # Default localhost is fine for local dev, Docker overrides via env vars
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Celery uses the same Redis instance
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL
    
    # ---------- ML / EMBEDDING CONFIG ----------
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # sentence-transformers
    HF_TOKEN: Optional[str] = None  # Hugging Face token for gated models
    
    # ---------- LOGGING ----------
    LOG_LEVEL: str = "INFO"
    
    class Config:
        # .env file se read karega. Docker Compose env vars override kar dega.
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Extra env vars ignore kar do taaki conflict na ho


# ---------- GLOBAL SINGLETON ----------
settings = AppSettings()

# ---------- OPTIONAL: SAFETY CHECKS ----------
# Ensure directories exist (optional but good practice)
if settings.ENVIRONMENT != "production":
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.ASSETS_DIR, exist_ok=True)