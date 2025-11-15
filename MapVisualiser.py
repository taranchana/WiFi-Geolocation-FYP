import folium
import os
from datetime import datetime
from pathlib import Path

class MapVisualiser:
    def __init__(self, default_location=[51.5074, -0.1278], default_zoom=6):
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
        Create a new map, optionally centered on provided locations.
        If locations provided, center on them; otherwise use default location.
        """
        if locations and len(locations) > 0:
            # Calculate center point from all locations
            avg_lat = sum(loc["lat"] for loc in locations) / len(locations)
            avg_lon = sum(loc["lon"] for loc in locations) / len(locations)
            center = [avg_lat, avg_lon]
            
            # Determine appropriate zoom level based on location spread
            if len(locations) == 1:
                zoom = 15  # Close zoom for single location
            else:
                # Calculate rough distance spread to determine zoom
                lat_spread = max(loc["lat"] for loc in locations) - min(loc["lat"] for loc in locations)
                lon_spread = max(loc["lon"] for loc in locations) - min(loc["lon"] for loc in locations)
                max_spread = max(lat_spread, lon_spread)
                
                if max_spread < 0.01:    # Very close locations
                    zoom = 14
                elif max_spread < 0.1:   # City-level spread
                    zoom = 11
                elif max_spread < 1:     # Regional spread
                    zoom = 8
                else:                    # Country/continent level
                    zoom = 6
        else:
            center = self.default_location
            zoom = self.default_zoom
        
        self.map = folium.Map(location=center, zoom_start=zoom)
        return self.map

    def plot_points(self, locations):
        """Add markers for all known SSID locations."""
        if not self.map:
            self.create_map(locations)
            
        for loc in locations:
            folium.Marker(
                [loc["lat"], loc["lon"]],
                popup=f'SSID: {loc["ssid"]}<br>Lat: {loc["lat"]:.6f}<br>Lon: {loc["lon"]:.6f}',
                tooltip=f'SSID: {loc["ssid"]}',
                icon=folium.Icon(color="blue", icon="wifi", prefix="fa")
            ).add_to(self.map)

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
            zoom_start=15
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
            
        filename = f"WiFiGeoMap_all_locations.html"
        filepath = Path(output_dir) / filename
        
        # Create map and plot all points
        self.create_map(all_locations)
        self.plot_points(all_locations)
        
        # Save the summary map
        if self.save_map(str(filepath)):
            return str(filepath)
        return None