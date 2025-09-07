"""
Enhanced Solar Rooftop Analysis API
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import health, analysis, docs
from src.utils.config import get_settings

# Get settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="API for analyzing solar potential of rooftops with advanced visualization",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(docs.router, prefix="/api/v1", tags=["Documentation"])


@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    """
    print(f"🚀 {settings.API_TITLE} v{settings.API_VERSION} is starting up...")
    print(f"📝 API documentation available at: /docs")
    print(f"📋 OpenAPI YAML available at: /api/v1/openapi.yaml")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    """
    print("🛑 Solar Analysis API is shutting down...")


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": "API for analyzing solar potential of rooftops",
        "docs": "/docs",
        "health": "/api/v1/health",
        "openapi_yaml": "/api/v1/openapi.yaml",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
