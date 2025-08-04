import numpy as np
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math

class SolarPredictionEngine:
    """
    Comprehensive solar energy prediction engine for rooftop analysis
    """
    
    def __init__(self):
        # Solar panel specifications (typical residential panel)
        self.panel_specs = {
            'power_rating': 400,  # Watts per panel
            'efficiency': 0.20,   # 20% efficiency
            'area': 2.0,         # m² per panel
            'temperature_coefficient': -0.004,  # %/°C
            'system_losses': 0.15  # 15% system losses
        }
        
        # Economic parameters
        self.economic_params = {
            'electricity_rate': 0.12,  # $/kWh (adjustable by region)
            'panel_cost': 300,         # $ per panel
            'installation_cost_per_watt': 1.5,  # $/W
            'maintenance_annual': 0.01  # 1% of system cost annually
        }
        
        # Location-specific solar data (Thailand example)
        self.location_data = {
            'latitude': 13.671842,
            'longitude': 100.540148,
            'timezone': 7,  # UTC+7
            'average_ghi': 5.2,  # kWh/m²/day annual average for Thailand
            'peak_sun_hours': 5.5
        }

    def calculate_solar_irradiance(self, lat: float, lon: float, date: datetime = None) -> Dict:
        """
        Calculate solar irradiance for given location and date
        """
        if date is None:
            date = datetime.now()
            
        # Solar position calculations
        day_of_year = date.timetuple().tm_yday
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        
        # Hour angle for solar noon
        hour_angle = 0  # Solar noon
        
        # Solar elevation angle
        elevation = math.asin(
            math.sin(math.radians(lat)) * math.sin(math.radians(declination)) +
            math.cos(math.radians(lat)) * math.cos(math.radians(declination)) * math.cos(math.radians(hour_angle))
        )
        
        # Air mass calculation
        air_mass = 1 / math.sin(elevation) if elevation > 0 else 0
        
        # Direct normal irradiance (simplified model)
        dni = 900 * math.exp(-0.357 * air_mass) if air_mass > 0 else 0
        
        # Global horizontal irradiance
        ghi = dni * math.sin(elevation) if elevation > 0 else 0
        
        # Seasonal adjustment for Thailand
        seasonal_factor = 1 + 0.1 * math.cos(2 * math.pi * (day_of_year - 172) / 365)
        ghi *= seasonal_factor
        
        return {
            'ghi': max(0, ghi),  # W/m²
            'dni': max(0, dni),
            'elevation_angle': math.degrees(elevation),
            'air_mass': air_mass,
            'seasonal_factor': seasonal_factor
        }

    def calculate_roof_area(self, polygon_coords: List[Tuple[float, float]]) -> float:
        """
        Calculate roof area from polygon coordinates using Shoelace formula
        """
        n = len(polygon_coords)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            # Convert lat/lon to approximate meters (rough approximation)
            x1, y1 = polygon_coords[i][0] * 111320, polygon_coords[i][1] * 110540
            x2, y2 = polygon_coords[j][0] * 111320, polygon_coords[j][1] * 110540
            area += x1 * y2 - x2 * y1
            
        return abs(area) / 2.0  # m²

    def optimize_panel_placement(self, roof_area: float, usable_factor: float = 0.75) -> Dict:
        """
        Optimize panel placement on roof considering spacing and obstructions
        """
        usable_area = roof_area * usable_factor
        panel_area = self.panel_specs['area']
        
        # Calculate maximum panels that can fit
        max_panels = int(usable_area / panel_area)
        
        # Consider spacing between panels (10% reduction)
        optimal_panels = int(max_panels * 0.9)
        
        total_power = optimal_panels * self.panel_specs['power_rating']
        
        return {
            'roof_area': roof_area,
            'usable_area': usable_area,
            'panel_count': optimal_panels,
            'total_power_kw': total_power / 1000,
            'coverage_ratio': (optimal_panels * panel_area) / roof_area
        }

    def calculate_energy_production(self, panel_count: int, ghi: float, temperature: float = 25) -> Dict:
        """
        Calculate energy production based on panels and conditions
        """
        # Temperature derating
        temp_factor = 1 + self.panel_specs['temperature_coefficient'] * (temperature - 25)
        
        # System efficiency including losses
        system_efficiency = self.panel_specs['efficiency'] * (1 - self.panel_specs['system_losses']) * temp_factor
        
        # Daily energy production
        panel_area_total = panel_count * self.panel_specs['area']
        daily_energy_kwh = (ghi / 1000) * panel_area_total * system_efficiency * self.location_data['peak_sun_hours']
        
        # Monthly and yearly projections
        monthly_energy_kwh = daily_energy_kwh * 30
        yearly_energy_kwh = daily_energy_kwh * 365
        
        return {
            'daily_energy_kwh': daily_energy_kwh,
            'monthly_energy_kwh': monthly_energy_kwh,
            'yearly_energy_kwh': yearly_energy_kwh,
            'system_efficiency': system_efficiency,
            'temperature_factor': temp_factor
        }

    def calculate_economic_analysis(self, yearly_energy_kwh: float, panel_count: int, 
                                  monthly_consumption_kwh: float = 500) -> Dict:
        """
        Calculate economic benefits and costs
        """
        # System costs
        total_power_kw = panel_count * self.panel_specs['power_rating'] / 1000
        equipment_cost = panel_count * self.economic_params['panel_cost']
        installation_cost = total_power_kw * 1000 * self.economic_params['installation_cost_per_watt']
        total_system_cost = equipment_cost + installation_cost
        
        # Annual savings
        annual_energy_value = yearly_energy_kwh * self.economic_params['electricity_rate']
        annual_maintenance = total_system_cost * self.economic_params['maintenance_annual']
        net_annual_savings = annual_energy_value - annual_maintenance
        
        # Monthly calculations
        monthly_energy_production = yearly_energy_kwh / 12
        monthly_energy_value = monthly_energy_production * self.economic_params['electricity_rate']
        
        # Net metering calculation
        if monthly_energy_production > monthly_consumption_kwh:
            # Excess energy sold back to grid (assume 80% of retail rate)
            excess_energy = monthly_energy_production - monthly_consumption_kwh
            monthly_bill_reduction = (monthly_consumption_kwh * self.economic_params['electricity_rate'] + 
                                    excess_energy * self.economic_params['electricity_rate'] * 0.8)
        else:
            # Partial offset of electricity bill
            monthly_bill_reduction = monthly_energy_production * self.economic_params['electricity_rate']
        
        # Payback period
        payback_years = total_system_cost / net_annual_savings if net_annual_savings > 0 else float('inf')
        
        return {
            'total_system_cost': total_system_cost,
            'equipment_cost': equipment_cost,
            'installation_cost': installation_cost,
            'annual_energy_value': annual_energy_value,
            'annual_maintenance': annual_maintenance,
            'net_annual_savings': net_annual_savings,
            'monthly_energy_value': monthly_energy_value,
            'monthly_bill_reduction': monthly_bill_reduction,
            'payback_years': payback_years,
            'roi_percentage': (net_annual_savings / total_system_cost) * 100
        }

    def get_color_palette_for_value(self, value: float, min_val: float, max_val: float) -> Tuple[str, str]:
        """
        Generate color palette based on solar potential value - Orange to White
        """
        # Always use orange to white gradient regardless of value
        return '#FF8C00', '#FFFFFF'

    def analyze_rooftop(self, polygon_coords: List[Tuple[float, float]], 
                       monthly_consumption_kwh: float = 500) -> Dict:
        """
        Comprehensive rooftop solar analysis
        """
        # Calculate roof area
        roof_area = self.calculate_roof_area(polygon_coords)
        
        # Get solar irradiance
        lat, lon = polygon_coords[0][1], polygon_coords[0][0]  # Use first coordinate
        irradiance_data = self.calculate_solar_irradiance(lat, lon)
        
        # Optimize panel placement
        panel_data = self.optimize_panel_placement(roof_area)
        
        # Calculate energy production
        energy_data = self.calculate_energy_production(
            panel_data['panel_count'], 
            irradiance_data['ghi']
        )
        
        # Economic analysis
        economic_data = self.calculate_economic_analysis(
            energy_data['yearly_energy_kwh'],
            panel_data['panel_count'],
            monthly_consumption_kwh
        )
        
        # Solar potential score (0-100)
        max_possible_ghi = 1200  # W/m² theoretical maximum
        solar_potential_score = (irradiance_data['ghi'] / max_possible_ghi) * 100
        
        return {
            'roof_analysis': {
                'area_m2': roof_area,
                'coordinates': polygon_coords
            },
            'solar_irradiance': irradiance_data,
            'panel_optimization': panel_data,
            'energy_production': energy_data,
            'economic_analysis': economic_data,
            'solar_potential_score': solar_potential_score,
            'recommended_color_palette': self.get_color_palette_for_value(
                solar_potential_score, 0, 100
            )
        }

# Example usage and testing
if __name__ == '__main__':
    engine = SolarPredictionEngine()
    
    # Test with one of your polygon coordinates
    test_coords = [(100.540148,13.671842),(100.540164,13.671602),(100.540577,13.67167),(100.54055,13.671899)]
    
    result = engine.analyze_rooftop(test_coords, monthly_consumption_kwh=600)
    
    print("=== SOLAR ROOFTOP ANALYSIS ===")
    print(f"Roof Area: {result['roof_analysis']['area_m2']:.2f} m²")
    print(f"Solar Potential Score: {result['solar_potential_score']:.1f}/100")
    print(f"Recommended Panels: {result['panel_optimization']['panel_count']}")
    print(f"Yearly Energy Production: {result['energy_production']['yearly_energy_kwh']:.2f} kWh")
    print(f"Monthly Bill Reduction: ${result['economic_analysis']['monthly_bill_reduction']:.2f}")
    print(f"Payback Period: {result['economic_analysis']['payback_years']:.1f} years")
    print(f"Recommended Colors: {result['recommended_color_palette']}")
