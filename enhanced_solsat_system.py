from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import folium
from folium.plugins import Draw, Fullscreen
from solar_prediction_engine import SolarPredictionEngine
from typing import List, Tuple, Dict
import json


palettes = [
        ((255, 165, 0), (255, 255, 255)),        # Orange to white
        ('#5efc8d', '#35a7ff'),                  # Mint to blue
        ((255,0,0), (255,255,0)),                # Red to yellow
    ]
class EnhancedSolarRooftopSystem:
    """
    Enhanced solar rooftop analysis system combining visualization with prediction
    """
    
    def __init__(self):
        self.prediction_engine = SolarPredictionEngine()
        self.analysis_results = {}
        
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def interpolate_colors(self, start_color, end_color, n):
        # Accept hex or RGB tuple
        if isinstance(start_color, str): 
            start_color = self.hex_to_rgb(start_color)
        if isinstance(end_color, str): 
            end_color = self.hex_to_rgb(end_color)
        start = np.array(start_color)
        end = np.array(end_color)
        ratios = np.linspace(0, 1, n)[:, None]
        return (start * (1 - ratios) + end * ratios).astype(np.uint8)

    def analyze_all_rooftops(self, polygon_coords_list: List[List[Tuple[float, float]]], 
                           monthly_consumption_kwh: float = 500) -> List[Dict]:
        """
        Analyze all rooftops and store results
        """
        results = []
        for i, coords in enumerate(polygon_coords_list):
            analysis = self.prediction_engine.analyze_rooftop(coords, monthly_consumption_kwh)
            analysis['polygon_id'] = i
            results.append(analysis)
            self.analysis_results[i] = analysis
        return results

    def get_optimized_palettes(self, analysis_results: List[Dict]) -> List[Tuple[str, str]]:
        """
        Generate optimized color palettes based on solar potential scores
        """
        palettes = []
        scores = [result['solar_potential_score'] for result in analysis_results]
        min_score, max_score = min(scores), max(scores)
        
        for result in analysis_results:
            palette = self.prediction_engine.get_color_palette_for_value(
                result['solar_potential_score'], min_score, max_score
            )
            palettes.append(palette)
        
        return palettes

    def create_enhanced_overlay_image(self, polygon, analysis_data, grid_shape, fname='enhanced_overlay.png'):
        """
        Create overlay image with solar potential visualization - Orange to White gradient without cropping
        """
        minx, miny, maxx, maxy = polygon.bounds
        
        # Get color palette (orange to white)
        color_palette = analysis_data['recommended_color_palette']
        
        # Create gradient from orange to white across the entire area
        n_pix = grid_shape[0] * grid_shape[1]
        rgb_colors = self.interpolate_colors(color_palette[0], color_palette[1], n_pix).reshape(grid_shape[0], grid_shape[1], 3)
        
        # Apply solar potential intensity variation
        potential_score = analysis_data['solar_potential_score'] / 100
        intensity_map = np.random.normal(potential_score, 0.1, grid_shape)
        intensity_map = np.clip(intensity_map, 0, 1)
        
        # Modulate colors based on intensity
        for i in range(3):  # RGB channels
            rgb_colors[:, :, i] = rgb_colors[:, :, i] * intensity_map
        
        # No masking - show full gradient with semi-transparent alpha
        alpha = np.full(grid_shape, 180, dtype=np.uint8)  # Semi-transparent overlay
        rgba = np.dstack([rgb_colors.astype(np.uint8), alpha])
        rgba = np.flipud(rgba)  # Correct orientation for mapping
        img = Image.fromarray(rgba, mode='RGBA')
        img.save(fname)
        return (miny, minx), (maxy, maxx), fname

    def create_info_popup(self, analysis_data: Dict) -> str:
        """
        Create detailed popup information for each rooftop
        """
        roof = analysis_data['roof_analysis']
        solar = analysis_data['solar_irradiance']
        panels = analysis_data['panel_optimization']
        energy = analysis_data['energy_production']
        economics = analysis_data['economic_analysis']
        
        popup_html = f"""
        <div style="width: 300px; font-family: Arial, sans-serif;">
            <h3 style="color: #2E8B57; margin-bottom: 10px;">🏠 Solar Rooftop Analysis</h3>
            
            <div style="background: #f0f8ff; padding: 8px; margin: 5px 0; border-radius: 5px;">
                <strong>📐 Roof Specifications:</strong><br>
                • Area: {roof['area_m2']:.1f} m²<br>
                • Usable Area: {panels['usable_area']:.1f} m²<br>
                • Coverage: {panels['coverage_ratio']*100:.1f}%
            </div>
            
            <div style="background: #fff8dc; padding: 8px; margin: 5px 0; border-radius: 5px;">
                <strong>☀️ Solar Potential:</strong><br>
                • Score: {analysis_data['solar_potential_score']:.1f}/100<br>
                • GHI: {solar['ghi']:.0f} W/m²<br>
                • Elevation: {solar['elevation_angle']:.1f}°
            </div>
            
            <div style="background: #f0fff0; padding: 8px; margin: 5px 0; border-radius: 5px;">
                <strong>🔋 Panel Configuration:</strong><br>
                • Recommended Panels: {panels['panel_count']}<br>
                • Total Power: {panels['total_power_kw']:.1f} kW<br>
                • System Efficiency: {energy['system_efficiency']*100:.1f}%
            </div>
            
            <div style="background: #fff0f5; padding: 8px; margin: 5px 0; border-radius: 5px;">
                <strong>⚡ Energy Production:</strong><br>
                • Daily: {energy['daily_energy_kwh']:.1f} kWh<br>
                • Monthly: {energy['monthly_energy_kwh']:.0f} kWh<br>
                • Yearly: {energy['yearly_energy_kwh']:.0f} kWh
            </div>
            
            <div style="background: #f5fffa; padding: 8px; margin: 5px 0; border-radius: 5px;">
                <strong>💰 Economic Analysis:</strong><br>
                • System Cost: ${economics['total_system_cost']:,.0f}<br>
                • Monthly Savings: ${economics['monthly_bill_reduction']:.0f}<br>
                • Payback: {economics['payback_years']:.1f} years<br>
                • ROI: {economics['roi_percentage']:.1f}%
            </div>
        </div>
        """
        return popup_html

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def interpolate_colors(self, start_color, end_color, n):
        # Accept hex or RGB tuple
        if isinstance(start_color, str): 
            start_color = self.hex_to_rgb(start_color)
        if isinstance(end_color, str): 
            end_color = self.hex_to_rgb(end_color)
        start = np.array(start_color)
        end = np.array(end_color)
        ratios = np.linspace(0, 1, n)[:, None]
        return (start * (1 - ratios) + end * ratios).astype(np.uint8)

    def create_masked_overlay_image(self, polygon, grid_shape, palette, fname='masked_overlay.png'):
        minx, miny, maxx, maxy = polygon.bounds
        xs = np.linspace(minx, maxx, grid_shape[1])
        ys = np.linspace(miny, maxy, grid_shape[0])
        xx, yy = np.meshgrid(xs, ys)
        lonlats = np.column_stack((xx.ravel(), yy.ravel()))
        mask = np.array([polygon.contains(Point(lon, lat)) for lon, lat in lonlats]).reshape(grid_shape)

        # Palette is (start, end), can be hex or RGB
        n_pix = grid_shape[0] * grid_shape[1]
        rgb_colors = self.interpolate_colors(palette[0], palette[1], n_pix).reshape(grid_shape[0], grid_shape[1], 3)
        alpha = (mask * 255).astype(np.uint8)
        rgba = np.dstack([rgb_colors, alpha])
        rgba = np.flipud(rgba)  # Correct orientation for mapping
        img = Image.fromarray(rgba, mode='RGBA')
        img.save(fname)
        return (miny, minx), (maxy, maxx), fname


    def render_enhanced_map(self, polygons, polygon_coords_list, monthly_consumption_kwh=500, 
                          grid_shape=(100, 100), show_map=True,rgb=True,
                          tile_layer='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}') -> folium.Map:
        """
        Render enhanced map with solar analysis
        """
        if not polygons:
            print("No polygons to display.")
            return None

        # Analyze all rooftops
        print("Analyzing rooftops for solar potential...")
        analysis_results = self.analyze_all_rooftops(polygon_coords_list, monthly_consumption_kwh)
        
        # Create summary statistics
        total_panels = sum(r['panel_optimization']['panel_count'] for r in analysis_results)
        total_yearly_energy = sum(r['energy_production']['yearly_energy_kwh'] for r in analysis_results)
        total_monthly_savings = sum(r['economic_analysis']['monthly_bill_reduction'] for r in analysis_results)
        avg_solar_score = np.mean([r['solar_potential_score'] for r in analysis_results])
        
        print(f"\n=== COMPREHENSIVE SOLAR ANALYSIS SUMMARY ===")
        print(f"Total Rooftops Analyzed: {len(analysis_results)}")
        print(f"Total Recommended Panels: {total_panels}")
        print(f"Total Yearly Energy Production: {total_yearly_energy:.0f} kWh")
        print(f"Total Monthly Savings: ${total_monthly_savings:.0f}")
        print(f"Average Solar Potential Score: {avg_solar_score:.1f}/100")

        centroid = polygons[0].centroid
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=18)

        folium.TileLayer(
            tiles=tile_layer,
            attr='Google',
            name='Google Satellite',
            overlay=True,
            control=True
        ).add_to(m)

        # Create files directory
        Path('files').mkdir(exist_ok=True)
        overlay_files = []

        # Add enhanced overlays for each polygon
        for idx, (polygon, analysis) in enumerate(zip(polygons, analysis_results)):
            fname = str(Path('files') / f'solar_overlay_{idx}.png')
            
            if rgb:
                palette = palettes[idx % len(palettes)]
                sw, ne, fname = self.create_masked_overlay_image(polygon, grid_shape, palette, fname)
            else:
                sw, ne, fname = self.create_enhanced_overlay_image(polygon, analysis, grid_shape, fname)
            overlay_files.append(fname)
            
            # Add overlay
            folium.raster_layers.ImageOverlay(
                name=f'Solar Roof {idx+1} (Score: {analysis["solar_potential_score"]:.1f})',
                image=fname,
                bounds=[sw, ne],
                opacity=0.8
            ).add_to(m)
            
            # # Add detailed popup
            # folium_coords = [(lat, lon) for lon, lat in polygon.exterior.coords]
            # popup_content = self.create_info_popup(analysis)
            
            # folium.Polygon(
            #     locations=folium_coords,
            #     color='#FF00FF', 
            #     weight=2, 
            #     fill=False,
            #     popup=folium.Popup(popup_content, max_width=350)
            # ).add_to(m)

        # Add summary marker
        summary_html = f"""
        <div style="width: 250px; font-family: Arial, sans-serif;">
            <h3 style="color: #1E90FF;">📊 Project Summary</h3>
            <p><strong>Rooftops:</strong> {len(analysis_results)}</p>
            <p><strong>Total Panels:</strong> {total_panels}</p>
            <p><strong>Yearly Energy:</strong> {total_yearly_energy:.0f} kWh</p>
            <p><strong>Monthly Savings:</strong> ${total_monthly_savings:.0f}</p>
            <p><strong>Avg Solar Score:</strong> {avg_solar_score:.1f}/100</p>
        </div>
        """
        
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=folium.Popup(summary_html, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

        folium.LayerControl().add_to(m)
        Fullscreen(position='topright').add_to(m)
        Draw().add_to(m)

        # Enhanced JavaScript for coordinate capture
        custom_js = """
        <script>
        map.on('draw:created', function (e) {
            var type = e.layerType,
                layer = e.layer;
            if (type === 'polygon') {
                var coords = layer.getLatLngs()[0]
                    .map(function(latlng) {
                        return '(' + latlng.lng.toFixed(6) + ',' + latlng.lat.toFixed(6) + ')';
                    })
                    .join(',');
                var popup_content = 'New Polygon Coordinates:<br>' + coords + 
                                  '<br><br>Copy this format for analysis:<br>[' + coords + ']';
                layer.bindPopup(popup_content).openPopup();
                console.log('New polygon coordinates:', coords);
            }
            drawnItems.addLayer(layer);
        });
        </script>
        """
        m.get_root().html.add_child(folium.Element(custom_js))

        if show_map:
            map_file = str(Path('files') / 'enhanced_solar_map.html')
            m.save(map_file)
            print(f"\nEnhanced solar map saved as {map_file}")
            
            # Save analysis results to JSON
            results_file = str(Path('files') / 'solar_analysis_results.json')
            with open(results_file, 'w') as f:
                # Convert numpy types to native Python types for JSON serialization
                json_results = []
                for result in analysis_results:
                    json_result = {}
                    for key, value in result.items():
                        if isinstance(value, dict):
                            json_result[key] = {k: float(v) if isinstance(v, (np.integer, np.floating)) else v 
                                              for k, v in value.items()}
                        else:
                            json_result[key] = float(value) if isinstance(value, (np.integer, np.floating)) else value
                    json_results.append(json_result)
                json.dump(json_results, f, indent=2)
            print(f"Analysis results saved as {results_file}")
            
            return m
        else:
            print("Map not shown (show_map=False)")
            return None

    def generate_report(self) -> str:
        """
        Generate a comprehensive text report
        """
        if not self.analysis_results:
            return "No analysis data available. Please run the analysis first."
        
        report = "=" * 60 + "\n"
        report += "COMPREHENSIVE SOLAR ROOFTOP ANALYSIS REPORT\n"
        report += "=" * 60 + "\n\n"
        
        total_area = 0
        total_panels = 0
        total_yearly_energy = 0
        total_cost = 0
        total_savings = 0
        
        for i, analysis in self.analysis_results.items():
            roof = analysis['roof_analysis']
            panels = analysis['panel_optimization']
            energy = analysis['energy_production']
            economics = analysis['economic_analysis']
            
            report += f"ROOFTOP #{i+1}\n"
            report += "-" * 20 + "\n"
            report += f"Solar Potential Score: {analysis['solar_potential_score']:.1f}/100\n"
            report += f"Roof Area: {roof['area_m2']:.1f} m²\n"
            report += f"Recommended Panels: {panels['panel_count']}\n"
            report += f"System Power: {panels['total_power_kw']:.1f} kW\n"
            report += f"Yearly Energy: {energy['yearly_energy_kwh']:.0f} kWh\n"
            report += f"System Cost: ${economics['total_system_cost']:,.0f}\n"
            report += f"Monthly Savings: ${economics['monthly_bill_reduction']:.0f}\n"
            report += f"Payback Period: {economics['payback_years']:.1f} years\n"
            report += f"ROI: {economics['roi_percentage']:.1f}%\n\n"
            
            total_area += roof['area_m2']
            total_panels += panels['panel_count']
            total_yearly_energy += energy['yearly_energy_kwh']
            total_cost += economics['total_system_cost']
            total_savings += economics['monthly_bill_reduction']
        
        report += "SUMMARY TOTALS\n"
        report += "=" * 20 + "\n"
        report += f"Total Roof Area: {total_area:.1f} m²\n"
        report += f"Total Panels: {total_panels}\n"
        report += f"Total Yearly Energy: {total_yearly_energy:.0f} kWh\n"
        report += f"Total System Cost: ${total_cost:,.0f}\n"
        report += f"Total Monthly Savings: ${total_savings:.0f}\n"
        report += f"Total Annual Savings: ${total_savings * 12:.0f}\n"
        report += f"Overall Payback: {total_cost / (total_savings * 12):.1f} years\n"
        
        return report

# Example usage
if __name__ == '__main__':
    # Initialize the enhanced system
    system = EnhancedSolarRooftopSystem()
    
    # Your polygon coordinates
    coords1 = [(100.540148,13.671842),(100.540164,13.671602),(100.540577,13.67167),(100.54055,13.671899),(100.540534,13.671972),(100.540239,13.67193),(100.540255,13.671847),(100.540148,13.671842)]
    coords2 = [(100.540212,13.671502),(100.540282,13.671041),(100.540448,13.671069),(100.540363,13.67152),(100.540212,13.671502)]
    coords3 = [(100.540073,13.672405),(100.540121,13.672118),(100.540416,13.672181),(100.540352,13.672478),(100.540073,13.672405)]
    coords4 = [(100.540325,13.672155),(100.540363,13.67193),(100.54054,13.671967),(100.540577,13.67191),(100.540727,13.671962),(100.540684,13.672181),(100.540325,13.672155)]
    coords5 = [(100.540593,13.671503),(100.540668,13.670982),(100.54092,13.671018),(100.540904,13.671159),(100.540963,13.671169),(100.540878,13.671534),(100.540593,13.671503)]
    coords6 = [(100.54062,13.671889),(100.540647,13.671649),(100.540776,13.671665),(100.540733,13.671915),(100.54062,13.671889)]

    polygon_coords_list = [coords1, coords2, coords3, coords4, coords5, coords6]
    polygons = [Polygon(coords) for coords in polygon_coords_list]
    
    # Create enhanced map with solar analysis
    system.render_enhanced_map(
        polygons=polygons,
        polygon_coords_list=polygon_coords_list,
        monthly_consumption_kwh=600,  # Adjust based on actual consumption
        grid_shape=(100, 100),
        show_map=True
    )
    
    # Generate and save report
    report = system.generate_report()
    with open('files/solar_analysis_report.txt', 'w') as f:
        f.write(report)
    
    print("\n" + report)
    print("\nFiles generated:")
    print("- enhanced_solar_map.html (Interactive map)")
    print("- solar_analysis_results.json (Raw data)")
    print("- solar_analysis_report.txt (Summary report)")
