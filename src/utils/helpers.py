"""
Helper functions for the application
"""

import numpy as np
from typing import Any, Dict, List, Union


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to native Python types for JSON serialization

    Args:
        obj: Object that may contain numpy types

    Returns:
        Object with numpy types converted to Python native types
    """
    if hasattr(obj, "dtype"):
        return obj.item()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def validate_coordinates(coords: List[tuple]) -> bool:
    """
    Validate that coordinates form a proper polygon

    Args:
        coords: List of (longitude, latitude) tuples

    Returns:
        True if coordinates are valid, False otherwise
    """
    if len(coords) < 3:
        return False

    # Check if coordinates are numeric
    for coord in coords:
        if len(coord) != 2:
            return False
        try:
            float(coord[0])  # longitude
            float(coord[1])  # latitude
        except (ValueError, TypeError):
            return False

    return True


def calculate_polygon_area(coords: List[tuple]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula

    Args:
        coords: List of (longitude, latitude) tuples

    Returns:
        Area in square degrees (approximate)
    """
    if len(coords) < 3:
        return 0.0

    x_coords = [coord[0] for coord in coords]
    y_coords = [coord[1] for coord in coords]

    # Shoelace formula
    area = 0.0
    n = len(coords)

    for i in range(n):
        j = (i + 1) % n
        area += x_coords[i] * y_coords[j]
        area -= x_coords[j] * y_coords[i]

    return abs(area) / 2.0


def format_currency(amount: float) -> str:
    """
    Format amount as currency string

    Args:
        amount: Numeric amount

    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def format_energy(kwh: float) -> str:
    """
    Format energy amount with appropriate units

    Args:
        kwh: Energy in kWh

    Returns:
        Formatted energy string
    """
    if kwh >= 1000:
        return f"{kwh / 1000:.1f} MWh"
    else:
        return f"{kwh:.1f} kWh"
