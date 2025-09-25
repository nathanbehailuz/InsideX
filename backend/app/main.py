"""
FastAPI application entry point for InsideX
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes_trades import router as trades_router
from backend.app.api.routes_companies import router as companies_router
from backend.app.api.routes_insiders import router as insiders_router
from backend.app.api.routes_signals import router as signals_router
from backend.app.core.config import settings

# Create FastAPI instance
app = FastAPI(
    title="InsideX API",
    description="API for insider trading signals and data analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/healthz", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "ok"})

# Include routers
app.include_router(trades_router, prefix="/api/v1", tags=["trades"])
app.include_router(companies_router, prefix="/api/v1", tags=["companies"]) 
app.include_router(insiders_router, prefix="/api/v1", tags=["insiders"])
app.include_router(signals_router, prefix="/api/v1", tags=["signals"])

@app.get("/", tags=["root"])
async def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to InsideX API", 
        "docs": "/docs",
        "health": "/healthz"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )