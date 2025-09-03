# Enhanced Solar Rooftop Analysis System

A comprehensive solar energy prediction and visualization system that analyzes rooftop potential using RGB color mapping, solar irradiance calculations, and economic modeling.

## 🌟 Features

### Core Capabilities
- **Solar Irradiance Prediction**: Real-time calculation of Global Horizontal Irradiance (GHI) and Direct Normal Irradiance (DNI)
- **Panel Optimization**: Intelligent placement algorithms considering roof geometry and spacing requirements
- **Energy Production Modeling**: Accurate yearly, monthly, and daily energy output predictions
- **Economic Analysis**: Complete ROI calculations including payback periods and monthly savings
- **Interactive Visualization**: Dynamic color-coded maps showing solar potential

### Advanced Analytics
- **Multi-Scenario Analysis**: Compare different consumption patterns (300-1200 kWh/month)
- **Color Palette Optimization**: RGB gradients based on solar potential scores
- **Comprehensive Reporting**: Detailed PDF and JSON reports for each analysis
- **Real-time Weather Integration**: Seasonal adjustments and temperature coefficients

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- uv (recommended) or pip for package management

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd 05_colab_solsat_poc
```

2. **Create virtual environment with uv**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
uv pip install -r requirements.txt
```

### Running the Demo

```bash
python main_solar_analysis.py
```

This will:
- Analyze 6 sample rooftops in Thailand
- Generate interactive maps with solar overlays
- Create detailed reports for 4 consumption scenarios
- Produce comparison summaries and visualizations

## 📊 System Architecture

### Core Components

1. **SolarPredictionEngine** (`solar_prediction_engine.py`)
   - Solar irradiance calculations
   - Panel optimization algorithms
   - Economic modeling
   - Color palette generation

2. **EnhancedSolarRooftopSystem** (`enhanced_solsat_system.py`)
   - Visualization engine
   - Interactive map generation
   - Report generation
   - Multi-scenario analysis

3. **Demo System** (`main_solar_analysis.py`)
   - Example usage
   - Scenario comparisons
   - File generation

### Data Flow
```
Polygon Coordinates → Solar Analysis → Visualization → Reports
     ↓                    ↓              ↓           ↓
Roof Geometry → Irradiance Calc → Color Mapping → JSON/HTML
     ↓                    ↓              ↓           ↓
Area Calculation → Panel Optimization → Overlays → Text Reports
     ↓                    ↓              ↓           ↓
Usage Patterns → Economic Analysis → Interactive Map → Comparisons
```

## 🔧 Configuration

### Solar Panel Specifications
```python
panel_specs = {
    'power_rating': 400,      # Watts per panel
    'efficiency': 0.20,       # 20% efficiency
    'area': 2.0,             # m² per panel
    'temperature_coefficient': -0.004,  # %/°C
    'system_losses': 0.15    # 15% system losses
}
```

### Economic Parameters
```python
economic_params = {
    'electricity_rate': 0.12,           # $/kWh
    'panel_cost': 300,                  # $ per panel
    'installation_cost_per_watt': 1.5,  # $/W
    'maintenance_annual': 0.01          # 1% annually
}
```

### Location Settings (Thailand Example)
```python
location_data = {
    'latitude': 13.671842,
    'longitude': 100.540148,
    'timezone': 7,              # UTC+7
    'average_ghi': 5.2,         # kWh/m²/day
    'peak_sun_hours': 5.5
}
```

## 📈 Analysis Results

### Sample Output for 6 Rooftops:
- **Total Roof Area**: 6,702 m²
- **Recommended Panels**: 2,256 panels
- **Total System Power**: 902.4 kW
- **Yearly Energy Production**: 1,037,707 kWh
- **Monthly Savings**: $8,374
- **Average Solar Score**: 56.2/100
- **Payback Period**: 19.5 years

### Generated Files:
- `enhanced_solar_map.html` - Interactive map with overlays
- `solar_analysis_results.json` - Raw analysis data
- `scenario_comparison.json` - Multi-scenario comparison
- `report_*.txt` - Detailed reports for each scenario
- `solar_overlay_*.png` - Color-coded roof overlays

## 🎨 Color Coding System

The system uses intelligent color palettes based on solar potential:

- **🔴 Low Potential (0-30%)**: Red to Orange gradient
- **🟡 Medium Potential (30-70%)**: Orange to Yellow gradient  
- **🟢 High Potential (70-100%)**: Yellow to Green gradient

## 📋 API Reference

### SolarPredictionEngine Methods

#### `analyze_rooftop(polygon_coords, monthly_consumption_kwh=500)`
Comprehensive analysis of a single rooftop.

**Parameters:**
- `polygon_coords`: List of (longitude, latitude) tuples
- `monthly_consumption_kwh`: Expected monthly energy consumption

**Returns:**
```python
{
    'roof_analysis': {...},
    'solar_irradiance': {...},
    'panel_optimization': {...},
    'energy_production': {...},
    'economic_analysis': {...},
    'solar_potential_score': float,
    'recommended_color_palette': (start_color, end_color)
}
```

#### `calculate_solar_irradiance(lat, lon, date=None)`
Calculate solar irradiance for specific location and time.

#### `optimize_panel_placement(roof_area, usable_factor=0.75)`
Determine optimal panel configuration for given roof area.

### EnhancedSolarRooftopSystem Methods

#### `render_enhanced_map(polygons, polygon_coords_list, monthly_consumption_kwh=500)`
Generate interactive map with solar analysis overlays.

#### `generate_report()`
Create comprehensive text report of all analyzed rooftops.

## 🔬 Technical Details

### Solar Calculations
- **Solar Position**: Declination angle and elevation calculations
- **Air Mass**: Atmospheric absorption modeling
- **Seasonal Adjustments**: Location-specific solar variations
- **Temperature Derating**: Performance impact of temperature

### Economic Modeling
- **Net Metering**: Grid tie-in calculations with 80% sellback rate
- **System Costs**: Equipment + installation + maintenance
- **ROI Analysis**: Payback periods and annual returns
- **Scenario Comparison**: Multiple consumption patterns

### Visualization Features
- **Google Satellite Base**: High-resolution satellite imagery
- **Interactive Overlays**: Clickable rooftop information
- **Layer Control**: Toggle different analysis layers
- **Drawing Tools**: Add new rooftop polygons
- **Responsive Design**: Works on desktop and mobile

## 🌍 Customization for Different Regions

### Adapting for New Locations

1. **Update Location Data**:
```python
location_data = {
    'latitude': YOUR_LATITUDE,
    'longitude': YOUR_LONGITUDE,
    'timezone': YOUR_TIMEZONE,
    'average_ghi': LOCAL_GHI_VALUE,
    'peak_sun_hours': LOCAL_PEAK_HOURS
}
```

2. **Adjust Economic Parameters**:
```python
economic_params = {
    'electricity_rate': LOCAL_RATE,
    'panel_cost': LOCAL_PANEL_COST,
    'installation_cost_per_watt': LOCAL_INSTALL_COST,
    'maintenance_annual': LOCAL_MAINTENANCE_RATE
}
```

3. **Modify Solar Calculations**:
- Update seasonal adjustment factors
- Adjust for local weather patterns
- Include regional solar incentives

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Solar irradiance calculations based on NREL methodologies
- Economic modeling inspired by PVGIS standards
- Visualization powered by Folium and Google Maps
- Thailand solar data from government energy statistics

## 📞 Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Contact the development team
- Check the documentation wiki

---

**Built with ❤️ for sustainable energy analysis**
