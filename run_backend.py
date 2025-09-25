#!/usr/bin/env python3
"""
Startup script for InsideX FastAPI backend
Run this from the project root directory
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    from backend.app.main import app
    
    print("Starting InsideX FastAPI backend...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    print("Health check at: http://localhost:8000/healthz")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
