# main.py
import csv
import webbrowser
from pathlib import Path
from CaptureManager import CaptureManager
from SSIDExtractor import SSIDExtractor
from GeoMapper import GeoMapper
from MapVisualiser import MapVisualiser


def main():
    print("[App] Starting WiFi GeoMapper...\n")

    # Step 1: Load Wi-Fi capture data
    capture_manager = CaptureManager("data/wifi-ssid-captures.txt")
    lines = capture_manager.read_capture()  # ✅ fixed method name
    print(f"[App] Loaded {len(lines)} lines from capture file.")

    # Step 2: Extract unique SSIDs
    extractor = SSIDExtractor()
    ssid_list = extractor.extract_ssids(lines)
    print(f"[App] Extracted {len(ssid_list)} unique SSIDs.\n")

    if not ssid_list:
        print("[App] No SSIDs found. Exiting.")
        return

    # Step 3: Map SSIDs to locations using WiGLE API (with caching + delay)
    mapper = GeoMapper(delay=2.5)  # polite delay between API requests
    mapped_locations = mapper.map_all(ssid_list)

    if not mapped_locations:
        print("[App] No valid location data returned. Exiting.")
        return

    # Step 4: Save results to CSV
    csv_path = Path("data/mapped_results.csv")
    csv_path.parent.mkdir(exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ssid", "lat", "lon"])
        writer.writeheader()
        writer.writerows(mapped_locations)
    print(f"[App] Saved mapped results to {csv_path}\n")

    # Step 5: Visualise results on an interactive map
    visualiser = MapVisualiser()
    visualiser.plot_points(mapped_locations)
    map_path = Path("data/WiFiGeoMap.html")
    visualiser.save_map(map_path)
    print(f"[App] Map generated: {map_path}")

    # Step 6: Automatically open the map in your default browser
    print("[App] Opening map in your default browser...\n")
    webbrowser.open(map_path.resolve().as_uri())

    print("[App] Process complete — map and CSV ready for review!")


if __name__ == "__main__":
    main()
