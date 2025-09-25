"""
Signal routes for the FastAPI application
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.app.core.deps import get_database
from backend.app.models.signal import SignalRequest, SignalResponse, TopSignalsResponse, Signal
from backend.app.services.signal_service import SignalService
from database import InsiderTradingDB

router = APIRouter()

@router.get("/signals/top", response_model=TopSignalsResponse)
async def get_top_signals(
    window_days: int = 30,
    limit: int = 50,
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get top-ranked trading signals for the specified time window.
    
    Uses ML model if available, otherwise falls back to heuristic scoring.
    """
    try:
        signal_service = SignalService(db)
        result = await signal_service.generate_signals(window_days, limit)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating signals: {str(e)}")

@router.post("/signals/score", response_model=SignalResponse)
async def score_signals(
    request: SignalRequest,
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Score trading signals for specific ticker or filings.
    
    Uses ML model if available for accurate signal scoring.
    """
    try:
        signal_service = SignalService(db)
        signals = []
        
        if request.ticker:
            # Score signals for specific ticker
            ticker_signals = await signal_service.score_ticker_signals(
                request.ticker, 
                request.lookback_days or 30
            )
            signals.extend(ticker_signals)
        
        elif request.filings:
            # Score individual filings (mock implementation for now)
            # In production, would create temporary dataframe and score
            for filing in request.filings:
                value = filing.quantity * filing.price
                score = min(0.95, max(0.1, value / 1000000 * 0.5 + 0.2))
                confidence = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
                
                signal = Signal(
                    ticker=filing.ticker,
                    score=score,
                    confidence=confidence,
                    reasons=[
                        f"Filing value: ${value:,.0f}",
                        f"Insider role: {filing.insider_role}"
                    ],
                    trade_date=filing.trade_date,
                    trade_value=value
                )
                signals.append(signal)
        
        # Get model info for metadata
        model_info = signal_service.get_model_info()
        
        return SignalResponse(
            generated_at=datetime.now(),
            signals=signals,
            metadata={
                "model_info": model_info,
                "signal_count": len(signals)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring signals: {str(e)}")

@router.get("/signals/model-info")
async def get_model_info(
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get information about the loaded ML model.
    """
    try:
        signal_service = SignalService(db)
        model_info = signal_service.get_model_info()
        return model_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")