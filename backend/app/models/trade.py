"""
Pydantic models for insider trading data
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TradeBase(BaseModel):
    """Base trade model with core fields"""
    trade_flag: Optional[str] = Field(None, description="Trade flag (e.g., '10% Owner')")
    filing_date: Optional[str] = Field(None, description="Filing date (YYYY-MM-DD)")
    trade_date: Optional[str] = Field(None, description="Trade execution date (YYYY-MM-DD)")
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")
    insider_name: str = Field(..., description="Insider/executive name")
    title: Optional[str] = Field(None, description="Insider's title/role")
    trade_type: str = Field(..., description="Trade type: Buy or Sell")
    price: Optional[float] = Field(None, ge=0, description="Trade price per share")
    qty: Optional[int] = Field(None, ge=0, description="Number of shares traded")
    owned: Optional[int] = Field(None, ge=0, description="Total shares owned after trade")
    delta_own: Optional[int] = Field(None, description="Change in ownership")
    value: Optional[float] = Field(None, ge=0, description="Total trade value in USD")


class TradePerformance(BaseModel):
    """Performance metrics for a trade"""
    performance_1d: Optional[float] = Field(None, description="1-day performance (%)")
    performance_1w: Optional[float] = Field(None, description="1-week performance (%)")
    performance_1m: Optional[float] = Field(None, description="1-month performance (%)")
    performance_6m: Optional[float] = Field(None, description="6-month performance (%)")


class Trade(TradeBase, TradePerformance):
    """Complete trade model including performance metrics"""
    id: int = Field(..., description="Unique trade record ID")
    scraped_at: Optional[datetime] = Field(None, description="When the record was scraped")
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy compatibility


class TradeResponse(BaseModel):
    """Response model for paginated trade queries"""
    trades: list[Trade]
    total: int = Field(..., description="Total number of matching records")
    limit: int = Field(..., description="Number of records per page")
    offset: int = Field(..., description="Number of records skipped")
    has_more: bool = Field(..., description="Whether more records are available")


class TradeFilters(BaseModel):
    """Available filters for trade queries"""
    ticker: Optional[str] = Field(None, description="Filter by ticker symbol")
    insider_name: Optional[str] = Field(None, description="Filter by insider name (partial match)")
    trade_type: Optional[str] = Field(None, description="Filter by trade type: Buy or Sell")
    trade_flag: Optional[str] = Field(None, description="Filter by trade flag")
    date_from: Optional[str] = Field(None, description="Filter trades from date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter trades to date (YYYY-MM-DD)")
    min_value_usd: Optional[float] = Field(None, ge=0, description="Minimum trade value in USD")