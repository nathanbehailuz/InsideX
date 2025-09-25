"""
Application configuration settings
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "InsideX"
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    
    # Database settings
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "../../insider_trading.db")
    
    # ML settings
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "app/ml/artifacts/model.joblib")
    ML_FEATURES_PATH: str = os.getenv("ML_FEATURES_PATH", "app/ml/artifacts/features.yaml")
    
    # Pagination defaults
    DEFAULT_LIMIT: int = 50
    MAX_LIMIT: int = 1000
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()