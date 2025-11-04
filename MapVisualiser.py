import folium

class MapVisualiser:
    """
    Visualises SSID location data on an interactive map using Folium.
    """

    def display_map(self, mapped_data):
        print("[MapVisualiser] Generating map...")
        map_obj = folium.Map(location=[52.4862, -1.8904], zoom_start=12)

        for entry in mapped_data:
            if entry["lat"] and entry["lon"]:
                folium.Marker(
                    [entry["lat"], entry["lon"]],
                    popup=entry["ssid"],
                    icon=folium.Icon(color="blue", icon="wifi", prefix="fa")
                ).add_to(map_obj)

        map_obj.save("WiFiGeoMap.html")
        print("[MapVisualiser] Map saved as WiFiGeoMap.html")