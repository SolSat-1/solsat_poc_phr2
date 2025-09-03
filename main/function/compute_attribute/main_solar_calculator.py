#!/usr/bin/env python3
"""
Enhanced Solar Calculator with Adaptive Buffering
=================================================

This module integrates the enhanced rooftop calculator with adaptive buffering methods
for ERA5 small polygon data retrieval, following the scientific methodologies outlined
in the reference documentation.

Key Features:
- Michalsky algorithm for solar position calculations
- Ineichen-Perez clear sky irradiance modeling
- Adaptive buffering for small polygon ERA5 data retrieval
- Comprehensive rooftop solar potential analysis

Author: SolSat POC Team
Date: 2025
"""

import sys
import os
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_rooftop_calculator import EnhancedRooftopCalculator
    from enhanced_gee_small_polygon_handler import EnhancedGEESmallPolygonHandler
    from gee_solar_data import GEESolarData
except ImportError as e:
    logging.warning(f"Import error: {e}. Some features may not be available.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSolarSystem:
    """
    Enhanced Solar System integrating rooftop calculator with adaptive buffering.
    
    This class combines the enhanced rooftop calculator with the adaptive buffering
    method for ERA5 small polygon data retrieval, providing comprehensive solar
    potential analysis for rooftop-scale applications.
    """
    
    def __init__(self, 
                 use_satellite_data: bool = True,
                 use_adaptive_buffering: bool = True,
                 thailand_optimized: bool = True):
        """
        Initialize the Enhanced Solar System.
        
        Args:
            use_satellite_data: Whether to use ERA5 satellite data
            use_adaptive_buffering: Whether to use adaptive buffering for small polygons
            thailand_optimized: Whether to use Thailand-optimized parameters
        """
        self.use_satellite_data = use_satellite_data
        self.use_adaptive_buffering = use_adaptive_buffering
        self.thailand_optimized = thailand_optimized
        
        # Initialize components
        self._initialize_components()
        
        # Thailand-optimized parameters
        if thailand_optimized:
            self._setup_thailand_parameters()
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            # Enhanced rooftop calculator
            self.rooftop_calculator = EnhancedRooftopCalculator(
                use_satellite_data=self.use_satellite_data
            )
            logger.info("Enhanced rooftop calculator initialized")
            
            # Adaptive buffering handler for small polygons
            if self.use_adaptive_buffering:
                self.polygon_handler = EnhancedGEESmallPolygonHandler()
                logger.info("Adaptive buffering handler initialized")
            
            # Google Earth Engine data handler
            if self.use_satellite_data:
                self.gee_handler = GEESolarData()
                logger.info("Google Earth Engine handler initialized")
                
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            # Fallback to basic functionality
            self.use_satellite_data = False
            self.use_adaptive_buffering = False
    
    def _setup_thailand_parameters(self):
        """Setup Thailand-optimized atmospheric and rooftop parameters."""
        # Thailand-specific atmospheric parameters
        thailand_atmospheric = {
            'altitude': 0.0,                    # Bangkok sea level
            'pressure': 101325,                 # Standard atmospheric pressure (Pa)
            'water_vapor': 2.5,                 # cm (tropical climate)
            'aerosol_optical_depth': 0.15,      # Urban Thailand
            'ozone': 0.3,                       # atm-cm (tropical)
            'albedo': 0.2                       # Ground reflectance
        }
        
        # Thailand-specific rooftop parameters
        thailand_rooftop = {
            'default_tilt': 15,                 # Optimal for Thailand latitude (~13-20°N)
            'default_azimuth': 180,             # South-facing
            'shading_factor': 0.95,             # 5% shading losses
            'soiling_factor': 0.98,             # 2% soiling losses (tropical climate)
            'spectral_factor': 1.02             # 2% spectral enhancement
        }
        
        # Update calculator parameters
        if hasattr(self, 'rooftop_calculator'):
            self.rooftop_calculator.atmospheric_params.update(thailand_atmospheric)
            self.rooftop_calculator.rooftop_params.update(thailand_rooftop)
            logger.info("Thailand-optimized parameters applied")
    
    def analyze_rooftop_potential(self, 
                                polygon_coords: List[Tuple[float, float]],
                                monthly_consumption_kwh: float = 600,
                                panel_efficiency: float = 0.17,
                                system_losses: float = 0.15) -> Dict[str, Any]:
        """
        Comprehensive rooftop solar potential analysis.
        
        Args:
            polygon_coords: List of (longitude, latitude) coordinates
            monthly_consumption_kwh: Monthly electricity consumption in kWh
            panel_efficiency: Solar panel efficiency (default 17%)
            system_losses: System losses factor (default 15%)
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        logger.info("Starting comprehensive rooftop solar potential analysis")
        
        try:
            # Calculate polygon centroid
            centroid_lon, centroid_lat = self._calculate_centroid(polygon_coords)
            
            # Calculate polygon area
            polygon_area_m2 = self._calculate_polygon_area(polygon_coords)
            
            # Enhanced irradiance calculation with adaptive buffering
            irradiance_result = self._get_enhanced_irradiance(
                centroid_lat, centroid_lon, polygon_coords
            )
            
            # Rooftop-specific calculations
            rooftop_analysis = self._analyze_rooftop_characteristics(
                polygon_coords, irradiance_result
            )
            
            # Energy production calculations
            energy_analysis = self._calculate_energy_production(
                irradiance_result, rooftop_analysis, polygon_area_m2,
                panel_efficiency, system_losses
            )
            
            # Economic analysis
            economic_analysis = self._calculate_economics(
                energy_analysis, monthly_consumption_kwh
            )
            
            # Compile comprehensive results
            results = {
                'location': {
                    'centroid_latitude': centroid_lat,
                    'centroid_longitude': centroid_lon,
                    'polygon_area_m2': polygon_area_m2,
                    'polygon_coords': polygon_coords
                },
                'irradiance_analysis': irradiance_result,
                'rooftop_analysis': rooftop_analysis,
                'energy_analysis': energy_analysis,
                'economic_analysis': economic_analysis,
                'system_parameters': {
                    'panel_efficiency': panel_efficiency,
                    'system_losses': system_losses,
                    'monthly_consumption_kwh': monthly_consumption_kwh
                },
                'methodology': {
                    'solar_position': 'Michalsky algorithm',
                    'clear_sky_model': 'Ineichen-Perez',
                    'air_mass_formula': 'Kasten-Young',
                    'adaptive_buffering': self.use_adaptive_buffering,
                    'satellite_data': self.use_satellite_data
                }
            }
            
            logger.info("Rooftop solar potential analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in rooftop potential analysis: {e}")
            return {
                'error': str(e),
                'success': False,
                'recommendations': [
                    'Check polygon coordinates format',
                    'Verify Google Earth Engine authentication',
                    'Ensure all required modules are available'
                ]
            }
    
    def _get_enhanced_irradiance(self, lat: float, lon: float, 
                               polygon_coords: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Get enhanced irradiance data using adaptive buffering if needed."""
        try:
            # First try enhanced rooftop calculator
            if hasattr(self, 'rooftop_calculator'):
                result = self.rooftop_calculator.calculate_enhanced_irradiance(
                    lat=lat, lon=lon, polygon_coords=polygon_coords
                )
                if result.get('success', True):
                    return result
            
            # Fallback to adaptive buffering method
            if self.use_adaptive_buffering and hasattr(self, 'polygon_handler'):
                logger.info("Using adaptive buffering for small polygon")
                buffer_result = self.polygon_handler.get_enhanced_era5_data(
                    polygon_coords, preferred_method='adaptive_buffering'
                )
                
                if buffer_result.get('success'):
                    # Convert to enhanced calculator format
                    return {
                        'final_poa_irradiance': buffer_result.get('ghi_kwh_per_m2_day', 0) * 1000 / 24,  # Convert to W/m²
                        'daily_energy_kwh_per_m2': buffer_result.get('ghi_kwh_per_m2_day', 0),
                        'satellite_data_used': True,
                        'method_used': buffer_result.get('method_used'),
                        'scientific_validity': buffer_result.get('method_info', {}).get('scientific_validity', 'Medium'),
                        'success': True
                    }
            
            # Final fallback to basic calculation
            logger.warning("Using basic solar calculation as fallback")
            return self._basic_solar_calculation(lat, lon)
            
        except Exception as e:
            logger.error(f"Error in enhanced irradiance calculation: {e}")
            return self._basic_solar_calculation(lat, lon)
    
    def _basic_solar_calculation(self, lat: float, lon: float) -> Dict[str, Any]:
        """Basic solar calculation fallback."""
        # Simple clear sky estimation for Thailand
        # Based on typical values for tropical regions
        daily_ghi_kwh_m2 = 4.5  # Typical for Thailand
        peak_irradiance = daily_ghi_kwh_m2 * 1000 / 8  # Assume 8 peak sun hours
        
        return {
            'final_poa_irradiance': peak_irradiance,
            'daily_energy_kwh_per_m2': daily_ghi_kwh_m2,
            'satellite_data_used': False,
            'method_used': 'basic_calculation',
            'scientific_validity': 'Low',
            'success': True
        }
    
    def _analyze_rooftop_characteristics(self, polygon_coords: List[Tuple[float, float]], 
                                       irradiance_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze rooftop-specific characteristics."""
        try:
            # Calculate roof orientation from polygon geometry
            roof_azimuth = self._estimate_roof_orientation(polygon_coords)
            
            # Estimate optimal tilt for location
            centroid_lat = self._calculate_centroid(polygon_coords)[1]
            optimal_tilt = min(abs(centroid_lat), 30)  # Simple rule for tropical regions
            
            # Calculate shading factors based on roof orientation
            shading_factor = self._calculate_shading_factor(roof_azimuth)
            
            return {
                'estimated_roof_azimuth': roof_azimuth,
                'optimal_tilt_angle': optimal_tilt,
                'shading_factor': shading_factor,
                'soiling_factor': 0.98,  # Thailand tropical climate
                'spectral_factor': 1.02,
                'quality_assessment': {
                    'roof_suitability': 'Good' if shading_factor > 0.9 else 'Moderate',
                    'orientation_score': self._score_orientation(roof_azimuth),
                    'tilt_score': self._score_tilt(optimal_tilt, centroid_lat)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in rooftop analysis: {e}")
            return {
                'estimated_roof_azimuth': 180,  # Default south-facing
                'optimal_tilt_angle': 15,       # Default for Thailand
                'shading_factor': 0.95,
                'soiling_factor': 0.98,
                'spectral_factor': 1.02,
                'quality_assessment': {
                    'roof_suitability': 'Unknown',
                    'orientation_score': 0.8,
                    'tilt_score': 0.9
                }
            }
    
    def _calculate_energy_production(self, irradiance_result: Dict[str, Any],
                                   rooftop_analysis: Dict[str, Any],
                                   area_m2: float,
                                   panel_efficiency: float,
                                   system_losses: float) -> Dict[str, Any]:
        """Calculate energy production with all factors."""
        try:
            # Base daily energy from irradiance
            daily_energy_kwh_per_m2 = irradiance_result.get('daily_energy_kwh_per_m2', 4.5)
            
            # Apply rooftop-specific factors
            shading_factor = rooftop_analysis.get('shading_factor', 0.95)
            soiling_factor = rooftop_analysis.get('soiling_factor', 0.98)
            spectral_factor = rooftop_analysis.get('spectral_factor', 1.02)
            
            # Calculate effective daily energy
            effective_daily_kwh_per_m2 = (
                daily_energy_kwh_per_m2 * 
                shading_factor * 
                soiling_factor * 
                spectral_factor
            )
            
            # Calculate system energy production
            usable_area_factor = 0.8  # Account for spacing, inverters, etc.
            usable_area_m2 = area_m2 * usable_area_factor
            
            daily_system_energy_kwh = (
                effective_daily_kwh_per_m2 * 
                usable_area_m2 * 
                panel_efficiency * 
                (1 - system_losses)
            )
            
            # Annual calculations
            annual_energy_kwh = daily_system_energy_kwh * 365
            
            # Monthly breakdown (simplified seasonal variation)
            monthly_energy_kwh = self._calculate_monthly_breakdown(daily_system_energy_kwh)
            
            return {
                'daily_energy_kwh_per_m2': daily_energy_kwh_per_m2,
                'effective_daily_kwh_per_m2': effective_daily_kwh_per_m2,
                'usable_roof_area_m2': usable_area_m2,
                'daily_system_energy_kwh': daily_system_energy_kwh,
                'monthly_system_energy_kwh': daily_system_energy_kwh * 30.44,  # Average month
                'annual_system_energy_kwh': annual_energy_kwh,
                'monthly_breakdown': monthly_energy_kwh,
                'performance_factors': {
                    'shading_factor': shading_factor,
                    'soiling_factor': soiling_factor,
                    'spectral_factor': spectral_factor,
                    'panel_efficiency': panel_efficiency,
                    'system_losses': system_losses,
                    'usable_area_factor': usable_area_factor
                }
            }
            
        except Exception as e:
            logger.error(f"Error in energy production calculation: {e}")
            return {
                'error': str(e),
                'daily_system_energy_kwh': 0,
                'annual_system_energy_kwh': 0
            }
    
    def _calculate_economics(self, energy_analysis: Dict[str, Any],
                           monthly_consumption_kwh: float) -> Dict[str, Any]:
        """Calculate economic analysis."""
        try:
            annual_production_kwh = energy_analysis.get('annual_system_energy_kwh', 0)
            monthly_production_kwh = energy_analysis.get('monthly_system_energy_kwh', 0)
            
            # Thailand electricity rates (approximate)
            electricity_rate_thb_per_kwh = 4.5  # THB per kWh
            
            # Calculate savings
            monthly_savings_potential = min(monthly_production_kwh, monthly_consumption_kwh)
            annual_savings_thb = monthly_savings_potential * 12 * electricity_rate_thb_per_kwh
            
            # Calculate excess energy
            monthly_excess_kwh = max(0, monthly_production_kwh - monthly_consumption_kwh)
            
            # Solar score calculation
            consumption_coverage = min(100, (monthly_production_kwh / monthly_consumption_kwh) * 100)
            solar_score = min(100, consumption_coverage * 0.8 + 20)  # Base score + coverage
            
            return {
                'monthly_production_kwh': monthly_production_kwh,
                'monthly_consumption_kwh': monthly_consumption_kwh,
                'monthly_savings_potential_kwh': monthly_savings_potential,
                'monthly_excess_kwh': monthly_excess_kwh,
                'annual_savings_thb': annual_savings_thb,
                'consumption_coverage_percent': consumption_coverage,
                'solar_potential_score': solar_score,
                'electricity_rate_thb_per_kwh': electricity_rate_thb_per_kwh,
                'payback_analysis': {
                    'estimated_system_cost_thb': annual_production_kwh * 50,  # Rough estimate
                    'annual_savings_thb': annual_savings_thb,
                    'simple_payback_years': (annual_production_kwh * 50) / max(annual_savings_thb, 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in economic calculation: {e}")
            return {
                'error': str(e),
                'solar_potential_score': 0
            }
    
    # Utility methods
    def _calculate_centroid(self, coords: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate polygon centroid."""
        if not coords:
            return 0.0, 0.0
        
        lon_sum = sum(coord[0] for coord in coords)
        lat_sum = sum(coord[1] for coord in coords)
        n = len(coords)
        
        return lon_sum / n, lat_sum / n
    
    def _calculate_polygon_area(self, coords: List[Tuple[float, float]]) -> float:
        """Calculate polygon area using Shoelace formula."""
        if len(coords) < 3:
            return 0.0
        
        # Ensure polygon is closed
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        
        # Shoelace formula
        area = 0.0
        for i in range(len(coords) - 1):
            area += coords[i][0] * coords[i + 1][1]
            area -= coords[i + 1][0] * coords[i][1]
        
        area = abs(area) / 2.0
        
        # Convert from degrees to square meters (approximate)
        # This is a rough approximation for small areas
        lat = self._calculate_centroid(coords)[1]
        meters_per_degree_lat = 111320
        meters_per_degree_lon = 111320 * math.cos(math.radians(lat))
        
        area_m2 = area * meters_per_degree_lat * meters_per_degree_lon
        
        return area_m2
    
    def _estimate_roof_orientation(self, coords: List[Tuple[float, float]]) -> float:
        """Estimate roof orientation from polygon geometry."""
        if len(coords) < 3:
            return 180  # Default south-facing
        
        # Find the longest edge (likely the main roof orientation)
        max_length = 0
        best_azimuth = 180
        
        for i in range(len(coords)):
            j = (i + 1) % len(coords)
            
            # Calculate edge vector
            dx = coords[j][0] - coords[i][0]
            dy = coords[j][1] - coords[i][1]
            
            # Calculate length
            length = math.sqrt(dx**2 + dy**2)
            
            if length > max_length:
                max_length = length
                # Calculate azimuth (0° = North, 90° = East, 180° = South, 270° = West)
                azimuth = math.degrees(math.atan2(dx, dy))
                if azimuth < 0:
                    azimuth += 360
                
                # Convert to solar azimuth (perpendicular to roof edge)
                best_azimuth = (azimuth + 90) % 360
        
        return best_azimuth
    
    def _calculate_shading_factor(self, roof_azimuth: float) -> float:
        """Calculate shading factor based on roof orientation."""
        # Optimal orientation is south (180°)
        deviation = abs(roof_azimuth - 180)
        if deviation > 180:
            deviation = 360 - deviation
        
        # Shading factor decreases with deviation from south
        if deviation <= 45:
            return 0.95  # Minimal shading
        elif deviation <= 90:
            return 0.85  # Moderate shading
        else:
            return 0.70  # Significant shading
    
    def _score_orientation(self, azimuth: float) -> float:
        """Score roof orientation (0-1 scale)."""
        deviation = abs(azimuth - 180)
        if deviation > 180:
            deviation = 360 - deviation
        
        return max(0.5, 1.0 - deviation / 180)
    
    def _score_tilt(self, tilt: float, latitude: float) -> float:
        """Score roof tilt (0-1 scale)."""
        optimal_tilt = abs(latitude)
        deviation = abs(tilt - optimal_tilt)
        
        return max(0.7, 1.0 - deviation / 45)
    
    def _calculate_monthly_breakdown(self, daily_kwh: float) -> List[float]:
        """Calculate monthly energy breakdown with seasonal variation."""
        # Thailand seasonal factors (dry season higher, rainy season lower)
        monthly_factors = [
            1.1,   # Jan - dry season
            1.1,   # Feb - dry season
            1.05,  # Mar - hot season
            1.0,   # Apr - hot season
            0.95,  # May - rainy season starts
            0.85,  # Jun - rainy season
            0.8,   # Jul - rainy season
            0.8,   # Aug - rainy season
            0.85,  # Sep - rainy season
            0.9,   # Oct - rainy season ends
            1.0,   # Nov - cool season
            1.05   # Dec - cool season
        ]
        
        days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        return [daily_kwh * days * factor for days, factor in zip(days_per_month, monthly_factors)]


# def main():
#     """Main function for testing the enhanced solar system."""
#     # Test coordinates (Bangkok area rooftop)
#     test_coords = [
#         (100.540148, 13.671842),
#         (100.540164, 13.671602),
#         (100.540577, 13.67167),
#         (100.54055, 13.671899)
#     ]
    
#     # Initialize enhanced solar system
#     solar_system = EnhancedSolarSystem(
#         use_satellite_data=True,
#         use_adaptive_buffering=True,
#         thailand_optimized=True
#     )
    
#     # Analyze rooftop potential
#     print("Analyzing rooftop solar potential...")
#     result = solar_system.analyze_rooftop_potential(
#         polygon_coords=test_coords,
#         monthly_consumption_kwh=600
#     )
    
#     # Display results
#     if result.get('success', True):
#         print("\n=== ROOFTOP SOLAR ANALYSIS RESULTS ===")
#         print(f"Location: {result['location']['centroid_latitude']:.6f}°N, {result['location']['centroid_longitude']:.6f}°E")
#         print(f"Roof Area: {result['location']['polygon_area_m2']:.1f} m²")
        
#         energy = result['energy_analysis']
#         print(f"\nDaily Energy Production: {energy['daily_system_energy_kwh']:.2f} kWh")
#         print(f"Monthly Energy Production: {energy['monthly_system_energy_kwh']:.1f} kWh")
#         print(f"Annual Energy Production: {energy['annual_system_energy_kwh']:.0f} kWh")
        
#         economics = result['economic_analysis']
#         print(f"\nSolar Potential Score: {economics['solar_potential_score']:.1f}/100")
#         print(f"Monthly Consumption Coverage: {economics['consumption_coverage_percent']:.1f}%")
#         print(f"Annual Savings: {economics['annual_savings_thb']:.0f} THB")
        
#         methodology = result['methodology']
#         print(f"\nMethodology:")
#         print(f"- Solar Position: {methodology['solar_position']}")
#         print(f"- Clear Sky Model: {methodology['clear_sky_model']}")
#         print(f"- Adaptive Buffering: {methodology['adaptive_buffering']}")
#         print(f"- Satellite Data: {methodology['satellite_data']}")
        
#     else:
#         print(f"Analysis failed: {result.get('error')}")
#         print("Recommendations:", result.get('recommendations', []))


# if __name__ == "__main__":
#     main()
