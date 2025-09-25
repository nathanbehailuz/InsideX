"""
Company routes for the FastAPI application
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List

from app.core.deps import get_database
from app.models.company import CompanyResponse
from app.services.trade_service import TradeService
from database import InsiderTradingDB

router = APIRouter()

@router.get("/companies/{ticker}", response_model=CompanyResponse)
async def get_company(
    ticker: str = Path(..., description="Stock ticker symbol (e.g., AAPL)"),
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get comprehensive company information including trading summary and recent insider activity.
    
    - **ticker**: Stock ticker symbol to look up
    
    Returns:
    - Company summary statistics (total trades, buy/sell activity, etc.)
    - Recent insider trades for the company
    """
    try:
        # Convert ticker to uppercase
        ticker = ticker.upper()
        
        # Get service and execute query
        service = TradeService(db)
        result = await service.get_company_summary(ticker)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company data: {str(e)}")

@router.get("/companies")
async def get_companies(
    limit: int = 50,
    db: InsiderTradingDB = Depends(get_database)
):
    """
    Get list of companies with recent insider trading activity.
    
    Returns the most actively traded companies by insider activity.
    """
    try:
        import sqlite3
        import pandas as pd
        
        # Get companies with most recent activity
        with sqlite3.connect(db.db_path) as conn:
            query = """
                SELECT 
                    ticker,
                    company_name,
                    COUNT(*) as recent_trades,
                    SUM(CASE WHEN trade_type = 'Buy' THEN qty ELSE 0 END) as total_bought,
                    SUM(CASE WHEN trade_type = 'Sell' THEN qty ELSE 0 END) as total_sold,
                    MAX(trade_date) as last_trade_date
                FROM insider_trades 
                WHERE trade_date >= date('now', '-90 days')
                GROUP BY ticker, company_name
                ORDER BY recent_trades DESC
                LIMIT ?
            """
            
            companies_df = pd.read_sql_query(query, conn, params=[limit])
            
            companies = []
            for _, row in companies_df.iterrows():
                company_dict = row.to_dict()
                # Handle NaN values
                for key, value in company_dict.items():
                    if pd.isna(value):
                        company_dict[key] = None
                companies.append(company_dict)
            
            return {
                "companies": companies,
                "total": len(companies)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching companies: {str(e)}")