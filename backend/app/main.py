"""
FastAPI application entry point for OpenSignal
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
    title="OpenSignal API",
    description=(
        "API for market signals from financial disclosures and transactions "
        "by influential decision-makers"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (ALLOWED_HOSTS / ALLOWED_ORIGIN_REGEX from env for Vercel)
_cors_origins = settings.ALLOWED_HOSTS
_allow_credentials = True
if _cors_origins == ["*"]:
    # Browsers reject allow_credentials with wildcard origin
    _allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX,
    allow_credentials=_allow_credentials,
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
        "message": "Welcome to OpenSignal API", 
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