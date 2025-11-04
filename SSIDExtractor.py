import re

class SSIDExtractor:
    """
    Extracts SSIDs from raw Wi-Fi capture data.
    Ensures that invalid, placeholder, or 'wildcard' SSIDs are ignored.
    """

    def extract_ssids(self, raw_data):
        """
        Parses capture text lines and returns a list of unique SSIDs.
        """
        ssids = set()
        for line in raw_data:
            match = re.search(r'SSID="([^"]+)"', line)
            if match:
                ssid = match.group(1).strip()
                # Skip empty, placeholder, or generic entries
                if ssid and not ssid.lower().startswith("wildcard") and not ssid.startswith("0000"):
                    ssids.add(ssid)

        print(f"[SSIDExtractor] Extracted {len(ssids)} unique SSIDs.")
        return list(ssids)