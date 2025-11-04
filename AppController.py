from CaptureManager import CaptureManager
from SSIDExtractor import SSIDExtractor
from DataAnonymiser import DataAnonymiser
from GeoMapper import GeoMapper
from MapVisualiser import MapVisualiser

class AppController:
    """
    Coordinates the full Wi-Fi SSID mapping workflow:
    1. Load capture data
    2. Extract SSIDs
    3. Anonymise data
    4. Query locations (WiGLE)
    5. Display interactive map
    """

    def __init__(self, capture_file="data/wifi-ssid-captures.txt"):
        self.capture_manager = CaptureManager(capture_file)
        self.extractor = SSIDExtractor()
        self.anonymiser = DataAnonymiser()
        self.mapper = GeoMapper()
        self.visualiser = MapVisualiser()

    def run(self):
        """Runs the end-to-end workflow."""
        raw_data = self.capture_manager.read_capture()
        ssids = self.extractor.extract_ssids(raw_data)
        safe_ssids = self.anonymiser.anonymise(ssids)
        mapped_data = self.mapper.batch_lookup(safe_ssids)
        self.visualiser.display_map(mapped_data)
        print("[AppController] Workflow complete — map generated.")