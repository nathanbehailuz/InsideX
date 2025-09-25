"""
Trade routes for the FastAPI application
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from backend.app.core.deps import get_database
from backend.app.models.trade import TradeResponse, TradeQuery
from backend.app.services.trade_service import TradeService
from database import InsiderTradingDB

router = APIRouter()

@router.get("/trades", response_model=TradeResponse)
async def get_trades(
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    insider_name: Optional[str] = Query(None, description="Filter by insider name"),
    trade_type: Optional[str] = Query(None, description="Filter by trade type (Buy/Sell)"),
    trade_flag: Optional[str] = Query(None, description="Filter by trade flag"),
    date_from: Optional[str] = Query(None, description="Filter trades from this date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter trades to this date (YYYY-MM-DD)"),
    min_value_usd: Optional[float] = Query(None, description="Minimum trade value in USD"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get insider trades with optional filtering and pagination.
    
    - **ticker**: Filter by stock ticker symbol (e.g., "AAPL")
    - **insider_name**: Filter by insider name (partial match supported)
    - **trade_type**: Filter by "Buy" or "Sell"
    - **trade_flag**: Filter by trade flags like "M", "D", "10% Owner"
    - **date_from/date_to**: Date range filter (YYYY-MM-DD format)
    - **min_value_usd**: Minimum trade value filter
    - **limit**: Number of results to return (1-1000)
    - **offset**: Number of results to skip for pagination
    """
    try:
        # Create query object
        query = TradeQuery(
            ticker=ticker,
            insider_name=insider_name,
            trade_type=trade_type,
            trade_flag=trade_flag,
            date_from=date_from,
            date_to=date_to,
            min_value_usd=min_value_usd,
            limit=limit,
            offset=offset
        )
        
        # Get service and execute query
        service = TradeService(db)
        result = await service.get_trades(query)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trades: {str(e)}")

@router.get("/trades/stats")
async def get_trade_stats(
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get basic database statistics
    """
    try:
        stats = db.get_stats()
        return {
            "total_records": stats["total_records"],
            "date_range": {
                "min_date": stats["date_range"][0],
                "max_date": stats["date_range"][1]
            },
            "unique_companies": stats["unique_companies"],
            "unique_insiders": stats["unique_insiders"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")