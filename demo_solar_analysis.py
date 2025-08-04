#!/usr/bin/env python3
"""
Demo script for the Enhanced Solar Rooftop Analysis System
This script demonstrates the complete solar analysis workflow
"""

from enhanced_solsat_system import EnhancedSolarRooftopSystem
from shapely.geometry import Polygon
import json

def main():
    print("🌞 ENHANCED SOLAR ROOFTOP ANALYSIS DEMO 🌞")
    print("=" * 50)
    
    # Initialize the enhanced system
    system = EnhancedSolarRooftopSystem()
    
    # Your rooftop polygon coordinates (Thailand location)
    rooftop_coordinates = [
        # Rooftop 1 - Large residential
        [(100.540148,13.671842),(100.540164,13.671602),(100.540577,13.67167),(100.54055,13.671899),(100.540534,13.671972),(100.540239,13.67193),(100.540255,13.671847),(100.540148,13.671842)],
        
        # Rooftop 2 - Medium residential
        [(100.540212,13.671502),(100.540282,13.671041),(100.540448,13.671069),(100.540363,13.67152),(100.540212,13.671502)],
        
        # Rooftop 3 - Small residential
        [(100.540073,13.672405),(100.540121,13.672118),(100.540416,13.672181),(100.540352,13.672478),(100.540073,13.672405)],
        
        # Rooftop 4 - Commercial building
        [(100.540325,13.672155),(100.540363,13.67193),(100.54054,13.671967),(100.540577,13.67191),(100.540727,13.671962),(100.540684,13.672181),(100.540325,13.672155)],
        
        # Rooftop 5 - Large residential
        [(100.540593,13.671503),(100.540668,13.670982),(100.54092,13.671018),(100.540904,13.671159),(100.540963,13.671169),(100.540878,13.671534),(100.540593,13.671503)],
        
        # Rooftop 6 - Small commercial
        [(100.54062,13.671889),(100.540647,13.671649),(100.540776,13.671665),(100.540733,13.671915),(100.54062,13.671889)]
    ]
    
    # Convert to Shapely polygons
    polygons = [Polygon(coords) for coords in rooftop_coordinates]
    
    print(f"📍 Analyzing {len(polygons)} rooftops in Thailand...")
    print("🔄 Processing solar irradiance, panel optimization, and economic analysis...")
    
    # Run comprehensive analysis with different consumption scenarios
    scenarios = [
        {"name": "Low Consumption Household", "consumption": 300},
        {"name": "Average Household", "consumption": 500},
        {"name": "High Consumption Household", "consumption": 800},
        {"name": "Small Business", "consumption": 1200}
    ]
    
    for scenario in scenarios:
        print(f"\n📊 SCENARIO: {scenario['name']} ({scenario['consumption']} kWh/month)")
        print("-" * 60)
        
        # Create enhanced map with solar analysis
        map_obj = system.render_enhanced_map(
            polygons=polygons,
            polygon_coords_list=rooftop_coordinates,
            monthly_consumption_kwh=scenario['consumption'],
            grid_shape=(100, 100),
            show_map=True
        )
        
        # Generate detailed report
        report = system.generate_report()
        
        # Save scenario-specific files
        scenario_name = scenario['name'].lower().replace(' ', '_')
        with open(f'files/report_{scenario_name}.txt', 'w') as f:
            f.write(f"SCENARIO: {scenario['name']}\n")
            f.write(f"Monthly Consumption: {scenario['consumption']} kWh\n\n")
            f.write(report)
        
        print(f"✅ Analysis complete for {scenario['name']}")
        print(f"📄 Report saved as: report_{scenario_name}.txt")
    
    # Create a summary comparison
    print("\n🔍 GENERATING COMPARISON SUMMARY...")
    create_scenario_comparison(rooftop_coordinates)
    
    print("\n🎉 DEMO COMPLETE!")
    print("\nGenerated Files:")
    print("📁 files/enhanced_solar_map.html - Interactive map")
    print("📁 files/solar_analysis_results.json - Raw analysis data")
    print("📁 files/solar_analysis_report.txt - Detailed report")
    print("📁 files/scenario_comparison.json - Scenario comparison")
    print("📁 files/report_*.txt - Individual scenario reports")

def create_scenario_comparison(rooftop_coordinates):
    """Create a comparison of different consumption scenarios"""
    system = EnhancedSolarRooftopSystem()
    polygons = [Polygon(coords) for coords in rooftop_coordinates]
    
    scenarios = [300, 500, 800, 1200]  # kWh/month
    comparison_data = {}
    
    for consumption in scenarios:
        # Analyze all rooftops for this scenario
        analysis_results = system.analyze_all_rooftops(rooftop_coordinates, consumption)
        
        # Calculate totals
        total_panels = sum(r['panel_optimization']['panel_count'] for r in analysis_results)
        total_yearly_energy = sum(r['energy_production']['yearly_energy_kwh'] for r in analysis_results)
        total_monthly_savings = sum(r['economic_analysis']['monthly_bill_reduction'] for r in analysis_results)
        total_system_cost = sum(r['economic_analysis']['total_system_cost'] for r in analysis_results)
        avg_payback = sum(r['economic_analysis']['payback_years'] for r in analysis_results) / len(analysis_results)
        
        comparison_data[f"{consumption}_kwh"] = {
            "monthly_consumption": consumption,
            "total_panels": total_panels,
            "total_yearly_energy": total_yearly_energy,
            "total_monthly_savings": total_monthly_savings,
            "total_system_cost": total_system_cost,
            "average_payback_years": avg_payback,
            "roi_percentage": (total_monthly_savings * 12 / total_system_cost) * 100
        }
    
    # Save comparison
    with open('files/scenario_comparison.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    # Print summary
    print("\n📈 SCENARIO COMPARISON SUMMARY:")
    print("Consumption | Panels | Yearly Energy | Monthly Savings | Payback")
    print("-" * 65)
    for consumption in scenarios:
        data = comparison_data[f"{consumption}_kwh"]
        print(f"{consumption:>10} kWh | {data['total_panels']:>6} | {data['total_yearly_energy']:>11.0f} kWh | ${data['total_monthly_savings']:>13.0f} | {data['average_payback_years']:>6.1f} yrs")

def quick_single_rooftop_analysis():
    """Quick analysis for a single rooftop"""
    print("\n🏠 QUICK SINGLE ROOFTOP ANALYSIS")
    print("-" * 40)
    
    from solar_prediction_engine import SolarPredictionEngine
    
    engine = SolarPredictionEngine()
    
    # Single rooftop coordinates
    test_coords = [(100.540148,13.671842),(100.540164,13.671602),(100.540577,13.67167),(100.54055,13.671899)]
    
    result = engine.analyze_rooftop(test_coords, monthly_consumption_kwh=500)
    
    print(f"🏠 Roof Area: {result['roof_analysis']['area_m2']:.1f} m²")
    print(f"☀️ Solar Score: {result['solar_potential_score']:.1f}/100")
    print(f"🔋 Recommended Panels: {result['panel_optimization']['panel_count']}")
    print(f"⚡ Yearly Energy: {result['energy_production']['yearly_energy_kwh']:.0f} kWh")
    print(f"💰 Monthly Savings: ${result['economic_analysis']['monthly_bill_reduction']:.0f}")
    print(f"📅 Payback Period: {result['economic_analysis']['payback_years']:.1f} years")
    print(f"🎨 Color Palette: {result['recommended_color_palette']}")

if __name__ == '__main__':
    try:
        # Run quick analysis first
        quick_single_rooftop_analysis()
        
        # Run full demo
        main()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
