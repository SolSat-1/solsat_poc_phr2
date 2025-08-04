from pathlib import Path
import numpy as np

from PIL import Image
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

import folium
from folium.plugins import Draw, Fullscreen

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def interpolate_colors(start_color, end_color, n):
    # Accept hex or RGB tuple
    if isinstance(start_color, str): start_color = hex_to_rgb(start_color)
    if isinstance(end_color, str): end_color = hex_to_rgb(end_color)
    start = np.array(start_color)
    end = np.array(end_color)
    ratios = np.linspace(0, 1, n)[:, None]
    return (start * (1 - ratios) + end * ratios).astype(np.uint8)

def render_map(polygons, grid_shape, palettes, show_map=True, tile_layer='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'):


    if not polygons:
        print("No polygons to display.")
        return None

    centroid = polygons[1].centroid  # Center on first
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=18)

    folium.TileLayer(
        tiles=tile_layer,
        attr='Google',
        name='Google Satellite',
        overlay=True,
        control=True
    ).add_to(m)

    # Store overlay file names for cleanup if needed
    overlay_files = []

    # Add overlays for each polygon
    for idx, polygon in enumerate(polygons):
        palette = palettes[idx % len(palettes)]
        fname = str(Path('files') / f'masked_overlay_{idx}.png')
        sw, ne, fname = create_masked_overlay_image(polygon, grid_shape, palette, fname)
        overlay_files.append(fname)
        folium.raster_layers.ImageOverlay(
            name=f'Overlay {idx+1}',
            image=fname,
            bounds=[sw, ne],
            opacity=0.7
        ).add_to(m)
        # folium_coords = [(lat, lon) for lon, lat in polygon.exterior.coords]
        # folium.Polygon(
        #     locations=folium_coords,
        #     color='#FF00FF', weight=0.5, fill=False
        # ).add_to(m)

    folium.LayerControl().add_to(m)
    Fullscreen(position='topright').add_to(m)
    Draw().add_to(m)

    # Show coordinates popup on draw (as before)
    custom_js = """
    <script>
    map.on('draw:created', function (e) {
        var type = e.layerType,
            layer = e.layer;
        if (type === 'polygon') {
            var coords = layer.getLatLngs()[0]
                .map(function(latlng) {
                    return '[' + latlng.lat.toFixed(6) + ', ' + latlng.lng.toFixed(6) + ']';
                })
                .join(',\\n');
            layer.bindPopup('Polygon coordinates:<br>' + coords).openPopup();
            alert('Polygon coordinates:\\n' + coords);
        }
        drawnItems.addLayer(layer);
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(custom_js))

    if show_map:
        m.save(str(Path('files') / 'multi_polygon_map.html'))
        print("Map saved as multi_polygon_map.html")
        return m
    else:
        print("Map not shown (show_map=False)")
        return None

def create_masked_overlay_image(polygon, grid_shape, color_palette, fname='masked_overlay.png'):
    minx, miny, maxx, maxy = polygon.bounds
    xs = np.linspace(minx, maxx, grid_shape[1])
    ys = np.linspace(miny, maxy, grid_shape[0])
    xx, yy = np.meshgrid(xs, ys)
    lonlats = np.column_stack((xx.ravel(), yy.ravel()))
    mask = np.array([polygon.contains(Point(lon, lat)) for lon, lat in lonlats]).reshape(grid_shape)

    # Palette is (start, end), can be hex or RGB
    n_pix = grid_shape[0] * grid_shape[1]
    rgb_colors = interpolate_colors(color_palette[0], color_palette[1], n_pix).reshape(grid_shape[0], grid_shape[1], 3)
    alpha = (mask * 255).astype(np.uint8)
    rgba = np.dstack([rgb_colors, alpha])
    rgba = np.flipud(rgba)  # Correct orientation for mapping
    img = Image.fromarray(rgba, mode='RGBA')
    img.save(fname)
    return (miny, minx), (maxy, maxx), fname

if __name__ == '__main__':
    # Example polygons (list of shapely Polygon)
    coords1 = [(100.540148,13.671842),(100.540164,13.671602),(100.540577,13.67167),(100.54055,13.671899),(100.540534,13.671972),(100.540239,13.67193),(100.540255,13.671847),(100.540148,13.671842)]
    coords2 = [(100.540212,13.671502),(100.540282,13.671041),(100.540448,13.671069),(100.540363,13.67152),(100.540212,13.671502)]
    coords3 = [(100.540073,13.672405),(100.540121,13.672118),(100.540416,13.672181),(100.540352,13.672478),(100.540073,13.672405)]
    coords4 = [(100.540325,13.672155),(100.540363,13.67193),(100.54054,13.671967),(100.540577,13.67191),(100.540727,13.671962),(100.540684,13.672181),(100.540325,13.672155)]
    coords5 = [(100.540593,13.671503),(100.540668,13.670982),(100.54092,13.671018),(100.540904,13.671159),(100.540963,13.671169),(100.540878,13.671534),(100.540593,13.671503)]
    coords6 = [(100.54062,13.671889),(100.540647,13.671649),(100.540776,13.671665),(100.540733,13.671915),(100.54062,13.671889)]

    polygons = [Polygon(coords1), Polygon(coords2), Polygon(coords3), Polygon(coords4), Polygon(coords5), Polygon(coords6)]
    
    # Palettes: list of (start, end) colors (RGB or hex)
    palettes = [
        ((255, 165, 0), (255, 255, 255)),        # Orange to white
        ('#5efc8d', '#35a7ff'),                  # Mint to blue
        ((255,0,0), (255,255,0)),                # Red to yellow
    ]

    # create store image
    Path('files').mkdir(exist_ok=True)

    # Call with as many polygons as you want; palettes are cycled
    render_map(
        polygons=polygons,
        grid_shape=(100, 100),
        palettes=palettes[:2],    # Pick 2 palettes for 2 polygons
        show_map=True
    )