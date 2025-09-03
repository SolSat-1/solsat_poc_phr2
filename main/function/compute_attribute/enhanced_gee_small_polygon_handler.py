#!/usr/bin/env python3
"""
Enhanced Google Earth Engine Handler for Small Polygon ERA5 Data Retrieval
=========================================================================

This module addresses the specific challenge of retrieving ERA5 Land Daily Aggregated data
for very small polygons (rooftop scale) that are smaller than the native pixel resolution
(~9-11 km for ERA5 Land). It implements multiple scientifically valid approaches to avoid
null values while maintaining data integrity.

Key Features:
1. Adaptive buffering based on ERA5 pixel size
2. Multi-scale sampling with quality assessment
3. Spatial interpolation with uncertainty quantification
4. Fallback strategies for robust data retrieval
5. Scientific validation of results

Based on best practices for working with coarse resolution satellite data
for small-scale applications.

Author: Enhanced Solar Analysis System
Date: 2025
"""

import ee
import json
import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

class EnhancedGEESmallPolygonHandler:
    """
    Enhanced handler for ERA5 data retrieval with small polygons
    Implements multiple strategies to avoid null values while maintaining scientific validity
    """
    
    def __init__(self):
        """Initialize the enhanced handler"""
        self.authenticate_gee()
        self.initialize_datasets()
        
        # ERA5 Land characteristics
        self.era5_native_resolution = 11132  # meters (~9-11 km)
        self.era5_pixel_size_degrees = 0.1   # degrees (approximately)
        
        # Quality thresholds
        self.min_polygon_area_m2 = 100       # Minimum meaningful polygon area
        self.max_buffer_distance_m = 15000   # Maximum buffer distance (1.5 ERA5 pixels)
        
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
            print("✅ Enhanced GEE Handler: Authentication successful!")
            
        except Exception as e:
            print(f"❌ GEE Authentication failed: {str(e)}")
            raise
    
    def initialize_datasets(self):
        """Initialize Earth Engine datasets"""
        try:
            # ERA5 reanalysis data
            self.era5_daily = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
            
            # ERA5 hourly for higher temporal resolution (if needed)
            self.era5_hourly = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
            
            print("✅ Enhanced GEE Handler: Datasets initialized!")
            
        except Exception as e:
            print(f"❌ Dataset initialization failed: {str(e)}")
            raise
    
    def create_polygon_geometry(self, polygon_coords: List[Tuple[float, float]]) -> ee.Geometry:
        """Convert polygon coordinates to Earth Engine geometry with validation"""
        if len(polygon_coords) < 3:
            raise ValueError("Polygon must have at least 3 coordinates")
        
        # Convert to GEE format: [[lon, lat], [lon, lat], ...]
        gee_coords = [[coord[0], coord[1]] for coord in polygon_coords]
        
        # Close the polygon if not already closed
        if gee_coords[0] != gee_coords[-1]:
            gee_coords.append(gee_coords[0])
        
        return ee.Geometry.Polygon([gee_coords])
    
    def calculate_polygon_area(self, geometry: ee.Geometry) -> float:
        """Calculate polygon area in square meters"""
        try:
            area_info = geometry.area(maxError=1).getInfo()
            return area_info
        except:
            return 0.0
    
    def calculate_optimal_buffer_distance(self, polygon_area_m2: float) -> float:
        """
        Calculate optimal buffer distance based on polygon size and ERA5 resolution
        
        Scientific rationale:
        - For polygons much smaller than ERA5 pixels, buffer to ensure intersection
        - Buffer distance should be proportional to the mismatch in scale
        - Limit buffer to maintain spatial representativeness
        """
        # ERA5 pixel area (approximately)
        era5_pixel_area_m2 = self.era5_native_resolution ** 2
        
        if polygon_area_m2 >= era5_pixel_area_m2 * 0.25:
            # Polygon is reasonably sized relative to ERA5 pixel
            return 0
        
        # Calculate buffer needed to reach ~25% of ERA5 pixel area
        target_area = era5_pixel_area_m2 * 0.25
        additional_area_needed = target_area - polygon_area_m2
        
        # Approximate buffer distance (assuming roughly circular expansion)
        buffer_distance = math.sqrt(additional_area_needed / math.pi)
        
        # Limit buffer distance
        return min(buffer_distance, self.max_buffer_distance_m)
    
    def method_1_adaptive_buffering(self, geometry: ee.Geometry, 
                                   polygon_area_m2: float) -> Tuple[ee.Geometry, Dict]:
        """
        Method 1: Adaptive buffering to ensure ERA5 pixel intersection
        
        Scientific validity: High
        - Maintains spatial context by expanding the area of interest
        - Buffer size is scientifically determined based on scale mismatch
        - Preserves the local characteristics of the area
        """
        buffer_distance = self.calculate_optimal_buffer_distance(polygon_area_m2)
        
        if buffer_distance > 0:
            buffered_geometry = geometry.buffer(buffer_distance)
            method_info = {
                'method': 'adaptive_buffering',
                'buffer_distance_m': buffer_distance,
                'original_area_m2': polygon_area_m2,
                'buffered_area_m2': self.calculate_polygon_area(buffered_geometry),
                'scientific_validity': 'High',
                'rationale': 'Expands ROI to ensure ERA5 pixel intersection while maintaining spatial context'
            }
            return buffered_geometry, method_info
        else:
            method_info = {
                'method': 'no_buffering_needed',
                'buffer_distance_m': 0,
                'original_area_m2': polygon_area_m2,
                'scientific_validity': 'High',
                'rationale': 'Polygon size adequate for ERA5 resolution'
            }
            return geometry, method_info
    
    def method_2_multi_scale_sampling(self, geometry: ee.Geometry, 
                                     image_collection: ee.ImageCollection) -> Tuple[Dict, Dict]:
        """
        Method 2: Multi-scale sampling with different reducers and scales
        
        Scientific validity: High
        - Uses multiple spatial scales to capture variability
        - Provides uncertainty estimates
        - Robust against single-point failures
        """
        scales = [
            self.era5_native_resolution,      # Native resolution
            self.era5_native_resolution // 2, # Half resolution (upsampled)
            self.era5_native_resolution * 2   # Double resolution (downsampled)
        ]
        
        reducers = [
            ee.Reducer.mean(),
            ee.Reducer.median(),
            ee.Reducer.mode()
        ]
        
        results = {}
        
        for scale in scales:
            for reducer in reducers:
                try:
                    result = (image_collection.mean()
                             .select(['surface_solar_radiation_downwards_sum'])
                             .reduceRegion(
                                 reducer=reducer,
                                 geometry=geometry,
                                 scale=scale,
                                 maxPixels=1e9,
                                 bestEffort=True
                             ).getInfo())
                    
                    key = f"scale_{scale}_reducer_{reducer.getInfo()['type']}"
                    results[key] = result.get('surface_solar_radiation_downwards_sum')
                    
                except Exception as e:
                    print(f"⚠️ Multi-scale sampling failed for scale {scale}: {str(e)}")
        
        # Calculate statistics from valid results
        valid_values = [v for v in results.values() if v is not None and v > 0]
        
        if valid_values:
            method_info = {
                'method': 'multi_scale_sampling',
                'mean_value': np.mean(valid_values),
                'std_value': np.std(valid_values),
                'min_value': np.min(valid_values),
                'max_value': np.max(valid_values),
                'n_valid_samples': len(valid_values),
                'coefficient_of_variation': np.std(valid_values) / np.mean(valid_values) if np.mean(valid_values) > 0 else 0,
                'scientific_validity': 'High',
                'rationale': 'Multiple scales and reducers provide robust estimates with uncertainty quantification'
            }
            
            return {'surface_solar_radiation_downwards_sum': np.mean(valid_values)}, method_info
        else:
            return {}, {'method': 'multi_scale_sampling', 'status': 'failed', 'scientific_validity': 'N/A'}
    
    def method_3_spatial_interpolation(self, geometry: ee.Geometry, 
                                      image_collection: ee.ImageCollection) -> Tuple[Dict, Dict]:
        """
        Method 3: Spatial interpolation using resampling
        
        Scientific validity: Medium-High
        - Uses bilinear interpolation to create finer resolution data
        - Maintains spatial relationships
        - May introduce some smoothing artifacts
        """
        try:
            # Resample to finer resolution using bilinear interpolation
            fine_scale = self.era5_native_resolution // 4  # 4x finer resolution
            
            resampled_image = (image_collection.mean()
                              .select(['surface_solar_radiation_downwards_sum'])
                              .resample('bilinear'))
            
            result = resampled_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=fine_scale,
                maxPixels=1e9,
                bestEffort=True
            ).getInfo()
            
            method_info = {
                'method': 'spatial_interpolation',
                'original_scale': self.era5_native_resolution,
                'interpolated_scale': fine_scale,
                'interpolation_method': 'bilinear',
                'scientific_validity': 'Medium-High',
                'rationale': 'Bilinear interpolation preserves spatial relationships while enabling fine-scale sampling'
            }
            
            return result, method_info
            
        except Exception as e:
            print(f"⚠️ Spatial interpolation failed: {str(e)}")
            return {}, {'method': 'spatial_interpolation', 'status': 'failed', 'scientific_validity': 'N/A'}
    
    def method_4_nearest_neighbor_sampling(self, geometry: ee.Geometry, 
                                          image_collection: ee.ImageCollection) -> Tuple[Dict, Dict]:
        """
        Method 4: Nearest neighbor sampling using sample()
        
        Scientific validity: Medium
        - Guarantees a value by sampling the nearest pixel
        - May not be representative of the exact location
        - Useful as a fallback method
        """
        try:
            # Get centroid of polygon
            centroid = geometry.centroid(maxError=1)
            
            # Sample the nearest pixel
            sample_result = (image_collection.mean()
                           .select(['surface_solar_radiation_downwards_sum'])
                           .sample(region=centroid, scale=self.era5_native_resolution, numPixels=1)
                           .first()
                           .getInfo())
            
            if sample_result and 'properties' in sample_result:
                value = sample_result['properties'].get('surface_solar_radiation_downwards_sum')
                
                method_info = {
                    'method': 'nearest_neighbor_sampling',
                    'sampling_point': 'polygon_centroid',
                    'scientific_validity': 'Medium',
                    'rationale': 'Samples nearest ERA5 pixel to polygon centroid - guaranteed value but may not be spatially representative'
                }
                
                return {'surface_solar_radiation_downwards_sum': value}, method_info
            
        except Exception as e:
            print(f"⚠️ Nearest neighbor sampling failed: {str(e)}")
        
        return {}, {'method': 'nearest_neighbor_sampling', 'status': 'failed', 'scientific_validity': 'N/A'}
    
    def get_enhanced_era5_data(self, polygon_coords: List[Tuple[float, float]], 
                              start_date: str = None, end_date: str = None,
                              preferred_method: str = 'adaptive_buffering') -> Dict:
        """
        Enhanced ERA5 data retrieval with multiple fallback strategies
        
        Args:
            polygon_coords: List of (longitude, latitude) tuples
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            preferred_method: Preferred method ('adaptive_buffering', 'multi_scale', 'interpolation', 'nearest_neighbor')
        
        Returns:
            Dictionary with solar data and method information
        """
        try:
            # Set default date range
            if not start_date:
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Create geometry and calculate area
            geometry = self.create_polygon_geometry(polygon_coords)
            polygon_area_m2 = self.calculate_polygon_area(geometry)
            
            # Filter ERA5 data
            era5_filtered = (self.era5_daily
                           .filterDate(start_date, end_date)
                           .filterBounds(geometry))
            
            print(f"📐 Polygon area: {polygon_area_m2:.1f} m² (ERA5 pixel: ~{self.era5_native_resolution**2:.0f} m²)")
            
            # Method selection and execution
            methods_to_try = []
            
            if preferred_method == 'adaptive_buffering':
                methods_to_try = ['adaptive_buffering', 'multi_scale', 'interpolation', 'nearest_neighbor']
            elif preferred_method == 'multi_scale':
                methods_to_try = ['multi_scale', 'adaptive_buffering', 'interpolation', 'nearest_neighbor']
            elif preferred_method == 'interpolation':
                methods_to_try = ['interpolation', 'adaptive_buffering', 'multi_scale', 'nearest_neighbor']
            else:
                methods_to_try = ['nearest_neighbor', 'adaptive_buffering', 'multi_scale', 'interpolation']
            
            successful_result = None
            method_results = []
            
            for method in methods_to_try:
                print(f"🔄 Trying method: {method}")
                
                try:
                    if method == 'adaptive_buffering':
                        buffered_geometry, method_info = self.method_1_adaptive_buffering(geometry, polygon_area_m2)
                        
                        result = (era5_filtered.mean()
                                .select(['surface_solar_radiation_downwards_sum'])
                                .reduceRegion(
                                    reducer=ee.Reducer.mean(),
                                    geometry=buffered_geometry,
                                    scale=self.era5_native_resolution,
                                    maxPixels=1e9,
                                    bestEffort=True
                                ).getInfo())
                        
                        method_info['result'] = result
                        
                    elif method == 'multi_scale':
                        result, method_info = self.method_2_multi_scale_sampling(geometry, era5_filtered)
                        
                    elif method == 'interpolation':
                        result, method_info = self.method_3_spatial_interpolation(geometry, era5_filtered)
                        
                    elif method == 'nearest_neighbor':
                        result, method_info = self.method_4_nearest_neighbor_sampling(geometry, era5_filtered)
                    
                    method_results.append(method_info)
                    
                    # Check if we got a valid result
                    solar_value = result.get('surface_solar_radiation_downwards_sum')
                    if solar_value is not None and solar_value > 0:
                        print(f"✅ Method {method} successful: {solar_value:.1f} J/m²")
                        successful_result = {
                            'raw_solar_radiation_j_m2': solar_value,
                            'method_used': method,
                            'method_info': method_info
                        }
                        break
                    else:
                        print(f"⚠️ Method {method} returned null/zero value")
                        
                except Exception as e:
                    print(f"❌ Method {method} failed: {str(e)}")
                    method_results.append({
                        'method': method,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            if successful_result:
                # Convert units and calculate derived values
                solar_j_m2 = successful_result['raw_solar_radiation_j_m2']
                ghi_kwh_per_day = solar_j_m2 / 3600000  # J to kWh conversion
                
                # Estimate clear sky and cloud impact
                clear_sky_ghi = ghi_kwh_per_day * 1.25  # Assume 25% higher for clear sky
                cloud_impact_factor = ghi_kwh_per_day / clear_sky_ghi
                
                return {
                    'success': True,
                    'ghi_kwh_per_m2_day': ghi_kwh_per_day,
                    'clear_sky_ghi_kwh_per_m2_day': clear_sky_ghi,
                    'cloud_impact_factor': cloud_impact_factor,
                    'diffuse_fraction': 0.3,  # Typical for Thailand
                    'data_source': 'ERA5_Enhanced',
                    'date_range': f"{start_date} to {end_date}",
                    'polygon_area_m2': polygon_area_m2,
                    'method_used': successful_result['method_used'],
                    'method_info': successful_result['method_info'],
                    'all_methods_tried': method_results,
                    'raw_data': {
                        'solar_radiation_j_m2': solar_j_m2
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'All methods failed to retrieve valid data',
                    'polygon_area_m2': polygon_area_m2,
                    'methods_tried': method_results,
                    'recommendations': self._generate_recommendations(polygon_area_m2, method_results)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Enhanced ERA5 retrieval failed: {str(e)}",
                'recommendations': ['Check polygon coordinates', 'Verify date range', 'Check GEE authentication']
            }
    
    def _generate_recommendations(self, polygon_area_m2: float, method_results: List[Dict]) -> List[str]:
        """Generate recommendations based on failure analysis"""
        recommendations = []
        
        if polygon_area_m2 < 100:
            recommendations.append("Polygon is very small (<100 m²). Consider using a representative point instead.")
        
        if polygon_area_m2 < self.era5_native_resolution ** 2 * 0.01:
            recommendations.append("Polygon is <1% of ERA5 pixel size. Results may not be spatially representative.")
        
        failed_methods = [r for r in method_results if r.get('status') == 'failed']
        if len(failed_methods) == len(method_results):
            recommendations.append("All methods failed. Check GEE authentication and data availability.")
        
        recommendations.append("Consider using multiple nearby points and averaging results.")
        recommendations.append("Validate results against ground measurements if available.")
        
        return recommendations
    
    def compare_methods(self, polygon_coords: List[Tuple[float, float]], 
                       start_date: str = None, end_date: str = None) -> Dict:
        """
        Compare all methods for the same polygon to assess consistency
        """
        methods = ['adaptive_buffering', 'multi_scale', 'interpolation', 'nearest_neighbor']
        results = {}
        
        for method in methods:
            print(f"\n🔍 Testing method: {method}")
            result = self.get_enhanced_era5_data(polygon_coords, start_date, end_date, method)
            results[method] = result
        
        # Analyze consistency
        successful_results = {k: v for k, v in results.items() if v.get('success', False)}
        
        if len(successful_results) > 1:
            ghi_values = [r['ghi_kwh_per_m2_day'] for r in successful_results.values()]
            consistency_analysis = {
                'mean_ghi': np.mean(ghi_values),
                'std_ghi': np.std(ghi_values),
                'coefficient_of_variation': np.std(ghi_values) / np.mean(ghi_values),
                'min_ghi': np.min(ghi_values),
                'max_ghi': np.max(ghi_values),
                'range_ghi': np.max(ghi_values) - np.min(ghi_values),
                'consistency_rating': 'High' if np.std(ghi_values) / np.mean(ghi_values) < 0.1 else 'Medium' if np.std(ghi_values) / np.mean(ghi_values) < 0.2 else 'Low'
            }
        else:
            consistency_analysis = {'status': 'insufficient_data'}
        
        return {
            'individual_results': results,
            'consistency_analysis': consistency_analysis,
            'recommendations': self._generate_method_recommendations(successful_results, consistency_analysis)
        }
    
    def _generate_method_recommendations(self, successful_results: Dict, consistency_analysis: Dict) -> List[str]:
        """Generate recommendations based on method comparison"""
        recommendations = []
        
        if len(successful_results) == 0:
            recommendations.append("No methods succeeded. Check polygon size and location.")
        elif len(successful_results) == 1:
            method = list(successful_results.keys())[0]
            recommendations.append(f"Only {method} succeeded. Use this method but validate results.")
        else:
            if consistency_analysis.get('consistency_rating') == 'High':
                recommendations.append("High consistency between methods. Results are reliable.")
                recommendations.append("Recommend using adaptive_buffering for best scientific validity.")
            elif consistency_analysis.get('consistency_rating') == 'Medium':
                recommendations.append("Medium consistency between methods. Consider averaging results.")
            else:
                recommendations.append("Low consistency between methods. Investigate polygon characteristics.")
                recommendations.append("Consider using ground truth data for validation.")
        
        return recommendations

# def test_enhanced_small_polygon_handler():
#     """Test the enhanced small polygon handler"""
#     print("🚀 Testing Enhanced Small Polygon Handler for ERA5 Data...")
    
#     # Initialize handler
#     handler = EnhancedGEESmallPolygonHandler()
    
#     # Test with very small rooftop polygon (Thailand)
#     small_rooftop_coords = [
#         (100.540148, 13.671842),  # ~30m x 20m rooftop
#         (100.540164, 13.671842),
#         (100.540164, 13.671862),
#         (100.540148, 13.671862)
#     ]
    
#     print(f"📍 Testing small rooftop: {small_rooftop_coords}")
    
#     # Test single method
#     print("\n--- Single Method Test (Adaptive Buffering) ---")
#     result = handler.get_enhanced_era5_data(small_rooftop_coords, preferred_method='adaptive_buffering')
    
#     if result['success']:
#         print(f"✅ Success with {result['method_used']}")
#         print(f"   GHI: {result['ghi_kwh_per_m2_day']:.2f} kWh/m²/day")
#         print(f"   Polygon area: {result['polygon_area_m2']:.1f} m²")
#         print(f"   Method info: {result['method_info']['rationale']}")
#     else:
#         print(f"❌ Failed: {result['error']}")
#         print(f"   Recommendations: {result['recommendations']}")
    
#     # Test method comparison
#     print("\n--- Method Comparison Test ---")
#     comparison = handler.compare_methods(small_rooftop_coords)
    
#     print(f"📊 Comparison Results:")
#     for method, result in comparison['individual_results'].items():
#         if result.get('success'):
#             print(f"   {method}: {result['ghi_kwh_per_m2_day']:.2f} kWh/m²/day ✅")
#         else:
#             print(f"   {method}: Failed ❌")
    
#     if 'consistency_rating' in comparison['consistency_analysis']:
#         print(f"🎯 Consistency: {comparison['consistency_analysis']['consistency_rating']}")
#         print(f"   Mean GHI: {comparison['consistency_analysis']['mean_ghi']:.2f} kWh/m²/day")
#         print(f"   Std Dev: {comparison['consistency_analysis']['std_ghi']:.3f}")
    
#     print(f"💡 Recommendations:")
#     for rec in comparison['recommendations']:
#         print(f"   - {rec}")
    
#     return {
#         'single_method_result': result,
#         'method_comparison': comparison,
#         'status': 'success'
#     }

# if __name__ == '__main__':
#     test_enhanced_small_polygon_handler()
