import folium
import os
from datetime import datetime
from pathlib import Path

class MapVisualiser:
    def __init__(self, default_location=[20, 0], default_zoom=6):
        """
        Initialize MapVisualiser with configurable defaults.
        default_location: [lat, lon] for initial map center (default: London)
        default_zoom: initial zoom level
        """
        self.default_location = default_location
        self.default_zoom = default_zoom
        self.map = None

    def create_map(self, locations=None):
        """
        Create a new map.
        If locations are tightly grouped, centre on them.
        If locations are globally spread, use a fixed world view.
        """
        if locations and len(locations) > 0:
            if len(locations) == 1:
                center = [locations[0]["lat"], locations[0]["lon"]]
                zoom = 15
            else:
                lat_spread = max(loc["lat"] for loc in locations) - min(loc["lat"] for loc in locations)
                lon_spread = max(loc["lon"] for loc in locations) - min(loc["lon"] for loc in locations)
                max_spread = max(lat_spread, lon_spread)

                # If points are globally spread, use a balanced world view
                if max_spread > 20:
                    center = [20, 0]
                    zoom = 2
                else:
                    avg_lat = sum(loc["lat"] for loc in locations) / len(locations)
                    avg_lon = sum(loc["lon"] for loc in locations) / len(locations)
                    center = [avg_lat, avg_lon]

                    if max_spread < 0.01:
                        zoom = 14
                    elif max_spread < 0.1:
                        zoom = 11
                    elif max_spread < 1:
                        zoom = 8
                    else:
                        zoom = 6
        else:
            center = self.default_location
            zoom = self.default_zoom

        self.map = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles="CartoDB positron"
        )
        return self.map

    def plot_points(self, locations):
        """Add markers for all known SSID locations."""
        if not self.map:
            self.create_map(locations)

        bounds = []

        for loc in locations:
            coords = [loc["lat"], loc["lon"]]
            bounds.append(coords)

            folium.Marker(
                coords,
                popup=f'SSID: {loc["ssid"]}<br>Lat: {loc["lat"]:.6f}<br>Lon: {loc["lon"]:.6f}',
                tooltip=f'SSID: {loc["ssid"]}',
                icon=folium.Icon(color="blue", icon="wifi", prefix="fa")
            ).add_to(self.map)

        if bounds:
            self.map.fit_bounds(bounds)

    def save_map(self, filename="WiFiGeoMap.html"):
        """Save the current map to file."""
        if not self.map:
            print("[MapVisualiser] No map to save - create a map first")
            return False
            
        try:
            # Ensure directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            self.map.save(filename)
            print(f"[MapVisualiser] Map saved as {filename}")
            return True
        except Exception as e:
            print(f"[MapVisualiser] Error saving map: {e}")
            return False

    def create_individual_map(self, location_data, output_dir="data/maps"):
        """
        Create and save an individual map for a single location.
        Returns the path to the saved map file.
        """
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_ssid = "".join(c for c in location_data["ssid"] if c.isalnum() or c in "._-")
        filename = f"WiFiGeoMap_{safe_ssid}_{timestamp}.html"
        filepath = Path(output_dir) / filename
        
        # Create map centered on this location
        single_location_map = folium.Map(
            location=[location_data["lat"], location_data["lon"]],
            zoom_start=15,
            tiles="CartoDB positron"
        )
        
        # Add marker for this location
        folium.Marker(
            [location_data["lat"], location_data["lon"]],
            popup=f'''
            <b>SSID:</b> {location_data["ssid"]}<br>
            <b>Latitude:</b> {location_data["lat"]:.6f}<br>
            <b>Longitude:</b> {location_data["lon"]:.6f}<br>
            <b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            ''',
            tooltip=f'SSID: {location_data["ssid"]}',
            icon=folium.Icon(color="red", icon="wifi", prefix="fa")
        ).add_to(single_location_map)
        
        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the map
        try:
            single_location_map.save(str(filepath))
            print(f"[MapVisualiser] Individual map saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"[MapVisualiser] Error saving individual map: {e}")
            return None

    def create_summary_map(self, all_locations, output_dir="data/maps/Full Map"):
        """
        Create a summary map showing all successful locations.
        Returns the path to the saved summary map.
        """
        if not all_locations:
            print("[MapVisualiser] No locations to create summary map")
            return None

        filename = "WiFiGeoMap_all_locations.html"
        filepath = Path(output_dir) / filename

        # Force a balanced global view for the summary map
        self.map = folium.Map(
            location=[20, 0],
            zoom_start=2,
            tiles="CartoDB positron"
        )
        self.plot_points(all_locations)

        if self.save_map(str(filepath)):
            return str(filepath)
        return None