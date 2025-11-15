import os
import time
import json
import requests
from dotenv import load_dotenv
from MapVisualiser import MapVisualiser

load_dotenv()

class GeoMapper:
    """
    Maps SSIDs to approximate geographic coordinates using the WiGLE API,
    with built-in caching, polite rate limiting, and individual map generation.
    """

    def __init__(self, api_name=None, api_token=None, delay=2.0, cache_path="data/wigle_cache.json", 
                 generate_individual_maps=True, maps_output_dir="data/maps", validator=None):
        self.api_name = api_name or os.getenv("WIGLE_API_NAME")
        self.api_token = api_token or os.getenv("WIGLE_API_TOKEN")
        self.api_url = "https://api.wigle.net/api/v2/network/search"
        self.delay = float(delay)
        self.cache_path = cache_path
        self.generate_individual_maps = generate_individual_maps
        self.maps_output_dir = maps_output_dir
        self.validator = validator
        self.mock_mode = not (self.api_name and self.api_token)

        # Load or create cache
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        self.cache = self._load_cache()
        
        # Initialize map visualiser for individual map generation
        if self.generate_individual_maps:
            self.visualiser = MapVisualiser()
            os.makedirs(maps_output_dir, exist_ok=True)
            
        # Track new discoveries in this session to avoid duplicate map generation
        self.new_discoveries = set()

    # -------------------------------
    # Cache handling
    # -------------------------------
    def _load_cache(self):
        """Load previously stored SSID locations from cache."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    print(f"[GeoMapper] Loaded cache from {self.cache_path}")
                    return json.load(f)
            except Exception as e:
                print(f"[GeoMapper] Failed to load cache: {e}")
        return {}

    def _save_cache(self):
        """Save the current cache to file."""
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
            print(f"[GeoMapper] Cache saved ({len(self.cache)} entries)")
        except Exception as e:
            print(f"[GeoMapper] Failed to save cache: {e}")

    # -------------------------------
    # WiGLE querying
    # -------------------------------
    def query_wigle(self, ssid):
        """Query WiGLE API for a specific SSID or return cached result."""
        ssid = ssid.strip()
        if not ssid:
            return None

        # Check if we have this SSID in cache (successful or failed)
        if ssid in self.cache:
            cached_result = self.cache[ssid]
            
            # If it's a failed lookup (stored as dict with failed flag), skip it
            if isinstance(cached_result, dict) and cached_result.get("failed", False):
                print(f"[GeoMapper] Skipping previously failed SSID: {ssid}")
                return None
            
            # It's a successful cached result
            print(f"[GeoMapper] Cached: {ssid} -> {cached_result}")
            
            # Only generate map for cached results if no map was previously generated
            # and this SSID hasn't been processed in current session
            if (self.generate_individual_maps and cached_result and 
                ssid not in self.new_discoveries and 
                not cached_result.get("map_generated", False)):
                
                map_path = self.visualiser.create_individual_map(
                    cached_result, self.maps_output_dir
                )
                if map_path:
                    print(f"[GeoMapper] First-time map generated for cached SSID: {map_path}")
                    # Mark that a map has been generated for this SSID
                    cached_result["map_generated"] = True
                    self.cache[ssid] = cached_result
                    self._save_cache()
                    if self.validator:
                        self.validator.log_map_generation(map_path, "individual", cached_result["ssid"])
                    self.new_discoveries.add(ssid)
            
            return cached_result

        # Mock mode if credentials missing
        if self.mock_mode:
            print(f"[GeoMapper] Mock mode active — skipping WiGLE lookup for '{ssid}'")
            return None

        params = {"ssid": ssid, "resultsPerPage": 1}
        print(f"[GeoMapper] Querying WiGLE for SSID: {ssid}")

        try:
            resp = requests.get(
                self.api_url,
                params=params,
                auth=(self.api_name, self.api_token),
                timeout=15
            )
        except requests.RequestException as e:
            print(f"[GeoMapper] Network error for '{ssid}': {e}")
            # Cache the failure to avoid retrying
            self.cache[ssid] = {"failed": True, "reason": f"Network error: {e}"}
            self._save_cache()
            return None

        if resp.status_code != 200:
            print(f"[GeoMapper] WiGLE error {resp.status_code} for '{ssid}'")
            # Cache the failure to avoid retrying
            self.cache[ssid] = {"failed": True, "reason": f"HTTP {resp.status_code}"}
            self._save_cache()
            return None

        try:
            data = resp.json()
        except ValueError:
            print(f"[GeoMapper] Invalid JSON response for '{ssid}'")
            # Cache the failure to avoid retrying
            self.cache[ssid] = {"failed": True, "reason": "Invalid JSON"}
            self._save_cache()
            return None

        if data.get("success") and data.get("resultCount", 0) > 0:
            result = data["results"][0]
            lat, lon = result.get("trilat"), result.get("trilong")
            if lat and lon:
                loc_data = {"ssid": ssid, "lat": lat, "lon": lon, "map_generated": False}
                self.cache[ssid] = loc_data
                print(f"[GeoMapper] Found {ssid} at ({lat}, {lon}) — cached")
                self._save_cache()
                
                # Generate individual map for NEW successful API hit
                if self.generate_individual_maps:
                    map_path = self.visualiser.create_individual_map(
                        loc_data, self.maps_output_dir
                    )
                    if map_path:
                        print(f"[GeoMapper] NEW discovery map generated: {map_path}")
                        # Mark that a map has been generated for this SSID
                        loc_data["map_generated"] = True
                        self.cache[ssid] = loc_data
                        self._save_cache()
                        if self.validator:
                            self.validator.log_map_generation(map_path, "individual", ssid)
                        self.new_discoveries.add(ssid)
                
                return loc_data

        # No valid result found - cache this failure
        print(f"[GeoMapper] No valid result for '{ssid}' — cached as failed")
        self.cache[ssid] = {"failed": True, "reason": "No location data found"}
        self._save_cache()
        return None

    # -------------------------------
    # Batch mapping
    # -------------------------------
    def map_all(self, ssid_list):
        """Query multiple SSIDs with caching and delay."""
        results = []
        for i, ssid in enumerate(ssid_list, start=1):
            print(f"[GeoMapper] Processing SSID {i}/{len(ssid_list)}: {ssid}")
            loc = self.query_wigle(ssid)
            if loc:
                results.append(loc)

            # Sleep between API calls unless this was a cached result
            if not self.mock_mode and ssid not in self.cache and i < len(ssid_list):
                print(f"[GeoMapper] Sleeping for {self.delay} seconds to avoid rate limits...")
                time.sleep(self.delay)

        print(f"[GeoMapper] Completed mapping {len(results)} SSIDs (cached + live).")
        
        # Generate summary map if we have results and individual map generation is enabled
        if results and self.generate_individual_maps:
            summary_path = self.visualiser.create_summary_map(results, "data/maps/Full Map")
            if summary_path:
                print(f"[GeoMapper] Summary map generated: {summary_path}")
        
        return results

    def get_stats(self):
        """Get statistics about processed SSIDs."""
        successful_cache = {k: v for k, v in self.cache.items() if isinstance(v, dict) and not v.get("failed", False)}
        failed_cache = {k: v for k, v in self.cache.items() if isinstance(v, dict) and v.get("failed", False)}
        
        return {
            "total_cached": len(self.cache),
            "successful_cached": len(successful_cache),
            "failed_cached": len(failed_cache),
            "new_discoveries_this_session": len(self.new_discoveries),
            "cache_file": self.cache_path,
            "maps_directory": self.maps_output_dir if self.generate_individual_maps else None,
            "individual_maps_enabled": self.generate_individual_maps
        }
