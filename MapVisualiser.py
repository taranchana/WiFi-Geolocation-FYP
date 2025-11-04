import folium

class MapVisualiser:
    def __init__(self):
        self.map = folium.Map(location=[51.5074, -0.1278], zoom_start=6)  # Default: London-ish

    def plot_points(self, locations):
        """Add markers for all known SSID locations."""
        for loc in locations:
            folium.Marker(
                [loc["lat"], loc["lon"]],
                popup=f'SSID: {loc["ssid"]}',
                icon=folium.Icon(color="blue", icon="wifi", prefix="fa")
            ).add_to(self.map)

    def save_map(self, filename="WiFiGeoMap.html"):
        self.map.save(filename)
        print(f"[MapVisualiser] Map saved as {filename}")