"""
Company-related Pydantic models
"""

from typing import Optional, List
from pydantic import BaseModel

class Company(BaseModel):
    """Company basic information"""
    ticker: str
    company_name: Optional[str] = None

class CompanySummary(BaseModel):
    """Company trading summary statistics"""
    ticker: str
    company_name: Optional[str] = None
    total_trades: int
    total_bought: Optional[int] = 0
    total_sold: Optional[int] = 0
    avg_buy_price: Optional[float] = None
    avg_sell_price: Optional[float] = None
    net_shares: Optional[int] = 0
    buy_sell_ratio: Optional[float] = None
    recent_activity_30d: Optional[int] = 0
    recent_activity_90d: Optional[int] = 0
    
class CompanyResponse(BaseModel):
    """Response model for company queries"""
    company: CompanySummary
    recent_trades: Optional[List] = []