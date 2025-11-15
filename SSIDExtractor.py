import re

class SSIDExtractor:
    """
    Extracts SSIDs from raw Wi-Fi capture data.
    Ensures that invalid, placeholder, or 'wildcard' SSIDs are ignored.
    """

    def __init__(self):
        self.filtered_count = 0
        self.filter_reasons = {}

    def _is_valid_ssid(self, ssid):
        """
        Enhanced validation to filter out illogical SSIDs.
        Returns (is_valid, reason) tuple.
        """
        if not ssid:
            return False, "empty"
        
        # Remove surrounding quotes if present
        ssid = ssid.strip('"')
        
        # Check minimum/maximum length (SSIDs can be 1-32 chars)
        if len(ssid) < 1 or len(ssid) > 32:
            return False, "invalid_length"
        
        # Filter out placeholder/broadcast SSIDs
        if ssid.startswith("0000") or ssid == "000000000000000000":
            return False, "placeholder_zeros"
            
        # Filter out wildcard SSIDs
        if ssid.lower().startswith("wildcard"):
            return False, "wildcard"
            
        # Filter out hidden/broadcast network patterns
        if re.match(r'^[0-9a-fA-F]{12,}$', ssid):  # Hex patterns likely MAC addresses
            return False, "hex_pattern"
            
        # Filter out SSIDs with only whitespace or special chars
        if not re.search(r'[a-zA-Z0-9]', ssid):
            return False, "no_alphanumeric"
            
        # Filter out SSIDs with invalid characters (control chars, etc)
        if any(ord(c) < 32 or ord(c) > 126 for c in ssid if c not in [' ']):
            return False, "invalid_characters"
            
        # Filter out common test/placeholder patterns
        placeholder_patterns = [
            r'^test',
            r'^default',
            r'^linksys',
            r'^netgear',
            r'^dlink',
            r'^admin',
            r'^setup'
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, ssid, re.IGNORECASE):
                return False, "common_placeholder"
        
        return True, "valid"

    def extract_ssids(self, raw_data):
        """
        Parses capture text lines and returns a list of unique, valid SSIDs.
        """
        ssids = set()
        self.filtered_count = 0
        self.filter_reasons = {}
        
        for line in raw_data:
            # Look for SSID patterns in the capture data
            match = re.search(r'SSID="([^"]*)"', line)  # Allow empty quotes too
            if not match:
                # Also try pattern without quotes
                match = re.search(r'SSID=([^\s,]+)', line)
                
            if match:
                ssid = match.group(1).strip()
                is_valid, reason = self._is_valid_ssid(ssid)
                
                if is_valid:
                    ssids.add(ssid)
                else:
                    self.filtered_count += 1
                    self.filter_reasons[reason] = self.filter_reasons.get(reason, 0) + 1

        print(f"[SSIDExtractor] Extracted {len(ssids)} unique SSIDs.")
        print(f"[SSIDExtractor] Filtered out {self.filtered_count} invalid SSIDs:")
        for reason, count in self.filter_reasons.items():
            print(f"  - {reason}: {count}")
            
        return list(ssids)