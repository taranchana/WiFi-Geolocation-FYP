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

    def _add_legend(self, folium_map, all_locations, total_ssids=None):
        """
        Inject a statistics and explanation legend panel into the map HTML.
        Addresses NFR4: map must be interpretable without technical background.
        """
        located = len(all_locations)
        total = total_ssids if total_ssids else located
        hit_rate = (located / total * 100) if total > 0 else 0

        legend_html = f"""
        <div style="
            position: fixed;
            bottom: 30px;
            left: 30px;
            z-index: 1000;
            background-color: white;
            border: 2px solid #444;
            border-radius: 8px;
            padding: 14px 18px;
            font-family: Arial, sans-serif;
            font-size: 13px;
            box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
            max-width: 260px;
            line-height: 1.5;
        ">
            <b style="font-size:14px;"> Wi-Fi Geo-Map</b>
            <hr style="margin: 6px 0; border-color: #ccc;">
            <b>What this shows:</b><br>
            Each marker is a Wi-Fi network (SSID) whose name was matched in the
            WiGLE crowdsourced database, revealing an approximate location where
            that network has previously been observed, captured passively from
            a single device.
            <hr style="margin: 6px 0; border-color: #ccc;">
            <b>Session Statistics:</b><br>
            SSIDs located: <b>{located}</b><br>
            SSIDs captured: <b>{total}</b><br>
            Geolocation rate: <b>{hit_rate:.1f}%</b>
            <hr style="margin: 6px 0; border-color: #ccc;">
            <span style="color:#2874a6;">&#11044;</span> Located Wi-Fi network<br>
        </div>
        """
        folium_map.get_root().html.add_child(folium.Element(legend_html))

    def create_summary_map(self, all_locations, output_dir="data/maps/Full Map", total_ssids=None):
        """
        Create a summary map showing all successful locations.
        Includes a legend and statistics panel to satisfy NFR4.
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

        # Add legend and statistics panel (addresses NFR4)
        self._add_legend(self.map, all_locations, total_ssids=total_ssids)

        if self.save_map(str(filepath)):
            return str(filepath)
        return None