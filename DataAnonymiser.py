class DataAnonymiser:
    """
    Placeholder anonymiser class.
    Currently passes SSID data through without modification.
    This keeps the project structure consistent while disabling anonymisation.
    """

    def anonymise(self, ssid_list):
        """
        Returns SSIDs exactly as provided.
        No filtering or renaming applied.
        """
        print(f"[DataAnonymiser] Skipping anonymisation — {len(ssid_list)} SSIDs returned unchanged.")
        return ssid_list