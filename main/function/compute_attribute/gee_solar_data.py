import ee
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

class GEESolarDataRetriever:
    """
    Google Earth Engine Solar Data Retrieval System
    Fetches real satellite data for solar irradiance analysis
    """
    
    def __init__(self):
        """Initialize GEE authentication and datasets"""
        self.authenticate_gee()
        self.initialize_datasets()
        
    def authenticate_gee(self):
        """Authenticate with Google Earth Engine using service account"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Build service account info from environment variables
            service_account_info = {
                "type": os.getenv("GOOGLE_TYPE"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
                "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
            }
            
            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=["https://www.googleapis.com/auth/earthengine"]
            )
            
            # Initialize Earth Engine
            ee.Initialize(credentials)
            print("✅ Google Earth Engine authentication successful!")
            
        except Exception as e:
            print(f"❌ GEE Authentication failed: {str(e)}")
            raise
    
    def initialize_datasets(self):
        """Initialize commonly used Earth Engine datasets"""
        try:
            # ERA5 reanalysis data for weather and solar radiation
            self.era5_daily = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
            
            # MODIS Terra Daily Surface Reflectance
            self.modis_terra = ee.ImageCollection("MODIS/061/MOD09GA")
            
            # Landsat 8 for surface reflectance (optional)
            self.landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            
            print("✅ Earth Engine datasets initialized successfully!")
            
        except Exception as e:
            print(f"❌ Dataset initialization failed: {str(e)}")
            raise
    
    def create_polygon_geometry(self, polygon_coords: List[Tuple[float, float]]) -> ee.Geometry:
        """Convert polygon coordinates to Earth Engine geometry"""
        # Convert to GEE format: [[lon, lat], [lon, lat], ...]
        gee_coords = [[coord[0], coord[1]] for coord in polygon_coords]
        return ee.Geometry.Polygon([gee_coords])
    
    def get_solar_irradiance_data(self, polygon_coords: List[Tuple[float, float]], 
                                 start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch solar irradiance data from ERA5 dataset
        
        Args:
            polygon_coords: List of (longitude, latitude) tuples
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
        """
        try:
            # Set default date range (last 6 months for better data availability)
            if not start_date:
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Create geometry
            geometry = self.create_polygon_geometry(polygon_coords)
            
            # Filter ERA5 data
            solar_data = (self.era5_daily
                         .filterDate(start_date, end_date)
                         .filterBounds(geometry))
            
            # Select solar radiation band
            solar_bands = solar_data.select([
                'surface_solar_radiation_downwards_sum',  # Solar radiation
            ])
            
            # Calculate statistics over the region
            stats = solar_bands.mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=11132,  # ~10km resolution
                maxPixels=1e9
            )
            
            # Get the computed values
            result = stats.getInfo()
            
            # Convert from J/m² to kWh/m²/day
            solar_radiation_j = result.get('surface_solar_radiation_downwards_sum', 0)
            ghi_kwh_per_day = solar_radiation_j / 3600000 if solar_radiation_j else 0  # J to kWh conversion
            
            # Estimate clear sky (assume 20% higher than actual for Thailand)
            clear_sky_ghi = ghi_kwh_per_day * 1.2
            
            return {
                'ghi_kwh_per_m2_day': ghi_kwh_per_day,
                'clear_sky_ghi_kwh_per_m2_day': clear_sky_ghi,
                'diffuse_fraction': 0.3,  # Typical value for Thailand
                'cloud_impact_factor': ghi_kwh_per_day / max(clear_sky_ghi, 0.1),
                'data_source': 'ERA5',
                'date_range': f"{start_date} to {end_date}",
                'raw_data': result
            }
            
        except Exception as e:
            print(f"❌ Error fetching solar irradiance data: {str(e)}")
            return None
    
    def get_weather_data(self, polygon_coords: List[Tuple[float, float]], 
                        start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch weather data from ERA5 dataset
        """
        try:
            # Set default date range
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Create geometry
            geometry = self.create_polygon_geometry(polygon_coords)
            
            # Filter ERA5 data
            weather_data = (self.era5_daily
                           .filterDate(start_date, end_date)
                           .filterBounds(geometry))
            
            print('weather_data', weather_data)
            # Select relevant weather bands
            weather_bands = weather_data.select([
                'temperature_2m',           # 2m temperature
                'total_precipitation_sum',  # Total precipitation
                'surface_solar_radiation_downwards_sum',  # Solar radiation
            ])
            
            # Calculate statistics
            stats = weather_bands.mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=11132,
                maxPixels=1e9
            )
            
            result = stats.getInfo()
            
            # Convert units with proper None handling
            temp_kelvin = result.get('temperature_2m')
            temp_celsius = (temp_kelvin - 273.15) if temp_kelvin is not None else 25.0  # Default to 25°C
            
            precipitation = result.get('total_precipitation_sum')
            precipitation_mm = (precipitation * 1000) if precipitation is not None else 0.0  # m to mm
            
            solar_radiation = result.get('surface_solar_radiation_downwards_sum')
            solar_radiation_kwh = (solar_radiation / 3600000) if solar_radiation is not None else 0.0  # J/m² to kWh/m²
            
            return {
                'average_temperature_celsius': temp_celsius,
                'total_precipitation_mm': precipitation_mm,
                'solar_radiation_kwh_per_m2': solar_radiation_kwh,
                'data_source': 'ERA5',
                'date_range': f"{start_date} to {end_date}",
                'raw_data': result
            }
            
        except Exception as e:
            print(f"❌ Error fetching weather data: {str(e)}")
            return None
    
    def get_monthly_solar_data(self, polygon_coords: List[Tuple[float, float]], 
                              year: int = None) -> Dict:
        """
        Get monthly solar irradiance data for a specific year
        """
        if not year:
            year = datetime.now().year - 1  # Previous year
        
        monthly_data = {}
        
        for month in range(1, 13):
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            
            month_data = self.get_solar_irradiance_data(
                polygon_coords, start_date, end_date
            )
            
            if month_data:
                monthly_data[f"month_{month:02d}"] = month_data
        
        return {
            'year': year,
            'monthly_data': monthly_data,
            'annual_average_ghi': np.mean([
                data['ghi_kwh_per_m2_day'] for data in monthly_data.values()
                if data.get('ghi_kwh_per_m2_day')
            ]) if monthly_data else 0
        }
    
    def compare_with_mock_data(self, polygon_coords: List[Tuple[float, float]], 
                              mock_ghi: float) -> Dict:
        """
        Compare GEE data with mock/calculated data
        """
        gee_data = self.get_solar_irradiance_data(polygon_coords)
        
        if not gee_data:
            return None
        
        gee_ghi = gee_data['ghi_kwh_per_m2_day']
        
        return {
            'gee_ghi_kwh_per_m2_day': gee_ghi,
            'mock_ghi_kwh_per_m2_day': mock_ghi,
            'difference_kwh_per_m2_day': gee_ghi - mock_ghi,
            'percentage_difference': ((gee_ghi - mock_ghi) / max(mock_ghi, 0.1)) * 100,
            'accuracy_assessment': 'GEE Higher' if gee_ghi > mock_ghi else 'Mock Higher',
            'data_quality': 'Good' if abs(gee_ghi - mock_ghi) < 1.0 else 'Significant Difference'
        }

# # Test function
# def test_gee_integration():
#     """Test the GEE integration with sample coordinates"""
#     try:
#         print("🚀 Testing Google Earth Engine Integration...")
        
#         # Initialize retriever
#         retriever = GEESolarDataRetriever()
        
#         # Test coordinates (Thailand)
#         test_coords = [
#             (100.540148, 13.671842),
#             (100.540164, 13.671602),
#             (100.540577, 13.67167),
#             (100.54055, 13.671899)
#         ]
        
#         print(f"📍 Testing with coordinates: {test_coords}")
        
#         # Get solar data
#         print("\n📊 Fetching solar irradiance data...")
#         solar_data = retriever.get_solar_irradiance_data(test_coords)
        
#         if solar_data:
#             print("✅ Solar data retrieved successfully!")
#             print(f"   GHI: {solar_data['ghi_kwh_per_m2_day']:.2f} kWh/m²/day")
#             print(f"   Clear Sky GHI: {solar_data['clear_sky_ghi_kwh_per_m2_day']:.2f} kWh/m²/day")
#             print(f"   Cloud Impact: {solar_data['cloud_impact_factor']:.2f}")
        
#         # Get weather data
#         print("\n🌤️ Fetching weather data...")
#         weather_data = retriever.get_weather_data(test_coords)
        
#         if weather_data:
#             print("✅ Weather data retrieved successfully!")
#             print(f"   Average Temperature: {weather_data['average_temperature_celsius']:.1f}°C")
#             print(f"   Solar Radiation: {weather_data['solar_radiation_kwh_per_m2']:.2f} kWh/m²")
        
        
#         get_monthly_solar = retriever.get_monthly_solar_data(test_coords)
#         print(f'get_monthly_solar\n{get_monthly_solar}')

#         return {
#             'solar_data': solar_data,
#             'weather_data': weather_data,
#             'status': 'success'
#         }
        
#     except Exception as e:
#         print(f"❌ Test failed: {str(e)}")
#         return {'status': 'failed', 'error': str(e)}

# if __name__ == '__main__':
#     test_gee_integration()
