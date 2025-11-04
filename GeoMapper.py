import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class GeoMapper:
    """
    Maps SSIDs to approximate geographic coordinates using the WiGLE API,
    with built-in caching and polite rate limiting.
    """

    def __init__(self, api_name=None, api_token=None, delay=2.0, cache_path="data/wigle_cache.json"):
        self.api_name = api_name or os.getenv("WIGLE_API_NAME")
        self.api_token = api_token or os.getenv("WIGLE_API_TOKEN")
        self.api_url = "https://api.wigle.net/api/v2/network/search"
        self.delay = float(delay)
        self.cache_path = cache_path
        self.mock_mode = not (self.api_name and self.api_token)

        # Load or create cache
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        self.cache = self._load_cache()

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

        # Return cached result if available
        if ssid in self.cache:
            print(f"[GeoMapper] Cached: {ssid} -> {self.cache[ssid]}")
            return self.cache[ssid]

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
            return None

        if resp.status_code != 200:
            print(f"[GeoMapper] WiGLE error {resp.status_code} for '{ssid}'")
            return None

        try:
            data = resp.json()
        except ValueError:
            print(f"[GeoMapper] Invalid JSON response for '{ssid}'")
            return None

        if data.get("success") and data.get("resultCount", 0) > 0:
            result = data["results"][0]
            lat, lon = result.get("trilat"), result.get("trilong")
            if lat and lon:
                loc_data = {"ssid": ssid, "lat": lat, "lon": lon}
                self.cache[ssid] = loc_data
                print(f"[GeoMapper] Found {ssid} at ({lat}, {lon}) — cached")
                self._save_cache()
                return loc_data

        print(f"[GeoMapper] No valid result for '{ssid}'")
        return None

    # -------------------------------
    # Batch mapping
    # -------------------------------
    def map_all(self, ssid_list):
        """Query multiple SSIDs with caching and delay."""
        results = []
        for i, ssid in enumerate(ssid_list, start=1):
            loc = self.query_wigle(ssid)
            if loc:
                results.append(loc)

            # Sleep between API calls unless this was a cached result
            if not self.mock_mode and ssid not in self.cache:
                print(f"[GeoMapper] Sleeping for {self.delay} seconds to avoid rate limits...")
                time.sleep(self.delay)

        print(f"[GeoMapper] Completed mapping {len(results)} SSIDs (cached + live).")
        return results
