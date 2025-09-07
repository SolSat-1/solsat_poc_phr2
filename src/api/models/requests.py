"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class PolygonCoordinate(BaseModel):
    """Single coordinate point for polygon definition"""

    longitude: float = Field(..., description="Longitude coordinate")
    latitude: float = Field(..., description="Latitude coordinate")


class SolarAnalysisRequest(BaseModel):
    """Request model for solar analysis"""

    polygon_coordinates: List[PolygonCoordinate] = Field(
        ...,
        description="List of polygon coordinates defining the rooftop area",
        min_items=3,
    )
    monthly_consumption_kwh: float = Field(
        500, description="Monthly electricity consumption in kWh", gt=0
    )


class SolarAnalysisResponse(BaseModel):
    """Response model for solar analysis results"""

    success: bool
    data: Dict[str, Any] = None
    message: str = None


class MultipleRooftopsRequest(BaseModel):
    """Request model for analyzing multiple rooftops"""

    polygons_data: List[SolarAnalysisRequest] = Field(
        ..., description="List of rooftop polygons with their consumption data"
    )
