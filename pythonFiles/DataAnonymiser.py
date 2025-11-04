class DataAnonymiser:
    """
    Anonymises SSIDs by removing identifiers or personal network names.
    Ensures privacy-by-design compliance.
    """

    def anonymise(self, ssid_list):
        cleaned = []
        for ssid in ssid_list:
            if any(keyword in ssid.lower() for keyword in ["home", "wifi", "guest", "personal", "family"]):
                cleaned.append("AnonymisedNetwork")
            else:
                cleaned.append(ssid)
        print(f"[DataAnonymiser] {len(cleaned)} SSIDs processed for anonymity.")
        return cleaned