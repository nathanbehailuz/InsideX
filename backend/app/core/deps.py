"""
Dependency injection for the FastAPI application
"""
from fastapi import HTTPException, Query
from typing import Optional
import sqlite3
import os
from app.core.config import settings


def get_database_connection():
    """Get database connection"""
    db_path = "insider_trading.db"  # Use existing database
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not found")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


class CommonQueryParams:
    """Common query parameters for pagination and filtering"""
    def __init__(
        self,
        limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
        offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    ):
        self.limit = limit
        self.offset = offset


class TradeQueryParams:
    """Query parameters for trade endpoints"""
    def __init__(
        self,
        ticker: Optional[str] = Query(default=None, description="Company ticker symbol"),
        insider_name: Optional[str] = Query(default=None, description="Insider name (partial match)"),
        trade_type: Optional[str] = Query(default=None, description="Trade type: Buy or Sell"),
        trade_flag: Optional[str] = Query(default=None, description="Trade flag (e.g., 10% Owner)"),
        date_from: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
        date_to: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
        min_value_usd: Optional[float] = Query(default=None, ge=0, description="Minimum trade value in USD"),
        limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
        offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    ):
        self.ticker = ticker
        self.insider_name = insider_name
        self.trade_type = trade_type
        self.trade_flag = trade_flag
        self.date_from = date_from
        self.date_to = date_to
        self.min_value_usd = min_value_usd
        self.limit = limit
        self.offset = offset