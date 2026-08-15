"""
Application configuration settings
"""

import json
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_host_list(raw: str) -> List[str]:
    value = raw.strip()
    if not value:
        return []
    if value.startswith("["):
        return list(json.loads(value))
    return [h.strip() for h in value.split(",") if h.strip()]


class Settings(BaseSettings):
    """Application settings (env-overridable for Modal / local)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OpenSignal"

    # CORS — env ALLOWED_HOSTS: comma-separated or JSON list, e.g.
    # ALLOWED_HOSTS=https://insidex.vercel.app,http://localhost:3000
    # Stored as str so pydantic-settings does not force JSON-only list decoding.
    allowed_hosts: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="ALLOWED_HOSTS",
    )

    # Optional regex for preview deployments (e.g. https://.*\\.vercel\\.app)
    ALLOWED_ORIGIN_REGEX: Optional[str] = None

    # Database — absolute path on Modal Volume (/data/insider_trading.db)
    DATABASE_PATH: str = "../../insider_trading.db"

    # ML artifacts — directory on Modal Volume (/data/ml)
    ML_ARTIFACTS_DIR: str = "app/ml/artifacts"
    ML_MODEL_PATH: str = "app/ml/artifacts/model.joblib"
    ML_FEATURES_PATH: str = "app/ml/artifacts/features.yaml"

    # Pagination defaults
    DEFAULT_LIMIT: int = 50
    MAX_LIMIT: int = 1000

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        return _parse_host_list(self.allowed_hosts)


settings = Settings()
