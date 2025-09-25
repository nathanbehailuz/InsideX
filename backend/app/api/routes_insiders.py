"""
API routes for insider data and profiles
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Optional, List
import logging
import urllib.parse

from app.models.insider import InsiderProfile, InsiderListItem, InsiderResponse
from app.services.trade_service import TradeService
from app.core.deps import CommonQueryParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insiders", tags=["insiders"])

# Global service instance
trade_service = TradeService()


@router.get("/", response_model=InsiderResponse)
async def get_insiders(params: CommonQueryParams = Depends()):
    """
    Get list of all insiders with basic trading statistics
    
    Returns insiders ordered by total number of trades (descending)
    """
    try:
        insiders_data, total_count = trade_service.get_all_insiders(
            limit=params.limit,
            offset=params.offset
        )
        
        # Convert to Pydantic models
        insiders = []
        for insider_data in insiders_data:
            insider = InsiderListItem(
                insider_name=insider_data['insider_name'],
                title=insider_data.get('title'),
                total_trades=insider_data['total_trades'],
                hit_rate_1m=insider_data.get('hit_rate_1m'),
                last_trade_date=insider_data.get('last_trade_date'),
                most_active_ticker=insider_data.get('most_active_ticker')
            )
            insiders.append(insider)
        
        return InsiderResponse(
            insiders=insiders,
            total=total_count,
            limit=params.limit,
            offset=params.offset
        )
        
    except Exception as e:
        logger.error(f"Error fetching insiders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch insiders")


@router.get("/{insider_name}")
async def get_insider_profile(
    insider_name: str = Path(..., description="Insider name (URL encoded if contains spaces)")
):
    """
    Get comprehensive profile for a specific insider
    
    **Returns:**
    - Insider basic info (name, title)
    - Trading statistics (total trades, buy/sell volumes, performance)
    - Recent activity (last 30d and 90d metrics)
    - Primary companies traded
    - Historical performance and hit rate
    
    **Note:** If the insider name contains spaces, it should be URL encoded (e.g., "John%20Smith")
    """
    try:
        # URL decode the insider name
        decoded_name = urllib.parse.unquote(insider_name)
        
        profile_data = trade_service.get_insider_profile(decoded_name)
        
        if not profile_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Insider '{decoded_name}' not found or has no trading data"
            )
        
        # Create nested Pydantic models
        from app.models.insider import InsiderStats, InsiderPerformance, InsiderRecentActivity
        
        stats = InsiderStats(**profile_data['stats'])
        performance = InsiderPerformance(**profile_data['performance'])
        recent_activity = InsiderRecentActivity(**profile_data['recent_activity'])
        
        insider_profile = InsiderProfile(
            insider_name=profile_data['insider_name'],
            title=profile_data.get('title'),
            stats=stats,
            performance=performance,
            recent_activity=recent_activity,
            first_trade_date=profile_data.get('first_trade_date'),
            last_trade_date=profile_data.get('last_trade_date'),
            primary_companies=profile_data.get('primary_companies', [])
        )
        
        return insider_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching insider profile for {insider_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch insider profile")


@router.get("/{insider_name}/trades")
async def get_insider_trades(
    insider_name: str = Path(..., description="Insider name (URL encoded if contains spaces)"),
    limit: int = Query(default=100, ge=1, le=500, description="Number of trades to return"),
    offset: int = Query(default=0, ge=0, description="Number of trades to skip")
):
    """Get all trades for a specific insider with pagination"""
    try:
        from app.models.trade import Trade
        
        # URL decode the insider name
        decoded_name = urllib.parse.unquote(insider_name)
        
        trades_data, total_count = trade_service.get_trades_by_insider(
            insider_name=decoded_name,
            limit=limit,
            offset=offset
        )
        
        if not trades_data and total_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No trades found for insider '{decoded_name}'"
            )
        
        trades = [Trade.model_validate(trade_data) for trade_data in trades_data]
        
        return {
            "insider_name": decoded_name,
            "trades": trades,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trades for insider {insider_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch insider trades")


@router.get("/search/by-name")
async def search_insiders_by_name(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results to return")
):
    """Search for insiders by name (partial matching)"""
    try:
        # Use the general trades search with insider_name filter
        trades_data, _ = trade_service.get_trades(
            insider_name=q,
            limit=1000,  # Get many trades to find unique insiders
            offset=0
        )
        
        # Extract unique insiders from the trades
        unique_insiders = {}
        for trade in trades_data:
            name = trade['insider_name']
            if name not in unique_insiders:
                unique_insiders[name] = {
                    'insider_name': name,
                    'title': trade.get('title'),
                    'sample_ticker': trade.get('ticker'),
                    'sample_company': trade.get('company_name'),
                    'last_seen': trade.get('trade_date')
                }
        
        # Convert to list and limit results
        results = list(unique_insiders.values())[:limit]
        
        return {
            "query": q,
            "results": results,
            "count": len(results),
            "total_found": len(unique_insiders)
        }
        
    except Exception as e:
        logger.error(f"Error searching insiders by name '{q}': {e}")
        raise HTTPException(status_code=500, detail="Failed to search insiders")


@router.get("/top/performers")
async def get_top_performing_insiders(
    metric: str = Query(default="hit_rate_1m", description="Performance metric: hit_rate_1m, total_trades, avg_1m_performance"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of top performers to return"),
    min_trades: int = Query(default=5, ge=1, description="Minimum number of trades required")
):
    """Get top performing insiders by various metrics"""
    try:
        # For now, return basic list ordered by total trades (would need more complex logic for other metrics)
        insiders_data, _ = trade_service.get_all_insiders(limit=limit, offset=0)
        
        # Filter by minimum trades and format response
        filtered_insiders = [
            insider for insider in insiders_data 
            if insider.get('total_trades', 0) >= min_trades
        ]
        
        return {
            "metric": metric,
            "min_trades": min_trades,
            "top_performers": filtered_insiders[:limit],
            "count": len(filtered_insiders[:limit]),
            "generated_at": "2025-09-25T12:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching top performing insiders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top performers")