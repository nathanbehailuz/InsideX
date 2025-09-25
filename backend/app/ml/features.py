"""
Feature engineering pipeline for insider trading signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import sqlite3

class FeatureEngineer:
    """Feature engineering for insider trading ML model"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_names = []
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for ML model training/inference"""
        
        if df.empty:
            return df
        
        # Make copy to avoid modifying original
        features_df = df.copy()
        
        # Convert date columns
        features_df['filing_date'] = pd.to_datetime(features_df['filing_date'], errors='coerce')
        features_df['trade_date'] = pd.to_datetime(features_df['trade_date'], errors='coerce')
        
        # Basic trade features
        features_df = self._add_basic_features(features_df)
        
        # Time-based features  
        features_df = self._add_time_features(features_df)
        
        # Insider-level features
        features_df = self._add_insider_features(features_df)
        
        # Company-level features
        features_df = self._add_company_features(features_df)
        
        # Market context features
        features_df = self._add_market_features(features_df)
        
        # Fill missing values
        features_df = self._fill_missing_values(features_df)
        
        return features_df
    
    def _add_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic trade-level features"""
        
        # Trade value in USD (qty * price)
        df['trade_value_usd'] = df['qty'].fillna(0) * df['price'].fillna(0)
        
        # Log transform of trade value (handle zeros)
        df['log_trade_value'] = np.log1p(df['trade_value_usd'])
        
        # Ownership change ratio
        df['delta_own_ratio'] = np.where(
            df['owned'].fillna(0) > 0,
            df['delta_own'].fillna(0) / df['owned'].fillna(1),
            0
        )
        
        # Trade type encoding
        df['is_buy'] = (df['trade_type'] == 'Buy').astype(int)
        df['is_sell'] = (df['trade_type'] == 'Sell').astype(int)
        
        # Trade flag encoding (binary indicators)
        trade_flags = ['D', 'M', 'A', 'S']
        for flag in trade_flags:
            df[f'flag_{flag}'] = df['trade_flag'].fillna('').str.contains(flag, na=False).astype(int)
        
        # Insider title encoding
        ceo_titles = ['CEO', 'Chief Executive Officer', 'President']
        cfo_titles = ['CFO', 'Chief Financial Officer', 'Treasurer']
        df['is_ceo'] = df['title'].fillna('').str.contains('|'.join(ceo_titles), case=False, na=False).astype(int)
        df['is_cfo'] = df['title'].fillna('').str.contains('|'.join(cfo_titles), case=False, na=False).astype(int)
        df['is_director'] = df['title'].fillna('').str.contains('Director', case=False, na=False).astype(int)
        df['is_owner'] = df['title'].fillna('').str.contains('Owner|10%', case=False, na=False).astype(int)
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        
        # Days between filing and trade date
        df['filing_delay_days'] = (df['filing_date'] - df['trade_date']).dt.days.fillna(0)
        
        # Day of week, month, quarter
        df['trade_day_of_week'] = df['trade_date'].dt.dayofweek
        df['trade_month'] = df['trade_date'].dt.month
        df['trade_quarter'] = df['trade_date'].dt.quarter
        
        # Year
        df['trade_year'] = df['trade_date'].dt.year
        
        # Recency (days since trade)
        current_date = datetime.now()
        df['days_since_trade'] = (current_date - df['trade_date']).dt.days
        
        return df
    
    def _add_insider_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add insider-level features"""
        
        # Group by insider
        insider_stats = df.groupby('insider_name').agg({
            'trade_value_usd': ['count', 'sum', 'mean', 'std'],
            'is_buy': 'sum',
            'performance_1m': 'mean',
            'performance_6m': 'mean'
        }).round(4)
        
        insider_stats.columns = [f'insider_{col[0]}_{col[1]}' for col in insider_stats.columns]
        insider_stats['insider_buy_ratio'] = insider_stats['insider_is_buy_sum'] / insider_stats['insider_trade_value_usd_count']
        insider_stats['insider_success_rate_1m'] = (insider_stats['insider_performance_1m_mean'] > 0).astype(int)
        
        # Merge back
        df = df.merge(insider_stats, left_on='insider_name', right_index=True, how='left')
        
        return df
    
    def _add_company_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add company-level features"""
        
        # Company-level aggregations
        company_stats = df.groupby('ticker').agg({
            'trade_value_usd': ['count', 'sum', 'mean'],
            'is_buy': 'sum',
            'price': 'mean'
        }).round(4)
        
        company_stats.columns = [f'company_{col[0]}_{col[1]}' for col in company_stats.columns]
        company_stats['company_buy_ratio'] = company_stats['company_is_buy_sum'] / company_stats['company_trade_value_usd_count']
        
        # Merge back
        df = df.merge(company_stats, left_on='ticker', right_index=True, how='left')
        
        return df
    
    def _add_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market context features"""
        
        # For now, add placeholder features
        # In production, these would come from market data APIs
        
        # Price momentum proxy (using available performance data)
        df['price_momentum_1m'] = df['performance_1m'].fillna(0)
        df['price_momentum_6m'] = df['performance_6m'].fillna(0)
        
        # Volatility proxy (std of recent performance)
        df['price_volatility'] = df.groupby('ticker')['performance_1m'].transform('std').fillna(0)
        
        return df
    
    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values with appropriate defaults"""
        
        # Numeric columns: fill with 0 or median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'ratio' in col or 'rate' in col:
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna(df[col].median())
        
        # Categorical columns: fill with 'Unknown'
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna('Unknown')
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names for ML model"""
        
        feature_names = [
            # Basic trade features
            'trade_value_usd', 'log_trade_value', 'delta_own_ratio',
            'is_buy', 'is_sell',
            
            # Trade flags
            'flag_D', 'flag_M', 'flag_A', 'flag_S',
            
            # Insider titles
            'is_ceo', 'is_cfo', 'is_director', 'is_owner',
            
            # Time features
            'filing_delay_days', 'trade_day_of_week', 'trade_month', 'trade_quarter',
            
            # Insider features  
            'insider_trade_value_usd_count', 'insider_trade_value_usd_mean',
            'insider_buy_ratio', 'insider_success_rate_1m',
            
            # Company features
            'company_trade_value_usd_count', 'company_trade_value_usd_mean',
            'company_buy_ratio', 'company_price_mean',
            
            # Market features
            'price_momentum_1m', 'price_momentum_6m', 'price_volatility'
        ]
        
        return feature_names
    
    def create_labels(self, df: pd.DataFrame, horizon_days: int = 20, 
                      threshold_pct: float = 5.0) -> pd.Series:
        """Create binary labels for supervised learning"""
        
        # Use existing performance columns as proxy for labels
        # In production, this would be calculated from actual price data
        
        if horizon_days <= 30:
            performance_col = 'performance_1m'
        else:
            performance_col = 'performance_6m'
        
        if performance_col in df.columns:
            # Binary classification: positive return > threshold
            labels = (df[performance_col].fillna(0) > threshold_pct / 100).astype(int)
        else:
            # If no performance data, return zeros (to be filled later)
            labels = pd.Series(0, index=df.index)
        
        return labels