"""
Pydantic models for insider data and profiles
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InsiderBase(BaseModel):
    """Base insider information"""
    insider_name: str = Field(..., description="Insider/executive name")
    title: Optional[str] = Field(None, description="Most common title/role")


class InsiderStats(BaseModel):
    """Insider trading statistics"""
    total_trades: int = Field(..., ge=0, description="Total number of trades by this insider")
    total_bought: int = Field(..., ge=0, description="Total shares bought")
    total_sold: int = Field(..., ge=0, description="Total shares sold")
    net_shares: int = Field(..., description="Net shares (bought - sold)")
    total_buy_value: float = Field(..., ge=0, description="Total value of buys (USD)")
    total_sell_value: float = Field(..., ge=0, description="Total value of sells (USD)")
    net_value: float = Field(..., description="Net trade value (buy_value - sell_value)")
    avg_trade_size: float = Field(..., ge=0, description="Average trade size (shares)")
    companies_traded: int = Field(..., ge=0, description="Number of different companies traded")


class InsiderPerformance(BaseModel):
    """Insider performance metrics"""
    avg_1d_performance: Optional[float] = Field(None, description="Average 1-day performance of trades (%)")
    avg_1w_performance: Optional[float] = Field(None, description="Average 1-week performance of trades (%)")
    avg_1m_performance: Optional[float] = Field(None, description="Average 1-month performance of trades (%)")
    avg_6m_performance: Optional[float] = Field(None, description="Average 6-month performance of trades (%)")
    profitable_trades_1m: int = Field(..., ge=0, description="Number of profitable trades (1-month)")
    total_trades_with_1m_data: int = Field(..., ge=0, description="Total trades with 1-month performance data")
    hit_rate_1m: Optional[float] = Field(None, ge=0, le=100, description="1-month hit rate (%)")


class InsiderRecentActivity(BaseModel):
    """Recent trading activity for an insider"""
    last_30d_trades: int = Field(..., ge=0, description="Trades in last 30 days")
    last_30d_buy_value: float = Field(..., ge=0, description="Buy value in last 30 days (USD)")
    last_30d_sell_value: float = Field(..., ge=0, description="Sell value in last 30 days (USD)")
    last_90d_trades: int = Field(..., ge=0, description="Trades in last 90 days")
    most_active_ticker: Optional[str] = Field(None, description="Most frequently traded ticker")
    most_active_company: Optional[str] = Field(None, description="Most frequently traded company")


class InsiderProfile(InsiderBase):
    """Complete insider profile with stats and performance"""
    stats: InsiderStats
    performance: InsiderPerformance
    recent_activity: InsiderRecentActivity
    first_trade_date: Optional[str] = Field(None, description="First recorded trade date")
    last_trade_date: Optional[str] = Field(None, description="Most recent trade date")
    primary_companies: List[str] = Field(default_factory=list, description="Most frequently traded companies")


class InsiderListItem(InsiderBase):
    """Lightweight insider info for lists"""
    total_trades: int = Field(..., description="Total trades by this insider")
    hit_rate_1m: Optional[float] = Field(None, description="1-month hit rate (%)")
    last_trade_date: Optional[str] = Field(None, description="Most recent trade date")
    most_active_ticker: Optional[str] = Field(None, description="Most frequently traded ticker")


class InsiderResponse(BaseModel):
    """Response model for insider queries"""
    insiders: List[InsiderListItem]
    total: int = Field(..., description="Total number of insiders")
    limit: int = Field(..., description="Number of records per page")
    offset: int = Field(..., description="Number of records skipped")