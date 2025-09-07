"""
Solar analysis endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
from shapely.geometry import Polygon, mapping

from src.api.models.requests import (
    SolarAnalysisRequest,
    SolarAnalysisResponse,
    MultipleRooftopsRequest,
)
from src.core.solar_prediction_engine import SolarPredictionEngine
from src.core.enhanced_solsat_system import EnhancedSolarRooftopSystem
from src.utils.helpers import convert_numpy_types

router = APIRouter()

# Initialize engines
solar_engine = SolarPredictionEngine()
enhanced_system = EnhancedSolarRooftopSystem()


def generate_overlay_data(coords, analysis_data, grid_size=30):
    """
    Generate overlay data for frontend rendering
    Returns grid values suitable for heatmap visualization on Google Maps
    """
    polygon = Polygon(coords)
    return enhanced_system.generate_overlay_grid_data(polygon, analysis_data, grid_size)


@router.post("/analyze", response_model=SolarAnalysisResponse)
async def analyze_solar_potential(request: SolarAnalysisRequest):
    """
    Analyze solar potential for a given rooftop polygon

    Parameters:
    - polygon_coordinates: List of coordinates defining the rooftop polygon
    - monthly_consumption_kwh: Monthly electricity consumption in kWh

    Returns:
    - Comprehensive solar analysis including roof area, solar potential score,
      panel optimization, energy production estimates, and economic analysis
    """
    try:
        # Convert pydantic coordinates to tuple format expected by the engine
        polygon_coords = [
            (coord.longitude, coord.latitude) for coord in request.polygon_coordinates
        ]

        # Validate polygon (minimum 3 points)
        if len(polygon_coords) < 3:
            raise HTTPException(
                status_code=400, detail="Polygon must have at least 3 coordinates"
            )

        # Run the solar analysis
        analysis_result = solar_engine.analyze_rooftop(
            polygon_coords=polygon_coords,
            monthly_consumption_kwh=request.monthly_consumption_kwh,
        )

        # Clean the result for JSON serialization
        clean_result = convert_numpy_types(analysis_result)

        return SolarAnalysisResponse(
            success=True,
            data=clean_result,
            message="Solar analysis completed successfully",
        )

    except Exception as e:
        return SolarAnalysisResponse(
            success=False, message=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze/multiple")
async def analyze_multiple_rooftops(polygons_data: List[SolarAnalysisRequest]):
    """
    Analyze multiple rooftops at once

    Parameters:
    - polygons_data: List of rooftop analysis requests

    Returns:
    - List of solar analyses for each rooftop
    """
    try:
        results = []
        total_stats = {
            "total_panels": 0,
            "total_yearly_energy": 0,
            "total_monthly_savings": 0,
            "total_system_cost": 0,
        }

        for idx, polygon_request in enumerate(polygons_data):
            # Convert coordinates
            polygon_coords = [
                (coord.longitude, coord.latitude)
                for coord in polygon_request.polygon_coordinates
            ]

            # Analyze this rooftop
            analysis = solar_engine.analyze_rooftop(
                polygon_coords=polygon_coords,
                monthly_consumption_kwh=polygon_request.monthly_consumption_kwh,
            )

            # Add to totals
            panels = analysis["panel_optimization"]["panel_count"]
            yearly_energy = analysis["energy_production"]["yearly_energy_kwh"]
            monthly_savings = analysis["economic_analysis"]["monthly_bill_reduction"]
            system_cost = analysis["economic_analysis"]["total_system_cost"]

            total_stats["total_panels"] += panels
            total_stats["total_yearly_energy"] += yearly_energy
            total_stats["total_monthly_savings"] += monthly_savings
            total_stats["total_system_cost"] += system_cost

            # Clean for JSON
            clean_analysis = convert_numpy_types(analysis)
            clean_analysis["rooftop_id"] = idx
            results.append(clean_analysis)

        # Calculate averages
        num_rooftops = len(polygons_data)
        total_stats["average_solar_score"] = (
            sum(r["solar_potential_score"] for r in results) / num_rooftops
        )
        total_stats["average_payback_years"] = (
            sum(r["economic_analysis"]["payback_years"] for r in results) / num_rooftops
        )

        return {
            "success": True,
            "rooftops_analyzed": num_rooftops,
            "individual_results": results,
            "summary_statistics": total_stats,
            "message": f"Successfully analyzed {num_rooftops} rooftops",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Multiple analysis failed: {str(e)}"
        )


@router.post("/analyze/geojson")
async def analyze_rooftops_for_map(request: MultipleRooftopsRequest):
    """
    Analyze multiple rooftops and return GeoJSON data for Google Maps
    visualization

    This endpoint is optimized for frontend map display:
    - Returns GeoJSON format for easy integration with map libraries
    - Includes color-coded polygons based on solar potential
    - Contains popup information for each rooftop
    - Lightweight data structure suitable for web applications

    Returns:
    - GeoJSON FeatureCollection with analyzed rooftop polygons
    - Each feature contains solar analysis data and visualization properties
    """
    try:
        # Convert all polygon requests to coordinate lists
        polygon_coords_list = []
        consumption_list = []

        for polygon_request in request.polygons_data:
            coords = [
                (coord.longitude, coord.latitude)
                for coord in polygon_request.polygon_coordinates
            ]
            polygon_coords_list.append(coords)
            consumption_list.append(polygon_request.monthly_consumption_kwh)

        # Analyze all rooftops using enhanced system
        analysis_results = enhanced_system.analyze_all_rooftops(
            polygon_coords_list,
            consumption_list[0],  # Use first consumption value as default
        )

        # Create GeoJSON features
        features = []

        for idx, (coords, analysis) in enumerate(
            zip(polygon_coords_list, analysis_results)
        ):
            # Create Shapely polygon for GeoJSON conversion
            polygon = Polygon(coords)

            # Determine color based on solar potential score
            score = analysis["solar_potential_score"]
            if score >= 80:
                color = "#00FF00"  # Green - Excellent
                opacity = 0.8
            elif score >= 60:
                color = "#FFFF00"  # Yellow - Good
                opacity = 0.7
            elif score >= 40:
                color = "#FFA500"  # Orange - Fair
                opacity = 0.6
            else:
                color = "#FF0000"  # Red - Poor
                opacity = 0.5

            # Create popup content using existing method
            popup_content = enhanced_system.create_info_popup(analysis)

            # Create GeoJSON feature with overlay data
            feature = {
                "type": "Feature",
                "properties": {
                    "rooftop_id": idx,
                    "solar_potential_score": float(analysis["solar_potential_score"]),
                    "color": color,
                    "opacity": opacity,
                    "popup_content": popup_content,
                    "panel_count": int(analysis["panel_optimization"]["panel_count"]),
                    "yearly_energy_kwh": float(
                        analysis["energy_production"]["yearly_energy_kwh"]
                    ),
                    "monthly_savings": float(
                        analysis["economic_analysis"]["monthly_bill_reduction"]
                    ),
                    "payback_years": float(
                        analysis["economic_analysis"]["payback_years"]
                    ),
                    "system_cost": float(
                        analysis["economic_analysis"]["total_system_cost"]
                    ),
                    "roof_area_m2": float(analysis["roof_analysis"]["area_m2"]),
                    # Add overlay data directly to feature properties
                    "overlay_data": generate_overlay_data(coords, analysis),
                },
                "geometry": mapping(polygon),
            }
            features.append(feature)

        # Calculate summary statistics
        total_panels = sum(
            int(r["panel_optimization"]["panel_count"]) for r in analysis_results
        )
        total_yearly_energy = sum(
            float(r["energy_production"]["yearly_energy_kwh"]) for r in analysis_results
        )
        total_monthly_savings = sum(
            float(r["economic_analysis"]["monthly_bill_reduction"])
            for r in analysis_results
        )
        avg_solar_score = sum(
            float(r["solar_potential_score"]) for r in analysis_results
        ) / len(analysis_results)
        total_system_cost = sum(
            float(r["economic_analysis"]["total_system_cost"]) for r in analysis_results
        )

        # Calculate map center (centroid of all polygons)
        if features:
            all_coords = []
            for coords in polygon_coords_list:
                all_coords.extend(coords)

            center_lng = sum(coord[0] for coord in all_coords) / len(all_coords)
            center_lat = sum(coord[1] for coord in all_coords) / len(all_coords)
            map_center = {"lat": center_lat, "lng": center_lng}
        else:
            map_center = {"lat": 0, "lng": 0}

        # Return GeoJSON with metadata
        return {
            "success": True,
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_rooftops": len(analysis_results),
                "total_panels": total_panels,
                "total_yearly_energy_kwh": total_yearly_energy,
                "total_monthly_savings": total_monthly_savings,
                "average_solar_score": round(avg_solar_score, 1),
                "total_system_cost": total_system_cost,
                "map_center": map_center,
                "zoom_level": 18,
            },
            "message": (
                f"Successfully analyzed {len(analysis_results)} rooftops "
                "for map visualization"
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"GeoJSON analysis failed: {str(e)}"
        )


@router.get("/overlay/{rooftop_id}")
async def get_overlay_data(rooftop_id: int, coords: str = None):
    """
    Get overlay data for a specific rooftop as numerical grid values

    This endpoint returns overlay data as a grid of solar potential values
    that can be rendered as heatmap overlay on Google Maps.

    Parameters:
    - rooftop_id: ID of the rooftop
    - coords: JSON string of polygon coordinates (optional, for demo)

    Returns:
    - Grid data with solar potential values and rendering instructions
    """
    try:
        if coords:
            # Parse coordinates from query parameter (for demo purposes)
            import json

            coords_list = json.loads(coords)
            polygon = Polygon([(c["lng"], c["lat"]) for c in coords_list])

            # Create mock analysis data for demo
            mock_analysis = {
                "solar_potential_score": 75.0,
                "roof_analysis": {"area_m2": 100.0},
                "panel_optimization": {"panel_count": 20},
                "energy_production": {"yearly_energy_kwh": 8000},
                "economic_analysis": {
                    "monthly_bill_reduction": 300,
                    "payback_years": 8.5,
                    "total_system_cost": 40000,
                },
            }

            overlay_data = enhanced_system.generate_overlay_grid_data(
                polygon, mock_analysis, grid_size=30
            )
            overlay_data["rooftop_id"] = rooftop_id

            return overlay_data
        else:
            # Return structured response for integration guidance
            return {
                "error": "No coordinate data provided",
                "usage": (
                    'Add ?coords=[{"lng":100.540148,"lat":13.671842},...] '
                    "to get overlay data"
                ),
                "example_response": {
                    "rooftop_id": rooftop_id,
                    "grid_size": 30,
                    "bounds": {
                        "north": 13.672,
                        "south": 13.671,
                        "east": 100.541,
                        "west": 100.540,
                    },
                    "values": "2D array of solar potential values (0-1)",
                    "color_mapping": {
                        "colors": {
                            "excellent": "#00FF00",
                            "good": "#FFFF00",
                            "fair": "#FFA500",
                            "poor": "#FF6B6B",
                        }
                    },
                },
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate overlay data: {str(e)}"
        )
