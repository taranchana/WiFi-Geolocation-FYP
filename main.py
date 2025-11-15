import time
import webbrowser
from pathlib import Path
from CaptureManager import CaptureManager
from SSIDExtractor import SSIDExtractor
from GeoMapper import GeoMapper
from MapVisualiser import MapVisualiser
from DataValidator import DataValidator


def main():
    print("[App] Starting WiFi GeoMapper - Processing All SSIDs from Capture Data...\n")

    # Initialize data validator for logging and statistics
    validator = DataValidator()

    # Step 1: Load capture data
    capture_path = Path("data/wifi-ssid-captures.txt")
    if not capture_path.exists():
        print(f"[Error] Capture file not found at: {capture_path}")
        return

    capture_manager = CaptureManager(capture_path)
    lines = capture_manager.read_capture()
    print(f"[App] Loaded {len(lines)} lines from capture file.")

    # Step 2: Extract and filter SSIDs
    extractor = SSIDExtractor()
    ssids = extractor.extract_ssids(lines)
    
    # Log extraction results
    validator.log_extraction_results(extractor, len(lines), ssids)
    
    if not ssids:
        print("[App] No valid SSIDs found in capture file after filtering.")
        validator.save_session_log()
        return

    print(f"[App] Found {len(ssids)} valid SSIDs after filtering:")
    for i, ssid in enumerate(ssids[:10], 1):  # Show first 10
        print(f"  {i}. {ssid}")
    if len(ssids) > 10:
        print(f"  ... and {len(ssids) - 10} more")
    print()

    # Step 3: Query WiGLE for each SSID with individual map generation
    print("[App] Querying WiGLE API and generating individual maps...\n")
    
    # Initialize mapper with individual map generation enabled
    mapper = GeoMapper(
        delay=8.0,  # 8 seconds between calls to avoid 429 errors
        generate_individual_maps=True,
        maps_output_dir="data/maps",
        validator=validator
    )
    
    # Process SSIDs individually to integrate with validator logging
    mapped_locations = []
    for i, ssid in enumerate(ssids, 1):
        print(f"[App] Processing SSID {i}/{len(ssids)}: {ssid}")
        
        loc = mapper.query_wigle(ssid)
        
        if loc:
            # Validate coordinates
            is_valid, validation_msg = validator.validate_coordinates(loc["lat"], loc["lon"])
            if is_valid:
                mapped_locations.append(loc)
                validator.log_api_query(ssid, True, loc)
                print(f"[App] ✓ Successfully mapped {ssid}")
            else:
                validator.log_api_query(ssid, False, error=f"Coordinate validation failed: {validation_msg}")
                print(f"[App] ✗ Invalid coordinates for {ssid}: {validation_msg}")
        else:
            validator.log_api_query(ssid, False, error="No location data returned")
            print(f"[App] ✗ No location found for {ssid}")

        # Sleep between API calls unless this was a cached result
        if not mapper.mock_mode and ssid not in mapper.cache and i < len(ssids):
            print(f"[App] Sleeping for {mapper.delay} seconds to avoid rate limits...")
            time.sleep(mapper.delay)

    if not mapped_locations:
        print("[App] No valid location data returned from WiGLE.")
        validator.save_session_log()
        return

    print(f"\n[App] Successfully mapped {len(mapped_locations)} SSIDs to locations:")
    for loc in mapped_locations:
        print(f"  - {loc['ssid']}: ({loc['lat']:.6f}, {loc['lon']:.6f})")

    # Step 4: Generate final summary map and open it
    print("\n[App] Generating final summary map...")
    visualiser = MapVisualiser()
    visualiser.create_map(mapped_locations)
    visualiser.plot_points(mapped_locations)
    
    summary_map_path = Path("data/maps/Full Map/WiFiGeoMap_all_locations.html")
    if visualiser.save_map(summary_map_path):
        validator.log_map_generation(summary_map_path, "summary")
        print(f"[App] Summary map generated successfully: {summary_map_path}")
        print("[App] Opening summary map in your default browser...\n")
        webbrowser.open(summary_map_path.resolve().as_uri())

    # Step 5: Save session log and display statistics
    log_file = validator.save_session_log()
    validator.print_session_summary()
    
    # Enhanced statistics with cache information
    stats = mapper.get_stats()
    print("\n[App] Cache Statistics:")
    print(f"  - Total cache entries: {stats['total_cached']}")
    print(f"  - Successful locations: {stats['successful_cached']}")
    print(f"  - Failed lookups (skipped): {stats['failed_cached']}")
    print(f"  - New discoveries this session: {stats['new_discoveries_this_session']}")
    print(f"  - New maps generated: {stats['new_discoveries_this_session']}")
    
    if log_file:
        print(f"\nDetailed session log saved to: {log_file}")

    print("\n[App] Complete! Check the data/maps/ directory for individual maps.")
    print(f"[App] Summary map saved to: data/maps/Full Map/WiFiGeoMap_all_locations.html")


if __name__ == "__main__":
    main()
