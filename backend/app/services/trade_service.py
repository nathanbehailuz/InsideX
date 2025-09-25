"""
Trade service for database operations and business logic
"""
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging
import os

# Import the existing database class
import sys
sys.path.append('/workspace')
from database import InsiderTradingDB

logger = logging.getLogger(__name__)


class TradeService:
    """Service class for trade-related database operations"""
    
    def __init__(self, db_path: str = "/workspace/insider_trading.db"):
        self.db_path = db_path
        self.db = InsiderTradingDB(db_path) if os.path.exists(db_path) else None
        if not self.db:
            logger.warning(f"Database not found at {db_path}")
    
    def get_trades(
        self,
        ticker: Optional[str] = None,
        insider_name: Optional[str] = None,
        trade_type: Optional[str] = None,
        trade_flag: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_value_usd: Optional[float] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "filing_date",
        order_desc: bool = True
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get filtered trades with pagination
        
        Returns:
            Tuple of (trade_records, total_count)
        """
        if not self.db:
            return [], 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Build the query with filters
                where_conditions = ["1=1"]
                params = []
                
                if ticker:
                    where_conditions.append("ticker = ?")
                    params.append(ticker.upper())
                
                if insider_name:
                    where_conditions.append("insider_name LIKE ?")
                    params.append(f"%{insider_name}%")
                
                if trade_type:
                    where_conditions.append("trade_type = ?")
                    params.append(trade_type)
                
                if trade_flag:
                    where_conditions.append("trade_flag = ?")
                    params.append(trade_flag)
                
                if date_from:
                    where_conditions.append("trade_date >= ?")
                    params.append(date_from)
                
                if date_to:
                    where_conditions.append("trade_date <= ?")
                    params.append(date_to)
                
                if min_value_usd:
                    where_conditions.append("value >= ?")
                    params.append(min_value_usd)
                
                where_clause = " AND ".join(where_conditions)
                
                # Get total count
                count_query = f"SELECT COUNT(*) FROM insider_trades WHERE {where_clause}"
                cursor = conn.cursor()
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated results
                order_direction = "DESC" if order_desc else "ASC"
                data_query = f"""
                    SELECT * FROM insider_trades 
                    WHERE {where_clause}
                    ORDER BY {order_by} {order_direction}
                    LIMIT ? OFFSET ?
                """
                
                params.extend([limit, offset])
                df = pd.read_sql_query(data_query, conn, params=params)
                
                # Convert to list of dicts
                records = df.to_dict('records') if not df.empty else []
                
                logger.info(f"Retrieved {len(records)} trades (total: {total_count})")
                return records, total_count
                
        except Exception as e:
            logger.error(f"Error querying trades: {e}")
            return [], 0
    
    def get_trade_by_id(self, trade_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific trade by ID"""
        if not self.db:
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM insider_trades WHERE id = ?"
                df = pd.read_sql_query(query, conn, params=[trade_id])
                
                if df.empty:
                    return None
                
                return df.iloc[0].to_dict()
                
        except Exception as e:
            logger.error(f"Error retrieving trade {trade_id}: {e}")
            return None
    
    def get_recent_trades(self, days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades within specified days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        records, _ = self.get_trades(
            date_from=cutoff_date,
            limit=limit,
            order_by="trade_date",
            order_desc=True
        )
        return records
    
    def get_large_trades(self, min_value: float = 1000000, limit: int = 50) -> List[Dict[str, Any]]:
        """Get large trades above specified value threshold"""
        records, _ = self.get_trades(
            min_value_usd=min_value,
            limit=limit,
            order_by="value",
            order_desc=True
        )
        return records
    
    def get_trades_by_ticker(self, ticker: str, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Get all trades for a specific ticker"""
        return self.get_trades(ticker=ticker, limit=limit, offset=offset)
    
    def get_trades_by_insider(self, insider_name: str, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Get all trades for a specific insider"""
        return self.get_trades(insider_name=insider_name, limit=limit, offset=offset)
    
    def get_buy_sell_summary(self, ticker: Optional[str] = None, days: Optional[int] = None) -> Dict[str, Any]:
        """Get buy/sell summary statistics"""
        if not self.db:
            return {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                where_conditions = ["1=1"]
                params = []
                
                if ticker:
                    where_conditions.append("ticker = ?")
                    params.append(ticker.upper())
                
                if days:
                    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                    where_conditions.append("trade_date >= ?")
                    params.append(cutoff_date)
                
                where_clause = " AND ".join(where_conditions)
                
                query = f"""
                    SELECT 
                        trade_type,
                        COUNT(*) as count,
                        SUM(CASE WHEN qty IS NOT NULL THEN qty ELSE 0 END) as total_qty,
                        SUM(CASE WHEN value IS NOT NULL THEN value ELSE 0 END) as total_value,
                        AVG(CASE WHEN price IS NOT NULL AND price > 0 THEN price ELSE NULL END) as avg_price
                    FROM insider_trades 
                    WHERE {where_clause}
                    GROUP BY trade_type
                """
                
                df = pd.read_sql_query(query, conn, params=params)
                
                result = {}
                for _, row in df.iterrows():
                    result[row['trade_type'].lower()] = {
                        'count': int(row['count']),
                        'total_qty': int(row['total_qty']) if row['total_qty'] else 0,
                        'total_value': float(row['total_value']) if row['total_value'] else 0.0,
                        'avg_price': float(row['avg_price']) if row['avg_price'] else 0.0
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting buy/sell summary: {e}")
            return {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get basic database statistics"""
        if not self.db:
            return {}
        
        try:
            stats = self.db.get_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def get_company_summary(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive summary for a specific company"""
        if not self.db:
            return {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                ticker_upper = ticker.upper()
                
                # Basic company info and stats
                basic_query = """
                    SELECT 
                        company_name,
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN trade_type = 'Buy' THEN qty ELSE 0 END) as total_bought,
                        SUM(CASE WHEN trade_type = 'Sell' THEN qty ELSE 0 END) as total_sold,
                        SUM(CASE WHEN trade_type = 'Buy' THEN value ELSE 0 END) as total_buy_value,
                        SUM(CASE WHEN trade_type = 'Sell' THEN value ELSE 0 END) as total_sell_value,
                        AVG(CASE WHEN trade_type = 'Buy' THEN price END) as avg_buy_price,
                        AVG(CASE WHEN trade_type = 'Sell' THEN price END) as avg_sell_price,
                        COUNT(DISTINCT insider_name) as unique_insiders,
                        MIN(trade_date) as first_trade_date,
                        MAX(trade_date) as last_trade_date
                    FROM insider_trades 
                    WHERE ticker = ?
                """
                
                df_basic = pd.read_sql_query(basic_query, conn, params=[ticker_upper])
                
                if df_basic.empty:
                    return {}
                
                basic_stats = df_basic.iloc[0].to_dict()
                
                # Recent activity (30 and 90 days)
                recent_query = """
                    SELECT 
                        CASE 
                            WHEN date(trade_date) >= date('now', '-30 days') THEN '30d'
                            WHEN date(trade_date) >= date('now', '-90 days') THEN '90d'
                            ELSE 'older'
                        END as period,
                        trade_type,
                        COUNT(*) as count,
                        SUM(COALESCE(value, 0)) as total_value
                    FROM insider_trades 
                    WHERE ticker = ? AND date(trade_date) >= date('now', '-90 days')
                    GROUP BY period, trade_type
                """
                
                df_recent = pd.read_sql_query(recent_query, conn, params=[ticker_upper])
                
                # Process recent activity
                recent_activity = {
                    'last_30d_buys': 0, 'last_30d_sells': 0,
                    'last_30d_buy_value': 0.0, 'last_30d_sell_value': 0.0,
                    'last_90d_buys': 0, 'last_90d_sells': 0,
                    'buy_sell_ratio_30d': None, 'buy_sell_ratio_90d': None
                }
                
                buys_30d = buys_90d = sells_30d = sells_90d = 0
                
                for _, row in df_recent.iterrows():
                    period = row['period']
                    trade_type = row['trade_type']
                    count = int(row['count'])
                    
                    if period == '30d':
                        if trade_type == 'Buy':
                            recent_activity['last_30d_buys'] = count
                            recent_activity['last_30d_buy_value'] = float(row['total_value'] or 0)
                            buys_30d = count
                        else:
                            recent_activity['last_30d_sells'] = count
                            recent_activity['last_30d_sell_value'] = float(row['total_value'] or 0)
                            sells_30d = count
                    
                    if trade_type == 'Buy':
                        buys_90d += count
                    else:
                        sells_90d += count
                
                recent_activity['last_90d_buys'] = buys_90d
                recent_activity['last_90d_sells'] = sells_90d
                
                # Calculate ratios
                if sells_30d > 0:
                    recent_activity['buy_sell_ratio_30d'] = buys_30d / sells_30d
                if sells_90d > 0:
                    recent_activity['buy_sell_ratio_90d'] = buys_90d / sells_90d
                
                return {
                    'ticker': ticker_upper,
                    'company_name': basic_stats.get('company_name', ''),
                    'stats': {
                        'total_trades': int(basic_stats.get('total_trades', 0)),
                        'total_bought': int(basic_stats.get('total_bought', 0)),
                        'total_sold': int(basic_stats.get('total_sold', 0)),
                        'net_shares': int(basic_stats.get('total_bought', 0)) - int(basic_stats.get('total_sold', 0)),
                        'total_buy_value': float(basic_stats.get('total_buy_value', 0)),
                        'total_sell_value': float(basic_stats.get('total_sell_value', 0)),
                        'avg_buy_price': float(basic_stats.get('avg_buy_price', 0)) if basic_stats.get('avg_buy_price') else None,
                        'avg_sell_price': float(basic_stats.get('avg_sell_price', 0)) if basic_stats.get('avg_sell_price') else None,
                        'unique_insiders': int(basic_stats.get('unique_insiders', 0))
                    },
                    'recent_activity': recent_activity,
                    'first_trade_date': basic_stats.get('first_trade_date'),
                    'last_trade_date': basic_stats.get('last_trade_date')
                }
                
        except Exception as e:
            logger.error(f"Error getting company summary for {ticker}: {e}")
            return {}
    
    def get_all_companies(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Get all companies with basic stats"""
        if not self.db:
            return [], 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get total count
                count_query = "SELECT COUNT(DISTINCT ticker) FROM insider_trades"
                cursor = conn.cursor()
                cursor.execute(count_query)
                total_count = cursor.fetchone()[0]
                
                # Get company list with stats
                query = """
                    SELECT 
                        ticker,
                        company_name,
                        COUNT(*) as total_trades,
                        MAX(trade_date) as last_trade_date
                    FROM insider_trades 
                    GROUP BY ticker, company_name
                    ORDER BY total_trades DESC
                    LIMIT ? OFFSET ?
                """
                
                df = pd.read_sql_query(query, conn, params=[limit, offset])
                companies = df.to_dict('records') if not df.empty else []
                
                return companies, total_count
                
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return [], 0
    
    def get_insider_profile(self, insider_name: str) -> Dict[str, Any]:
        """Get comprehensive profile for a specific insider"""
        if not self.db:
            return {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic insider stats
                basic_query = """
                    SELECT 
                        insider_name,
                        title,
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN trade_type = 'Buy' THEN qty ELSE 0 END) as total_bought,
                        SUM(CASE WHEN trade_type = 'Sell' THEN qty ELSE 0 END) as total_sold,
                        SUM(CASE WHEN trade_type = 'Buy' THEN value ELSE 0 END) as total_buy_value,
                        SUM(CASE WHEN trade_type = 'Sell' THEN value ELSE 0 END) as total_sell_value,
                        AVG(CASE WHEN qty IS NOT NULL THEN qty ELSE 0 END) as avg_trade_size,
                        COUNT(DISTINCT ticker) as companies_traded,
                        MIN(trade_date) as first_trade_date,
                        MAX(trade_date) as last_trade_date
                    FROM insider_trades 
                    WHERE insider_name = ?
                    GROUP BY insider_name
                """
                
                df_basic = pd.read_sql_query(basic_query, conn, params=[insider_name])
                
                if df_basic.empty:
                    return {}
                
                basic_stats = df_basic.iloc[0].to_dict()
                
                # Performance metrics
                performance_query = """
                    SELECT 
                        AVG(CASE WHEN performance_1d IS NOT NULL THEN performance_1d END) as avg_1d_performance,
                        AVG(CASE WHEN performance_1w IS NOT NULL THEN performance_1w END) as avg_1w_performance,
                        AVG(CASE WHEN performance_1m IS NOT NULL THEN performance_1m END) as avg_1m_performance,
                        AVG(CASE WHEN performance_6m IS NOT NULL THEN performance_6m END) as avg_6m_performance,
                        COUNT(CASE WHEN performance_1m > 0 THEN 1 END) as profitable_trades_1m,
                        COUNT(CASE WHEN performance_1m IS NOT NULL THEN 1 END) as total_trades_with_1m_data
                    FROM insider_trades 
                    WHERE insider_name = ?
                """
                
                df_perf = pd.read_sql_query(performance_query, conn, params=[insider_name])
                perf_stats = df_perf.iloc[0].to_dict() if not df_perf.empty else {}
                
                # Recent activity
                recent_query = """
                    SELECT 
                        COUNT(CASE WHEN date(trade_date) >= date('now', '-30 days') THEN 1 END) as last_30d_trades,
                        SUM(CASE WHEN date(trade_date) >= date('now', '-30 days') AND trade_type = 'Buy' THEN value ELSE 0 END) as last_30d_buy_value,
                        SUM(CASE WHEN date(trade_date) >= date('now', '-30 days') AND trade_type = 'Sell' THEN value ELSE 0 END) as last_30d_sell_value,
                        COUNT(CASE WHEN date(trade_date) >= date('now', '-90 days') THEN 1 END) as last_90d_trades
                    FROM insider_trades 
                    WHERE insider_name = ?
                """
                
                df_recent = pd.read_sql_query(recent_query, conn, params=[insider_name])
                recent_stats = df_recent.iloc[0].to_dict() if not df_recent.empty else {}
                
                # Most active ticker
                ticker_query = """
                    SELECT ticker, company_name, COUNT(*) as trade_count
                    FROM insider_trades 
                    WHERE insider_name = ?
                    GROUP BY ticker, company_name
                    ORDER BY trade_count DESC
                    LIMIT 1
                """
                
                df_ticker = pd.read_sql_query(ticker_query, conn, params=[insider_name])
                most_active = df_ticker.iloc[0].to_dict() if not df_ticker.empty else {}
                
                # Primary companies (top 3)
                companies_query = """
                    SELECT company_name, COUNT(*) as trade_count
                    FROM insider_trades 
                    WHERE insider_name = ?
                    GROUP BY company_name
                    ORDER BY trade_count DESC
                    LIMIT 3
                """
                
                df_companies = pd.read_sql_query(companies_query, conn, params=[insider_name])
                primary_companies = df_companies['company_name'].tolist() if not df_companies.empty else []
                
                # Calculate hit rate
                hit_rate_1m = None
                if perf_stats.get('total_trades_with_1m_data', 0) > 0:
                    hit_rate_1m = (perf_stats.get('profitable_trades_1m', 0) / 
                                  perf_stats.get('total_trades_with_1m_data', 1)) * 100
                
                return {
                    'insider_name': basic_stats.get('insider_name', insider_name),
                    'title': basic_stats.get('title'),
                    'stats': {
                        'total_trades': int(basic_stats.get('total_trades', 0)),
                        'total_bought': int(basic_stats.get('total_bought', 0)),
                        'total_sold': int(basic_stats.get('total_sold', 0)),
                        'net_shares': int(basic_stats.get('total_bought', 0)) - int(basic_stats.get('total_sold', 0)),
                        'total_buy_value': float(basic_stats.get('total_buy_value', 0)),
                        'total_sell_value': float(basic_stats.get('total_sell_value', 0)),
                        'net_value': float(basic_stats.get('total_buy_value', 0)) - float(basic_stats.get('total_sell_value', 0)),
                        'avg_trade_size': float(basic_stats.get('avg_trade_size', 0)),
                        'companies_traded': int(basic_stats.get('companies_traded', 0))
                    },
                    'performance': {
                        'avg_1d_performance': perf_stats.get('avg_1d_performance'),
                        'avg_1w_performance': perf_stats.get('avg_1w_performance'),
                        'avg_1m_performance': perf_stats.get('avg_1m_performance'),
                        'avg_6m_performance': perf_stats.get('avg_6m_performance'),
                        'profitable_trades_1m': int(perf_stats.get('profitable_trades_1m', 0)),
                        'total_trades_with_1m_data': int(perf_stats.get('total_trades_with_1m_data', 0)),
                        'hit_rate_1m': hit_rate_1m
                    },
                    'recent_activity': {
                        'last_30d_trades': int(recent_stats.get('last_30d_trades', 0)),
                        'last_30d_buy_value': float(recent_stats.get('last_30d_buy_value', 0)),
                        'last_30d_sell_value': float(recent_stats.get('last_30d_sell_value', 0)),
                        'last_90d_trades': int(recent_stats.get('last_90d_trades', 0)),
                        'most_active_ticker': most_active.get('ticker'),
                        'most_active_company': most_active.get('company_name')
                    },
                    'first_trade_date': basic_stats.get('first_trade_date'),
                    'last_trade_date': basic_stats.get('last_trade_date'),
                    'primary_companies': primary_companies
                }
                
        except Exception as e:
            logger.error(f"Error getting insider profile for {insider_name}: {e}")
            return {}
    
    def get_all_insiders(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Get all insiders with basic stats"""
        if not self.db:
            return [], 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get total count
                count_query = "SELECT COUNT(DISTINCT insider_name) FROM insider_trades"
                cursor = conn.cursor()
                cursor.execute(count_query)
                total_count = cursor.fetchone()[0]
                
                # Get insider list with basic stats
                query = """
                    SELECT 
                        insider_name,
                        title,
                        COUNT(*) as total_trades,
                        MAX(trade_date) as last_trade_date,
                        (SELECT ticker FROM insider_trades t2 
                         WHERE t2.insider_name = t1.insider_name 
                         GROUP BY ticker 
                         ORDER BY COUNT(*) DESC 
                         LIMIT 1) as most_active_ticker,
                        AVG(CASE WHEN performance_1m > 0 THEN 1.0 ELSE 0.0 END) * 100 as hit_rate_1m
                    FROM insider_trades t1
                    GROUP BY insider_name, title
                    ORDER BY total_trades DESC
                    LIMIT ? OFFSET ?
                """
                
                df = pd.read_sql_query(query, conn, params=[limit, offset])
                insiders = df.to_dict('records') if not df.empty else []
                
                return insiders, total_count
                
        except Exception as e:
            logger.error(f"Error getting insiders: {e}")
            return [], 0