"""
Main FastAPI application for InsideX
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import routes_trades, routes_companies, routes_insiders, routes_signals
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="API for insider trading signals and data",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(routes_trades.router, prefix=settings.api_v1_prefix)
app.include_router(routes_companies.router, prefix=settings.api_v1_prefix)
app.include_router(routes_insiders.router, prefix=settings.api_v1_prefix)
app.include_router(routes_signals.router, prefix=settings.api_v1_prefix)


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Welcome to InsideX API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/healthz"
    }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )