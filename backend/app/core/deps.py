"""
Dependency injection for FastAPI
"""

import os
import sys
from typing import Generator

# Add the parent directory to Python path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))

from database import InsiderTradingDB
from app.core.config import settings

def get_database() -> Generator[InsiderTradingDB, None, None]:
    """
    Get database connection
    """
    # Construct path relative to backend directory
    db_path = os.path.join(os.path.dirname(__file__), settings.DATABASE_PATH)
    db = InsiderTradingDB(db_path)
    try:
        yield db
    finally:
        # Database connections are handled within the InsiderTradingDB class
        pass