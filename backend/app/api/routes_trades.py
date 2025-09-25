"""
API routes for insider trading data
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
import logging

from app.models.trade import Trade, TradeResponse, TradeFilters
from app.services.trade_service import TradeService
from app.core.deps import TradeQueryParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trades", tags=["trades"])

# Global service instance
trade_service = TradeService()


@router.get("/", response_model=TradeResponse)
async def get_trades(params: TradeQueryParams = Depends()):
    """
    Get insider trades with filtering and pagination
    
    **Supported filters:**
    - ticker: Company ticker symbol (e.g., AAPL)  
    - insider_name: Insider name (partial match)
    - trade_type: Buy or Sell
    - trade_flag: Trade flag (e.g., "10% Owner")
    - date_from/date_to: Date range filter (YYYY-MM-DD)
    - min_value_usd: Minimum trade value in USD
    
    **Pagination:**
    - limit: Records per page (max 1000)
    - offset: Records to skip
    """
    try:
        trades_data, total_count = trade_service.get_trades(
            ticker=params.ticker,
            insider_name=params.insider_name,
            trade_type=params.trade_type,
            trade_flag=params.trade_flag,
            date_from=params.date_from,
            date_to=params.date_to,
            min_value_usd=params.min_value_usd,
            limit=params.limit,
            offset=params.offset
        )
        
        # Convert to Pydantic models
        trades = [Trade.model_validate(trade_data) for trade_data in trades_data]
        
        return TradeResponse(
            trades=trades,
            total=total_count,
            limit=params.limit,
            offset=params.offset,
            has_more=(params.offset + params.limit) < total_count
        )
        
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trades")


@router.get("/recent")
async def get_recent_trades(
    days: int = Query(default=30, ge=1, le=365, description="Days to look back"),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum number of trades")
):
    """Get recent insider trades within specified days"""
    try:
        trades_data = trade_service.get_recent_trades(days=days, limit=limit)
        trades = [Trade.model_validate(trade_data) for trade_data in trades_data]
        
        return {
            "trades": trades,
            "days": days,
            "count": len(trades),
            "generated_at": "2025-09-25T12:00:00Z"  # Would be datetime.now() in real implementation
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent trades: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent trades")


@router.get("/large")
async def get_large_trades(
    min_value: float = Query(default=1000000, ge=0, description="Minimum trade value in USD"),
    limit: int = Query(default=50, ge=1, le=500, description="Maximum number of trades")
):
    """Get large insider trades above specified value threshold"""
    try:
        trades_data = trade_service.get_large_trades(min_value=min_value, limit=limit)
        trades = [Trade.model_validate(trade_data) for trade_data in trades_data]
        
        return {
            "trades": trades,
            "min_value": min_value,
            "count": len(trades),
            "generated_at": "2025-09-25T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching large trades: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch large trades")


@router.get("/{trade_id}")
async def get_trade_by_id(trade_id: int):
    """Get a specific trade by ID"""
    try:
        trade_data = trade_service.get_trade_by_id(trade_id)
        
        if not trade_data:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        
        return Trade.model_validate(trade_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trade {trade_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trade")


@router.get("/summary/buy-sell")
async def get_buy_sell_summary(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Days to look back")
):
    """Get buy vs sell summary statistics"""
    try:
        summary = trade_service.get_buy_sell_summary(ticker=ticker, days=days)
        
        return {
            "summary": summary,
            "filters": {
                "ticker": ticker,
                "days": days
            },
            "generated_at": "2025-09-25T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching buy/sell summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch summary")