"""
Pydantic models for company data and summaries
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    """Base company information"""
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")


class CompanyStats(BaseModel):
    """Company trading statistics"""
    total_trades: int = Field(..., ge=0, description="Total number of insider trades")
    total_bought: int = Field(..., ge=0, description="Total shares bought by insiders")
    total_sold: int = Field(..., ge=0, description="Total shares sold by insiders")
    net_shares: int = Field(..., description="Net shares (bought - sold)")
    avg_buy_price: Optional[float] = Field(None, ge=0, description="Average buy price")
    avg_sell_price: Optional[float] = Field(None, ge=0, description="Average sell price")
    unique_insiders: int = Field(..., ge=0, description="Number of unique insiders who traded")


class CompanyRecentActivity(BaseModel):
    """Recent trading activity for a company"""
    last_30d_buys: int = Field(..., ge=0, description="Buy trades in last 30 days")
    last_30d_sells: int = Field(..., ge=0, description="Sell trades in last 30 days")
    last_30d_buy_value: float = Field(..., ge=0, description="Total buy value in last 30 days (USD)")
    last_30d_sell_value: float = Field(..., ge=0, description="Total sell value in last 30 days (USD)")
    last_90d_buys: int = Field(..., ge=0, description="Buy trades in last 90 days")
    last_90d_sells: int = Field(..., ge=0, description="Sell trades in last 90 days")
    buy_sell_ratio_30d: Optional[float] = Field(None, description="Ratio of buys to sells (last 30d)")
    buy_sell_ratio_90d: Optional[float] = Field(None, description="Ratio of buys to sells (last 90d)")


class CompanySummary(CompanyBase):
    """Complete company summary with stats and recent activity"""
    stats: CompanyStats
    recent_activity: CompanyRecentActivity
    last_filing_date: Optional[str] = Field(None, description="Most recent filing date")
    last_trade_date: Optional[str] = Field(None, description="Most recent trade date")


class CompanyListItem(CompanyBase):
    """Lightweight company info for lists"""
    total_trades: int = Field(..., description="Total trades for this company")
    last_trade_date: Optional[str] = Field(None, description="Most recent trade date")


class CompanyResponse(BaseModel):
    """Response model for company queries"""
    companies: List[CompanyListItem]
    total: int = Field(..., description="Total number of companies")
    limit: int = Field(..., description="Number of records per page")
    offset: int = Field(..., description="Number of records skipped")