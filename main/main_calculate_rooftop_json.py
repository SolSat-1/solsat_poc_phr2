from icecream import ic
from function.compute_attribute.enhanced_report_generator import EnhancedSolarReportGenerator

def main():
    """Main function to demonstrate the enhanced report generator"""
    
    # Sample rooftop coordinates (Thailand)
    sample_rooftops = [
        # Rooftop 1 - Large commercial building
        [
            (100.540148, 13.671842),
            (100.540164, 13.671602),
            (100.540577, 13.67167),
            (100.54055, 13.671899)
        ],
        # Rooftop 2 - Medium residential building
        [
            (100.540212, 13.671502),
            (100.540282, 13.671041),
            (100.540448, 13.671069),
            (100.540363, 13.67152)
        ],
        # Rooftop 3 - Small residential building
        [
            (100.540073, 13.672405),
            (100.540121, 13.672118),
            (100.540416, 13.672181),
            (100.540352, 13.672478)
        ]
    ]
    sample_rooftops = [
        [(100.540148,13.671842),(100.540164,13.671602),(100.540577,13.67167),(100.54055,13.671899),(100.540534,13.671972),(100.540239,13.67193),(100.540255,13.671847),(100.540148,13.671842)],
        [(100.540212,13.671502),(100.540282,13.671041),(100.540448,13.671069),(100.540363,13.67152),(100.540212,13.671502)],
        [(100.540073,13.672405),(100.540121,13.672118),(100.540416,13.672181),(100.540352,13.672478),(100.540073,13.672405)],
        [(100.540325,13.672155),(100.540363,13.67193),(100.54054,13.671967),(100.540577,13.67191),(100.540727,13.671962),(100.540684,13.672181),(100.540325,13.672155)],
        [(100.540593,13.671503),(100.540668,13.670982),(100.54092,13.671018),(100.540904,13.671159),(100.540963,13.671169),(100.540878,13.671534),(100.540593,13.671503)],
        [(100.54062,13.671889),(100.540647,13.671649),(100.540776,13.671665),(100.540733,13.671915),(100.54062,13.671889)]
    ]    
    # Initialize report generator
    generator = EnhancedSolarReportGenerator(
        use_satellite_data=True,
        thailand_optimized=True
    )
    
    # Generate comprehensive report
    report = generator.process_solar_analysis(
        rooftop_coords_list=sample_rooftops,
        monthly_consumption_kwh=600
    )
    
    return report

if __name__ == "__main__":
    ic(main())
