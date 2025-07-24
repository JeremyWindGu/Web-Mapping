import os
from collections import Counter

import geopandas as gpd
import folium
from shapely.geometry import Point

def load_geojson(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist")
    return gpd.read_file(path)

def prepare_data(gdf):
    pts = [geom if isinstance(geom, Point) else geom.centroid for geom in gdf.geometry]

    line_coords = [(pt.y, pt.x) for pt in pts]

    coord_counter = Counter(line_coords)
    weighted = [(coord, coord_counter[coord]) for coord in coord_counter]

    return line_coords, weighted

def create_map(line_coords, weighted, center, zoom_start=10):
    MAPBOX_TOKEN = "pk.eyJ1IjoiamVyZW15d2luZGd1IiwiYSI6ImNtY3UxMGdoOTAxcGEyaW9xMGJheW5ybzEifQ.3awWC_TU0b4RdbVmRnaf5g"

    MAPBOX_STYLE = "mapbox/dark-v10"

    tiles_url = (
        f"https://api.mapbox.com/styles/v1/{MAPBOX_STYLE}/tiles/256/"
        f"{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}"
    )

    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles=None,
        control_scale=True
    )

    folium.TileLayer(
        tiles=tiles_url,
        attr="Mapbox",
        name="Mapbox",
        overlay=False,
        control=True
    ).add_to(m)

    folium.PolyLine(
        locations=line_coords,
        color="#FF007C",
        weight=2,
        opacity=0.8,
        tooltip="Link"
    ).add_to(m)

    for (lat, lon), count in weighted:
        folium.CircleMarker(
            location=(lat, lon),
            radius=5 + count * 2,
            color="#00FFD1",
            fill=True,
            fill_opacity=0.6,
            tooltip=f"Overlap {count} times"
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

if __name__ == "__main__":
    geojson_path = "Steam.geojson"
    gdf = load_geojson(geojson_path)

    line_coords, weighted = prepare_data(gdf)

    lats = [lat for lat, lon in line_coords]
    lons = [lon for lat, lon in line_coords]
    center = (sum(lats) / len(lats), sum(lons) / len(lons))

    m = create_map(line_coords, weighted, center, zoom_start=12)
    
    base_name = os.path.splitext(os.path.basename(geojson_path))[0]
    output_html = f"Map_of_{base_name}.html"
    m.save(output_html)
    print(f"The map has been saved to {output_html}")