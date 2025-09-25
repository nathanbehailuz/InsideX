"""
API routes for ML signals and predictions (placeholder for ML milestone)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/")
async def signals_info():
    """Information about the signals API (ML functionality coming in M2)"""
    return {
        "message": "ML signals API - Coming in Milestone 2",
        "status": "placeholder",
        "planned_endpoints": [
            "GET /signals/top - Get top ranked tickers",
            "POST /signals/score - Score specific filings/tickers"
        ],
        "implementation_status": "pending_ml_milestone"
    }


@router.get("/top")
async def get_top_signals(
    window_days: int = Query(default=30, ge=1, le=365, description="Days of data to consider"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum signals to return")
):
    """Get top signals (placeholder - will be implemented in ML milestone)"""
    raise HTTPException(
        status_code=501,
        detail="Signal generation not implemented yet. Coming in ML Milestone (M2)."
    )


@router.post("/score")
async def score_signals():
    """Score specific filings or tickers (placeholder - will be implemented in ML milestone)"""
    raise HTTPException(
        status_code=501,
        detail="Signal scoring not implemented yet. Coming in ML Milestone (M2)."
    )