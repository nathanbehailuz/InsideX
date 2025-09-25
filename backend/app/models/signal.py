"""
Pydantic models for ML signals and predictions
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Signal confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SignalReason(BaseModel):
    """Individual reason contributing to a signal"""
    feature: str = Field(..., description="Feature name that contributed to the signal")
    importance: float = Field(..., ge=0, le=1, description="Feature importance score (0-1)")
    description: str = Field(..., description="Human-readable description of this reason")


class SignalBase(BaseModel):
    """Base signal information"""
    ticker: str = Field(..., description="Stock ticker symbol")
    score: float = Field(..., ge=0, le=1, description="Signal strength score (0-1)")
    confidence: ConfidenceLevel = Field(..., description="Confidence level of the signal")
    prediction_horizon_days: int = Field(..., gt=0, description="Prediction horizon in days")
    expected_return_pct: Optional[float] = Field(None, description="Expected return percentage")


class Signal(SignalBase):
    """Complete signal with reasoning"""
    reasons: List[SignalReason] = Field(default_factory=list, description="Reasons for the signal")
    generated_at: datetime = Field(..., description="When the signal was generated")
    model_version: str = Field(..., description="Version of the model used")
    recent_trades_count: int = Field(..., ge=0, description="Number of recent trades considered")
    insider_activity_score: Optional[float] = Field(None, ge=0, le=1, description="Insider activity intensity score")


class SignalRequest(BaseModel):
    """Request model for generating signals"""
    ticker: Optional[str] = Field(None, description="Specific ticker to score (optional)")
    lookback_days: int = Field(30, gt=0, le=365, description="Days to look back for insider activity")
    min_trade_value: Optional[float] = Field(None, ge=0, description="Minimum trade value to consider")
    prediction_horizon_days: int = Field(20, gt=0, le=100, description="Prediction horizon in trading days")


class FilingForSignal(BaseModel):
    """Individual filing/trade for manual signal scoring"""
    ticker: str = Field(..., description="Stock ticker symbol")
    trade_date: str = Field(..., description="Trade execution date (YYYY-MM-DD)")
    insider_role: str = Field(..., description="Insider's role (e.g., 'CEO', 'VP', '10% Owner')")
    price: float = Field(..., gt=0, description="Trade price per share")
    quantity: int = Field(..., description="Number of shares (positive for buy, negative for sell)")
    ownership_after: Optional[float] = Field(None, ge=0, le=1, description="Ownership percentage after trade")


class SignalRequestWithFilings(BaseModel):
    """Request model for scoring specific filings"""
    filings: List[FilingForSignal] = Field(..., min_items=1, description="List of filings to score")
    prediction_horizon_days: int = Field(20, gt=0, le=100, description="Prediction horizon in trading days")


class SignalTopResponse(BaseModel):
    """Response model for top signals endpoint"""
    signals: List[Signal]
    generated_at: datetime = Field(..., description="When these signals were generated")
    window_days: int = Field(..., description="Days of data considered")
    total_tickers_evaluated: int = Field(..., description="Total number of tickers evaluated")


class SignalScoreResponse(BaseModel):
    """Response model for signal scoring"""
    generated_at: datetime = Field(..., description="When the signal was generated")
    signals: List[Signal]