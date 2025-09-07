"""
Health check endpoint
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns the current status of the API service
    """
    return {"status": "healthy", "message": "Solar Analysis API is running"}
