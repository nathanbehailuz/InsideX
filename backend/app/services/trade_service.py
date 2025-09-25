"""
Trade service for business logic and data operations
"""

import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from database import InsiderTradingDB
from backend.app.models.trade import Trade, TradeResponse, TradeQuery
from backend.app.models.company import CompanySummary, CompanyResponse  
from backend.app.models.insider import InsiderSummary, InsiderResponse

class TradeService:
    """Service class for trade-related operations"""
    
    def __init__(self, db: InsiderTradingDB):
        self.db = db
    
    async def get_trades(self, query: TradeQuery) -> TradeResponse:
        """Get trades with filtering and pagination"""
        
        # Build query parameters
        filters = {}
        if query.ticker:
            filters['ticker'] = query.ticker
        if query.insider_name:
            filters['insider_name'] = query.insider_name
        if query.trade_type:
            filters['trade_type'] = query.trade_type
        if query.trade_flag:
            filters['trade_flag'] = query.trade_flag
        if query.date_from:
            filters['start_date'] = query.date_from
        if query.date_to:
            filters['end_date'] = query.date_to
        
        # Get paginated results
        trades_df = self.db.query_trades(
            ticker=query.ticker,
            insider_name=query.insider_name,
            trade_type=query.trade_type,
            trade_flag=query.trade_flag,
            start_date=query.date_from,
            end_date=query.date_to,
            limit=query.limit
        )
        
        # Get total count for pagination (simplified approach)
        total_count = len(trades_df) if not trades_df.empty else 0
        
        # Apply value filter if specified
        if query.min_value_usd and not trades_df.empty:
            trades_df = trades_df[trades_df['value'] >= query.min_value_usd]
        
        # Apply offset
        if query.offset and not trades_df.empty:
            trades_df = trades_df.iloc[query.offset:]
        
        # Convert to Trade models
        trades = []
        for _, row in trades_df.iterrows():
            trade_dict = row.to_dict()
            # Handle NaN values
            for key, value in trade_dict.items():
                if pd.isna(value):
                    trade_dict[key] = None
            trades.append(Trade(**trade_dict))
        
        return TradeResponse(
            trades=trades,
            total=total_count,
            limit=query.limit,
            offset=query.offset or 0
        )
    
    async def get_company_summary(self, ticker: str) -> CompanyResponse:
        """Get comprehensive company trading summary"""
        
        # Get basic company summary
        summary_df = self.db.get_company_summary(ticker)
        
        if summary_df.empty:
            # Return empty response if company not found
            return CompanyResponse(
                company=CompanySummary(
                    ticker=ticker,
                    total_trades=0
                ),
                recent_trades=[]
            )
        
        summary_row = summary_df.iloc[0].to_dict()
        
        # Get recent trades (last 30 days)
        recent_trades_df = self.db.query_trades(
            ticker=ticker,
            limit=20
        )
        
        # Calculate additional metrics
        net_shares = (summary_row.get('total_bought', 0) or 0) - (summary_row.get('total_sold', 0) or 0)
        
        buy_sell_ratio = None
        if summary_row.get('total_sold', 0):
            buy_sell_ratio = (summary_row.get('total_bought', 0) or 0) / summary_row['total_sold']
        
        # Get recent activity counts
        recent_30d = self._get_recent_activity_count(ticker, 30)
        recent_90d = self._get_recent_activity_count(ticker, 90)
        
        company_summary = CompanySummary(
            ticker=ticker,
            company_name=self._get_company_name(ticker),
            total_trades=summary_row.get('total_trades', 0),
            total_bought=summary_row.get('total_bought', 0),
            total_sold=summary_row.get('total_sold', 0),
            avg_buy_price=summary_row.get('avg_buy_price'),
            avg_sell_price=summary_row.get('avg_sell_price'),
            net_shares=net_shares,
            buy_sell_ratio=buy_sell_ratio,
            recent_activity_30d=recent_30d,
            recent_activity_90d=recent_90d
        )
        
        # Convert recent trades to dict format
        recent_trades = []
        for _, row in recent_trades_df.iterrows():
            trade_dict = row.to_dict()
            # Handle NaN values
            for key, value in trade_dict.items():
                if pd.isna(value):
                    trade_dict[key] = None
            recent_trades.append(trade_dict)
        
        return CompanyResponse(
            company=company_summary,
            recent_trades=recent_trades[:10]  # Limit to top 10
        )
    
    async def get_insider_summary(self, insider_name: str) -> InsiderResponse:
        """Get comprehensive insider trading summary"""
        
        # Get all trades for this insider
        insider_trades_df = self.db.query_trades(
            insider_name=insider_name,
            limit=1000  # Get more data for analysis
        )
        
        if insider_trades_df.empty:
            return InsiderResponse(
                insider=InsiderSummary(
                    insider_name=insider_name,
                    total_trades=0
                ),
                recent_trades=[],
                performance_history=[]
            )
        
        # Calculate summary statistics
        total_trades = len(insider_trades_df)
        total_bought = insider_trades_df[insider_trades_df['trade_type'] == 'Buy']['qty'].sum() if 'qty' in insider_trades_df.columns else 0
        total_sold = insider_trades_df[insider_trades_df['trade_type'] == 'Sell']['qty'].sum() if 'qty' in insider_trades_df.columns else 0
        total_companies = insider_trades_df['ticker'].nunique() if 'ticker' in insider_trades_df.columns else 0
        
        avg_trade_value = None
        if 'value' in insider_trades_df.columns:
            avg_trade_value = insider_trades_df['value'].mean()
            if pd.isna(avg_trade_value):
                avg_trade_value = None
        
        # Calculate success rates (simplified)
        success_rate_1m = self._calculate_success_rate(insider_trades_df, 'performance_1m')
        success_rate_3m = None  # Would need 3m performance data
        success_rate_6m = self._calculate_success_rate(insider_trades_df, 'performance_6m')
        
        # Recent activity
        recent_30d = self._get_recent_insider_activity(insider_name, 30)
        
        insider_summary = InsiderSummary(
            insider_name=insider_name,
            total_trades=total_trades,
            total_bought=int(total_bought) if pd.notna(total_bought) else 0,
            total_sold=int(total_sold) if pd.notna(total_sold) else 0,
            total_companies=total_companies,
            avg_trade_value=avg_trade_value,
            success_rate_1m=success_rate_1m,
            success_rate_3m=success_rate_3m,
            success_rate_6m=success_rate_6m,
            recent_activity_30d=recent_30d
        )
        
        # Get recent trades
        recent_trades = []
        for _, row in insider_trades_df.head(10).iterrows():
            trade_dict = row.to_dict()
            # Handle NaN values
            for key, value in trade_dict.items():
                if pd.isna(value):
                    trade_dict[key] = None
            recent_trades.append(trade_dict)
        
        # Performance history (simplified)
        performance_history = self._get_insider_performance_history(insider_trades_df)
        
        return InsiderResponse(
            insider=insider_summary,
            recent_trades=recent_trades,
            performance_history=performance_history
        )
    
    def _get_company_name(self, ticker: str) -> Optional[str]:
        """Get company name for ticker"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT company_name FROM insider_trades WHERE ticker = ? LIMIT 1",
                    (ticker,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception:
            return None
    
    def _get_recent_activity_count(self, ticker: str, days: int) -> int:
        """Get count of trades for ticker in last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM insider_trades WHERE ticker = ? AND trade_date >= ?",
                    (ticker, cutoff_date)
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0
    
    def _get_recent_insider_activity(self, insider_name: str, days: int) -> int:
        """Get count of trades for insider in last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM insider_trades WHERE insider_name = ? AND trade_date >= ?",
                    (insider_name, cutoff_date)
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0
    
    def _calculate_success_rate(self, df: pd.DataFrame, performance_col: str) -> Optional[float]:
        """Calculate success rate based on performance column"""
        if performance_col not in df.columns:
            return None
        
        performance_data = df[performance_col].dropna()
        if len(performance_data) == 0:
            return None
        
        successful_trades = (performance_data > 0).sum()
        return successful_trades / len(performance_data) if len(performance_data) > 0 else None
    
    def _get_insider_performance_history(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get insider performance history over time"""
        # Simplified version - group by month and calculate avg performance
        if df.empty or 'trade_date' not in df.columns:
            return []
        
        try:
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df['month'] = df['trade_date'].dt.to_period('M')
            
            monthly_performance = df.groupby('month').agg({
                'performance_1m': 'mean',
                'performance_6m': 'mean',
                'trade_type': 'count'
            }).reset_index()
            
            performance_history = []
            for _, row in monthly_performance.iterrows():
                performance_history.append({
                    'period': str(row['month']),
                    'avg_performance_1m': row['performance_1m'] if pd.notna(row['performance_1m']) else None,
                    'avg_performance_6m': row['performance_6m'] if pd.notna(row['performance_6m']) else None,
                    'trade_count': row['trade_type']
                })
            
            return performance_history[-12:]  # Last 12 months
        except Exception:
            return []