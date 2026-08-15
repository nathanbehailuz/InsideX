"""
People (insider) routes for the FastAPI application
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from backend.app.core.deps import get_database
from backend.app.models.insider import InsiderResponse
from backend.app.services.trade_service import TradeService
from database import InsiderTradingDB

router = APIRouter()

# OpenInsider uses "P - Purchase" / "S - Sale"; also accept legacy Buy/Sell.
_BUY_TYPES = ("'P - Purchase'", "'Buy'", "'Purchase'")
_SELL_TYPES = ("'S - Sale'", "'Sell'", "'Sale'")
_BUY_IN = ", ".join(_BUY_TYPES)
_SELL_IN = ", ".join(_SELL_TYPES)


@router.get("/insiders")
async def get_insiders(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    sort_by: str = Query("activity", description="Sort by: activity, performance, or recent"),
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get list of people (decision-makers) with trading activity.
    """
    try:
        import sqlite3
        import pandas as pd

        if sort_by == "activity":
            order_clause = "total_trades DESC"
        elif sort_by == "performance":
            order_clause = "avg_performance DESC"
        elif sort_by == "recent":
            order_clause = "last_trade_date DESC"
        else:
            order_clause = "total_trades DESC"

        with sqlite3.connect(db.db_path) as conn:
            query = f"""
                SELECT
                    insider_name,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN trade_type IN ({_BUY_IN}) THEN qty ELSE 0 END) as total_bought,
                    SUM(CASE WHEN trade_type IN ({_SELL_IN}) THEN qty ELSE 0 END) as total_sold,
                    COUNT(DISTINCT ticker) as companies_traded,
                    AVG(value) as avg_trade_value,
                    AVG(performance_1m) as avg_performance,
                    MAX(trade_date) as last_trade_date,
                    COUNT(CASE WHEN trade_date >= date('now', '-30 days') THEN 1 END) as recent_30d
                FROM insider_trades
                WHERE insider_name IS NOT NULL AND insider_name != ''
                GROUP BY insider_name
                HAVING total_trades >= 3
                ORDER BY {order_clause}
                LIMIT ?
            """

            insiders_df = pd.read_sql_query(query, conn, params=[limit])

            insiders = []
            for _, row in insiders_df.iterrows():
                insider_dict = row.to_dict()
                for key, value in insider_dict.items():
                    if pd.isna(value):
                        insider_dict[key] = None

                success_rate = None
                if insider_dict.get('avg_performance') is not None:
                    success_rate = 1.0 if insider_dict['avg_performance'] > 0 else 0.0

                insider_dict['success_rate'] = success_rate
                insiders.append(insider_dict)

            return {
                "insiders": insiders,
                "total": len(insiders),
                "sorted_by": sort_by
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching people: {str(e)}")


@router.get("/insiders/top")
async def get_top_insiders(
    limit: int = Query(10, ge=1, le=50, description="Number of top people to return"),
    db: InsiderTradingDB = Depends(get_database)
):
    """Get top people by trading activity."""
    try:
        top_insiders = db.get_top_insiders(limit)

        insiders = []
        for _, row in top_insiders.iterrows():
            insider_dict = row.to_dict()
            for key, value in insider_dict.items():
                if pd.isna(value):
                    insider_dict[key] = None
            insiders.append(insider_dict)

        return {
            "insiders": insiders,
            "total": len(insiders)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top people: {str(e)}")


@router.get("/insiders/{insider_name}", response_model=InsiderResponse)
async def get_insider(
    insider_name: str = Path(..., description="Person name to look up"),
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get comprehensive person information including trading history and performance.
    """
    try:
        service = TradeService(db)
        result = await service.get_insider_summary(insider_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching person data: {str(e)}")
