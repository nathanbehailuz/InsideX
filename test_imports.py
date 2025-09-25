#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    print("Testing imports...")
    
    # Test database import
    from database import InsiderTradingDB
    print("✓ Database import successful")
    
    # Test backend imports
    from backend.app.core.config import settings
    print("✓ Config import successful")
    
    from backend.app.core.deps import get_database_connection
    print("✓ Dependencies import successful")
    
    from backend.app.services.trade_service import TradeService
    print("✓ Trade service import successful")
    
    from backend.app.main import app
    print("✓ Main app import successful")
    
    print("\n🎉 All imports successful! Backend should work now.")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
