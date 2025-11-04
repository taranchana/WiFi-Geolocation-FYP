import os
import requests
import time

class GeoMapper:
    """
    Maps SSIDs to approximate geographic coordinates using the WiGLE API.
    Operates in 'mock mode' when no credentials are provided for ethical testing.
    """

    def __init__(self):
        # Securely obtain WiGLE credentials from environment variables
        self.api_name = os.getenv("WIGLE_API_NAME")
        self.api_token = os.getenv("WIGLE_API_TOKEN")
        self.base_url = "https://api.wigle.net/api/v2/network/search"
        self.mock_mode = not (self.api_name and self.api_token)

    def lookup(self, ssid: str):
        """
        Looks up one SSID on the WiGLE API and returns its coordinates.
        Returns mock data when credentials are missing.
        """
        if self.mock_mode:
            print(f"[GeoMapper] Mock lookup for {ssid}")
            return {
                "ssid": ssid,
                "lat": 52.4862,     # Example: Birmingham coordinates
                "lon": -1.8904,
                "address": "Mock Location"
            }

        print(f"[GeoMapper] Querying WiGLE for SSID: {ssid}")
        try:
            response = requests.get(
                self.base_url,
                auth=(self.api_name, self.api_token),
                params={"ssid": ssid, "resultsPerPage": 1},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("resultCount", 0) > 0:
                    result = data["results"][0]
                    return {
                        "ssid": ssid,
                        "lat": result.get("trilat"),
                        "lon": result.get("trilong"),
                        "address": result.get("road", "Unknown")
                    }
                else:
                    print(f"[GeoMapper] No results found for {ssid}")
            else:
                print(f"[GeoMapper] API request failed ({response.status_code})")

        except requests.RequestException as e:
            print(f"[GeoMapper] Error connecting to WiGLE: {e}")

        return {"ssid": ssid, "lat": None, "lon": None, "address": None}

    def batch_lookup(self, ssid_list):
        """
        Performs multiple lookups with a short delay between each
        to respect API rate limits.
        """
        results = []
        for ssid in ssid_list:
            results.append(self.lookup(ssid))
            time.sleep(2)
        return results