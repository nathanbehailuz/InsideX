"""
Configuration settings for the InsideX API
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "InsideX API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///insider_trading.db"
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:8000",  # FastAPI docs
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # ML settings
    model_artifact_path: str = "app/ml/artifacts/model.joblib"
    features_config_path: str = "app/ml/artifacts/features.yaml"
    
    class Config:
        env_file = ".env"


settings = Settings()