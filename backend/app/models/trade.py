"""
Trade-related Pydantic models
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Trade(BaseModel):
    """Individual trade record"""
    id: int
    trade_flag: Optional[str] = None
    filing_date: Optional[str] = None
    trade_date: Optional[str] = None
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    insider_name: Optional[str] = None
    title: Optional[str] = None
    trade_type: Optional[str] = None
    price: Optional[float] = None
    qty: Optional[int] = None
    owned: Optional[int] = None
    delta_own: Optional[int] = None
    value: Optional[float] = None
    performance_1d: Optional[float] = None
    performance_1w: Optional[float] = None
    performance_1m: Optional[float] = None
    performance_6m: Optional[float] = None
    scraped_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TradeQuery(BaseModel):
    """Query parameters for trade search"""
    ticker: Optional[str] = None
    insider_name: Optional[str] = None
    trade_type: Optional[str] = None
    trade_flag: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_value_usd: Optional[float] = None
    limit: Optional[int] = Field(default=50, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)

class TradeResponse(BaseModel):
    """Response model for trade queries"""
    trades: List[Trade]
    total: int
    limit: int
    offset: int
