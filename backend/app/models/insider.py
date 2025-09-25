"""
Insider-related Pydantic models
"""

from typing import Optional, List
from pydantic import BaseModel

class Insider(BaseModel):
    """Insider basic information"""
    insider_name: str
    title: Optional[str] = None

class InsiderSummary(BaseModel):
    """Insider trading summary statistics"""
    insider_name: str
    total_trades: int
    total_bought: Optional[int] = 0
    total_sold: Optional[int] = 0
    total_companies: Optional[int] = 0
    avg_trade_value: Optional[float] = None
    success_rate_1m: Optional[float] = None
    success_rate_3m: Optional[float] = None
    success_rate_6m: Optional[float] = None
    recent_activity_30d: Optional[int] = 0
    
class InsiderResponse(BaseModel):
    """Response model for insider queries"""
    insider: InsiderSummary
    recent_trades: Optional[List] = []
    performance_history: Optional[List] = []