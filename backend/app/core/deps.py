"""
Dependency injection for FastAPI
"""

import os
import sys
from typing import Generator

# Add the project root to Python path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))

from database import InsiderTradingDB
from backend.app.core.config import settings


def resolve_database_path() -> str:
    """Resolve DATABASE_PATH; absolute paths (Modal Volume) used as-is."""
    if os.path.isabs(settings.DATABASE_PATH):
        return settings.DATABASE_PATH
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), settings.DATABASE_PATH)
    )


def get_database() -> Generator[InsiderTradingDB, None, None]:
    """
    Get database connection
    """
    db = InsiderTradingDB(resolve_database_path())
    try:
        yield db
    finally:
        # Database connections are handled within the InsiderTradingDB class
        pass
