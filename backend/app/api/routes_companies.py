"""
API routes for company data and summaries
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Optional, List
import logging

from app.models.company import CompanySummary, CompanyListItem, CompanyResponse
from app.services.trade_service import TradeService
from app.core.deps import CommonQueryParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies", tags=["companies"])

# Global service instance
trade_service = TradeService()


@router.get("/", response_model=CompanyResponse)
async def get_companies(params: CommonQueryParams = Depends()):
    """
    Get list of all companies with basic trading statistics
    
    Returns companies ordered by total number of trades (descending)
    """
    try:
        companies_data, total_count = trade_service.get_all_companies(
            limit=params.limit,
            offset=params.offset
        )
        
        # Convert to Pydantic models
        companies = []
        for company_data in companies_data:
            company = CompanyListItem(
                ticker=company_data['ticker'],
                company_name=company_data['company_name'],
                total_trades=company_data['total_trades'],
                last_trade_date=company_data.get('last_trade_date')
            )
            companies.append(company)
        
        return CompanyResponse(
            companies=companies,
            total=total_count,
            limit=params.limit,
            offset=params.offset
        )
        
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch companies")


@router.get("/{ticker}")
async def get_company_summary(
    ticker: str = Path(..., description="Company ticker symbol (e.g., AAPL)")
):
    """
    Get comprehensive summary for a specific company
    
    **Returns:**
    - Company basic info (ticker, name)
    - Trading statistics (total trades, buy/sell volumes, prices)
    - Recent activity (last 30d and 90d metrics)
    - Historical data range
    """
    try:
        ticker_upper = ticker.upper()
        summary_data = trade_service.get_company_summary(ticker_upper)
        
        if not summary_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Company {ticker_upper} not found or has no trading data"
            )
        
        # The service returns data in the exact format needed for CompanySummary
        # But we need to restructure it slightly to match our Pydantic model
        from app.models.company import CompanyStats, CompanyRecentActivity
        
        stats = CompanyStats(**summary_data['stats'])
        recent_activity = CompanyRecentActivity(**summary_data['recent_activity'])
        
        company_summary = CompanySummary(
            ticker=summary_data['ticker'],
            company_name=summary_data['company_name'],
            stats=stats,
            recent_activity=recent_activity,
            last_filing_date=summary_data.get('last_trade_date'),  # Using trade_date as filing_date for now
            last_trade_date=summary_data.get('last_trade_date')
        )
        
        return company_summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company summary for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch company summary")


@router.get("/{ticker}/trades")
async def get_company_trades(
    ticker: str = Path(..., description="Company ticker symbol"),
    limit: int = Query(default=100, ge=1, le=500, description="Number of trades to return"),
    offset: int = Query(default=0, ge=0, description="Number of trades to skip")
):
    """Get all trades for a specific company with pagination"""
    try:
        from app.models.trade import Trade
        
        ticker_upper = ticker.upper()
        trades_data, total_count = trade_service.get_trades_by_ticker(
            ticker=ticker_upper,
            limit=limit,
            offset=offset
        )
        
        if not trades_data and total_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No trades found for company {ticker_upper}"
            )
        
        trades = [Trade.model_validate(trade_data) for trade_data in trades_data]
        
        return {
            "ticker": ticker_upper,
            "trades": trades,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trades for company {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch company trades")


@router.get("/{ticker}/stats")
async def get_company_stats(
    ticker: str = Path(..., description="Company ticker symbol"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Days to look back (optional)")
):
    """Get trading statistics for a specific company"""
    try:
        ticker_upper = ticker.upper()
        
        # Get buy/sell summary for this ticker
        summary = trade_service.get_buy_sell_summary(ticker=ticker_upper, days=days)
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"No trading data found for company {ticker_upper}"
            )
        
        return {
            "ticker": ticker_upper,
            "stats": summary,
            "period_days": days,
            "generated_at": "2025-09-25T12:00:00Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats for company {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch company stats")