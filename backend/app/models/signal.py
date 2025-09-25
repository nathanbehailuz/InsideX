"""
Signal-related Pydantic models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FilingInput(BaseModel):
    """Input structure for individual filing"""
    ticker: str
    trade_date: str
    insider_role: str
    price: float
    quantity: int
    ownership_after: Optional[float] = None

class SignalRequest(BaseModel):
    """Request model for signal scoring"""
    ticker: Optional[str] = None
    lookback_days: Optional[int] = Field(default=30, ge=1, le=365)
    filings: Optional[List[FilingInput]] = None

class Signal(BaseModel):
    """Individual signal"""
    ticker: str
    score: float = Field(ge=0.0, le=1.0)
    confidence: str  # "low", "medium", "high"
    reasons: List[str]
    trade_date: Optional[str] = None
    insider_name: Optional[str] = None
    trade_value: Optional[float] = None
    expected_return: Optional[float] = None
    
class SignalResponse(BaseModel):
    """Response model for signal queries"""
    generated_at: datetime
    signals: List[Signal]
    metadata: Optional[Dict[str, Any]] = {}

class TopSignalsResponse(BaseModel):
    """Response for top signals endpoint"""
    generated_at: datetime
    window_days: int
    signals: List[Signal]
    total: int