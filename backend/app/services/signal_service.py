"""
Signal generation service using ML model
"""

import joblib
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from backend.app.ml.features import FeatureEngineer
from backend.app.models.signal import Signal, SignalResponse, TopSignalsResponse
from database import InsiderTradingDB

class SignalService:
    """Service for generating ML-based trading signals"""
    
    def __init__(self, db: InsiderTradingDB, model_path: str = "app/ml/artifacts"):
        self.db = db
        self.model_path = Path(model_path)
        self.feature_engineer = FeatureEngineer(db.db_path)
        
        # Load model artifacts
        self.model = None
        self.scaler = None
        self.metadata = {}
        self._load_model()
    
    def _load_model(self) -> None:
        """Load trained model and artifacts"""
        
        try:
            # Load model
            model_file = self.model_path / "model.joblib"
            if model_file.exists():
                self.model = joblib.load(model_file)
                print(f"Loaded ML model from {model_file}")
            
            # Load scaler if exists
            scaler_file = self.model_path / "scaler.joblib"
            if scaler_file.exists():
                self.scaler = joblib.load(scaler_file)
                print(f"Loaded scaler from {scaler_file}")
            
            # Load metadata
            metadata_file = self.model_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                print(f"Loaded model metadata: {self.metadata.get('model_type', 'Unknown')}")
            
        except Exception as e:
            print(f"Warning: Could not load ML model: {e}")
            print("Will use fallback heuristic scoring")
    
    async def generate_signals(self, window_days: int = 30, limit: int = 50) -> TopSignalsResponse:
        """Generate top trading signals for recent activity"""
        
        # Get recent trades
        cutoff_date = (datetime.now() - timedelta(days=window_days)).strftime('%Y-%m-%d')
        
        recent_trades = self.db.query_trades(
            start_date=cutoff_date,
            limit=1000  # Get more data for better signal generation
        )
        
        if recent_trades.empty:
            return TopSignalsResponse(
                generated_at=datetime.now(),
                window_days=window_days,
                signals=[],
                total=0
            )
        
        # Filter for buy trades only (main signal source)
        buy_trades = recent_trades[recent_trades['trade_type'] == 'Buy'].copy()
        
        if buy_trades.empty:
            return TopSignalsResponse(
                generated_at=datetime.now(),
                window_days=window_days,
                signals=[],
                total=0
            )
        
        # Generate signals
        signals = []
        if self.model and len(self.metadata.get('feature_names', [])) > 0:
            signals = await self._generate_ml_signals(buy_trades)
        else:
            signals = await self._generate_heuristic_signals(buy_trades)
        
        # Sort by score descending and limit
        signals.sort(key=lambda x: x.score, reverse=True)
        signals = signals[:limit]
        
        return TopSignalsResponse(
            generated_at=datetime.now(),
            window_days=window_days,
            signals=signals,
            total=len(signals)
        )
    
    async def score_ticker_signals(self, ticker: str, lookback_days: int = 30) -> List[Signal]:
        """Generate signals for specific ticker"""
        
        # Get recent trades for ticker
        cutoff_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        ticker_trades = self.db.query_trades(
            ticker=ticker.upper(),
            start_date=cutoff_date,
            limit=100
        )
        
        if ticker_trades.empty:
            return []
        
        # Filter for buy trades
        buy_trades = ticker_trades[ticker_trades['trade_type'] == 'Buy'].copy()
        
        if buy_trades.empty:
            return []
        
        # Generate signals
        if self.model and len(self.metadata.get('feature_names', [])) > 0:
            signals = await self._generate_ml_signals(buy_trades)
        else:
            signals = await self._generate_heuristic_signals(buy_trades)
        
        # Filter for the requested ticker and sort by score
        ticker_signals = [s for s in signals if s.ticker.upper() == ticker.upper()]
        ticker_signals.sort(key=lambda x: x.score, reverse=True)
        
        return ticker_signals
    
    async def _generate_ml_signals(self, trades_df: pd.DataFrame) -> List[Signal]:
        """Generate signals using trained ML model"""
        
        signals = []
        
        try:
            # Create features
            features_df = self.feature_engineer.create_features(trades_df)
            
            # Get feature names from metadata
            feature_names = self.metadata.get('feature_names', [])
            available_features = [col for col in feature_names if col in features_df.columns]
            
            if not available_features:
                print("Warning: No features available for ML prediction, falling back to heuristics")
                return await self._generate_heuristic_signals(trades_df)
            
            # Prepare feature matrix
            X = features_df[available_features].copy()
            
            # Fill any remaining missing values
            X = X.fillna(0)
            
            # Scale features if scaler exists
            if self.scaler:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X.values
            
            # Get predictions
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            
            # Generate signals for each trade
            for idx, (_, trade) in enumerate(trades_df.iterrows()):
                score = float(probabilities[idx])
                
                # Skip very low probability signals
                if score < 0.3:
                    continue
                
                # Determine confidence
                confidence = "high" if score > 0.7 else "medium" if score > 0.5 else "low"
                
                # Generate reasons based on feature importance and values
                reasons = self._generate_ml_reasons(features_df.iloc[idx], score)
                
                signal = Signal(
                    ticker=trade['ticker'],
                    score=score,
                    confidence=confidence,
                    reasons=reasons,
                    trade_date=trade.get('trade_date'),
                    insider_name=trade.get('insider_name'),
                    trade_value=trade.get('value'),
                    expected_return=score * 0.15  # Rough expected return estimate
                )
                
                signals.append(signal)
                
        except Exception as e:
            print(f"Error in ML signal generation: {e}")
            # Fallback to heuristic signals
            return await self._generate_heuristic_signals(trades_df)
        
        return signals
    
    async def _generate_heuristic_signals(self, trades_df: pd.DataFrame) -> List[Signal]:
        """Generate signals using heuristic rules (fallback)"""
        
        signals = []
        
        for _, trade in trades_df.iterrows():
            # Heuristic scoring based on trade characteristics
            score = 0.4  # Base score
            reasons = []
            
            # Trade value factor
            trade_value = trade.get('value', 0) or 0
            if trade_value > 1000000:  # $1M+
                score += 0.25
                reasons.append(f"Large trade value: ${trade_value:,.0f}")
            elif trade_value > 500000:  # $500K+
                score += 0.15
                reasons.append(f"Significant trade value: ${trade_value:,.0f}")
            
            # Insider role factor
            title = str(trade.get('title', '')).lower()
            if any(role in title for role in ['ceo', 'president', 'chief executive']):
                score += 0.15
                reasons.append("CEO-level insider trading")
            elif any(role in title for role in ['cfo', 'chief financial']):
                score += 0.12
                reasons.append("CFO-level insider trading")
            elif 'director' in title:
                score += 0.08
                reasons.append("Director-level insider trading")
            
            # Performance history factor
            perf_1m = trade.get('performance_1m')
            if perf_1m and perf_1m > 0.05:  # 5%+ historical performance
                score += 0.1
                reasons.append(f"Strong 1M performance history: {perf_1m:.1%}")
            
            # Recent activity factor
            filing_date = pd.to_datetime(trade.get('filing_date'), errors='coerce')
            if filing_date and (datetime.now() - filing_date).days < 7:
                score += 0.05
                reasons.append("Recently filed")
            
            # Cap the score
            score = min(score, 0.95)
            
            # Skip low-scoring signals
            if score < 0.35:
                continue
            
            # Determine confidence
            confidence = "high" if score > 0.7 else "medium" if score > 0.5 else "low"
            
            signal = Signal(
                ticker=trade['ticker'],
                score=score,
                confidence=confidence,
                reasons=reasons or ["Insider buy activity"],
                trade_date=trade.get('trade_date'),
                insider_name=trade.get('insider_name'),
                trade_value=trade_value,
                expected_return=score * 0.12  # Rough expected return estimate
            )
            
            signals.append(signal)
        
        return signals
    
    def _generate_ml_reasons(self, trade_features: pd.Series, score: float) -> List[str]:
        """Generate human-readable reasons for ML-based signals"""
        
        reasons = []
        
        # Get feature importance if available
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.metadata.get('feature_names', [])
            feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            
            # Sort features by importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            # Generate reasons for top contributing features
            for feature_name, importance in sorted_features[:5]:
                if feature_name in trade_features.index and importance > 0.05:
                    value = trade_features[feature_name]
                    
                    if feature_name == 'trade_value_usd' and value > 500000:
                        reasons.append(f"High trade value: ${value:,.0f}")
                    elif feature_name == 'is_ceo' and value == 1:
                        reasons.append("CEO-level insider")
                    elif feature_name == 'is_cfo' and value == 1:
                        reasons.append("CFO-level insider")
                    elif feature_name == 'insider_success_rate_1m' and value > 0.6:
                        reasons.append(f"High insider success rate: {value:.1%}")
                    elif feature_name == 'company_buy_ratio' and value > 0.7:
                        reasons.append("Strong company insider buying")
                    elif feature_name == 'price_momentum_1m' and value > 0.05:
                        reasons.append(f"Positive price momentum: {value:.1%}")
        
        # Add model confidence reason
        reasons.append(f"ML model confidence: {score:.1%}")
        
        return reasons[:4]  # Limit to top 4 reasons
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        
        return {
            "model_loaded": self.model is not None,
            "model_type": self.metadata.get('model_type', 'Unknown'),
            "n_features": len(self.metadata.get('feature_names', [])),
            "model_timestamp": self.metadata.get('timestamp'),
            "model_metrics": self.metadata.get('metrics', {}),
            "scaler_used": self.scaler is not None
        }
