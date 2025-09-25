#!/usr/bin/env python3
"""
Debug script to test backend imports and startup
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🔍 Testing backend imports...")

try:
    # Test individual imports
    print("1. Testing config import...")
    from backend.app.core.config import settings
    print("   ✅ Config imported successfully")
    
    print("2. Testing deps import...")
    from backend.app.core.deps import get_database
    print("   ✅ Dependencies imported successfully")
    
    print("3. Testing models import...")
    from backend.app.models.trade import TradeResponse, TradeQuery
    print("   ✅ Trade models imported successfully")
    
    print("4. Testing services import...")
    from backend.app.services.trade_service import TradeService
    print("   ✅ Trade service imported successfully")
    
    print("5. Testing API routes import...")
    from backend.app.api.routes_trades import router as trades_router
    print("   ✅ Trades router imported successfully")
    
    from backend.app.api.routes_companies import router as companies_router
    print("   ✅ Companies router imported successfully")
    
    from backend.app.api.routes_insiders import router as insiders_router
    print("   ✅ Insiders router imported successfully")
    
    print("6. Testing main app import...")
    from backend.app.main import app
    print("   ✅ Main app imported successfully")
    
    print("\n🎉 All imports successful! Backend should work now.")
    
    # Test if we can create the app
    print("\n🚀 Testing FastAPI app creation...")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    
    print("\n✅ Backend is ready to run!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
