"""
ML model training pipeline for insider trading signals
"""

import pandas as pd
import numpy as np
import joblib
import json
import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve, auc
from sklearn.preprocessing import StandardScaler

from .features import FeatureEngineer

class MLTrainer:
    """ML model trainer for insider trading signals"""
    
    def __init__(self, db_path: str, artifacts_dir: str = "app/ml/artifacts"):
        self.db_path = db_path
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(exist_ok=True)
        
        self.feature_engineer = FeatureEngineer(db_path)
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.metrics = {}
    
    def load_data(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Load training data from database"""
        
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT *
                FROM insider_trades
                WHERE trade_date IS NOT NULL 
                  AND ticker IS NOT NULL
                  AND trade_type IN ('Buy', 'Sell')
                ORDER BY trade_date DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql_query(query, conn)
        
        print(f"Loaded {len(df)} records from database")
        return df
    
    def prepare_features_and_labels(self, df: pd.DataFrame, 
                                   horizon_days: int = 20,
                                   threshold_pct: float = 5.0) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and labels for training"""
        
        # Create features
        features_df = self.feature_engineer.create_features(df)
        
        # Create labels
        labels = self.feature_engineer.create_labels(
            features_df, 
            horizon_days=horizon_days,
            threshold_pct=threshold_pct
        )
        
        # Get feature columns
        feature_cols = self.feature_engineer.get_feature_names()
        
        # Filter to available columns
        available_features = [col for col in feature_cols if col in features_df.columns]
        self.feature_names = available_features
        
        # Select features
        X = features_df[available_features]
        y = labels
        
        print(f"Prepared {len(available_features)} features")
        print(f"Feature names: {available_features}")
        print(f"Label distribution: {y.value_counts().to_dict()}")
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = 0.2, random_state: int = 42) -> Tuple:
        """Split data into train/test sets"""
        
        # For time series data, should use temporal split
        # For now, using random split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size,
            random_state=random_state,
            stratify=y if len(y.unique()) > 1 else None
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series,
                   model_type: str = "random_forest") -> None:
        """Train the ML model"""
        
        print(f"Training {model_type} model...")
        
        # Initialize model
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                random_state=42,
                max_iter=1000
            )
            
            # Scale features for logistic regression
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Train model
        self.model.fit(X_train, y_train)
        print("Model training completed")
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """Evaluate the trained model"""
        
        print("Evaluating model...")
        
        # Scale test data if scaler exists
        X_test_scaled = self.scaler.transform(X_test) if self.scaler else X_test
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Metrics
        auc_score = roc_auc_score(y_test, y_pred_proba) if len(y_test.unique()) > 1 else 0.0
        
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        pr_auc = auc(recall, precision) if len(y_test.unique()) > 1 else 0.0
        
        # Classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        metrics = {
            "auc": auc_score,
            "pr_auc": pr_auc,
            "accuracy": class_report["accuracy"],
            "precision": class_report.get("1", {}).get("precision", 0.0),
            "recall": class_report.get("1", {}).get("recall", 0.0),
            "f1": class_report.get("1", {}).get("f1-score", 0.0),
            "support": {
                "negative": class_report.get("0", {}).get("support", 0),
                "positive": class_report.get("1", {}).get("support", 0)
            }
        }
        
        self.metrics = metrics
        
        print(f"Model evaluation completed:")
        print(f"  AUC: {auc_score:.3f}")
        print(f"  PR-AUC: {pr_auc:.3f}")
        print(f"  Accuracy: {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall: {metrics['recall']:.3f}")
        print(f"  F1: {metrics['f1']:.3f}")
        
        return metrics
    
    def save_model(self) -> None:
        """Save trained model and artifacts"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save model
        model_path = self.artifacts_dir / f"model_{timestamp}.joblib"
        joblib.dump(self.model, model_path)
        
        # Save latest model (overwrite)
        latest_model_path = self.artifacts_dir / "model.joblib"
        joblib.dump(self.model, latest_model_path)
        
        # Save scaler if exists
        if self.scaler:
            scaler_path = self.artifacts_dir / f"scaler_{timestamp}.joblib"
            joblib.dump(self.scaler, scaler_path)
            
            latest_scaler_path = self.artifacts_dir / "scaler.joblib"
            joblib.dump(self.scaler, latest_scaler_path)
        
        # Save metadata
        metadata = {
            "timestamp": timestamp,
            "model_type": self.model.__class__.__name__,
            "feature_names": self.feature_names,
            "n_features": len(self.feature_names),
            "metrics": self.metrics,
            "scaler_used": self.scaler is not None
        }
        
        metadata_path = self.artifacts_dir / f"metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        latest_metadata_path = self.artifacts_dir / "metadata.json"
        with open(latest_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {model_path}")
        print(f"Metadata saved to {metadata_path}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        
        if not self.model:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            # Tree-based models
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            # Linear models
            importance = np.abs(self.model.coef_[0])
        else:
            return {}
        
        feature_importance = dict(zip(self.feature_names, importance))
        
        # Sort by importance
        feature_importance = dict(sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return feature_importance

def main():
    """Main training function"""
    
    parser = argparse.ArgumentParser(description='Train insider trading signal model')
    parser.add_argument('--db_path', default='../../insider_trading.db', 
                       help='Path to database file')
    parser.add_argument('--model_type', default='random_forest',
                       choices=['random_forest', 'logistic_regression'],
                       help='Type of model to train')
    parser.add_argument('--horizon_days', type=int, default=20,
                       help='Prediction horizon in days')
    parser.add_argument('--threshold_pct', type=float, default=5.0,
                       help='Performance threshold percentage')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of records for testing')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    
    args = parser.parse_args()
    
    print("Starting ML model training...")
    print(f"Parameters: {vars(args)}")
    
    # Set random seed
    np.random.seed(args.seed)
    
    # Initialize trainer
    trainer = MLTrainer(args.db_path)
    
    try:
        # Load data
        df = trainer.load_data(limit=args.limit)
        
        if len(df) < 100:
            print("Warning: Very small dataset. Results may not be reliable.")
        
        # Prepare features and labels
        X, y = trainer.prepare_features_and_labels(
            df, 
            horizon_days=args.horizon_days,
            threshold_pct=args.threshold_pct
        )
        
        if X.empty or len(y.unique()) < 2:
            print("Error: Insufficient data for training")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = trainer.split_data(X, y, random_state=args.seed)
        
        # Train model
        trainer.train_model(X_train, y_train, model_type=args.model_type)
        
        # Evaluate model
        trainer.evaluate_model(X_test, y_test)
        
        # Show feature importance
        feature_importance = trainer.get_feature_importance()
        print("\nTop 10 Feature Importance:")
        for feature, importance in list(feature_importance.items())[:10]:
            print(f"  {feature}: {importance:.4f}")
        
        # Save model
        trainer.save_model()
        
        print("\nTraining completed successfully!")
        
    except Exception as e:
        print(f"Error during training: {e}")
        raise

if __name__ == "__main__":
    main()