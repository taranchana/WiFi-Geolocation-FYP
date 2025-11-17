# WiFi-Geolocation-FYP
WiFi Geo Mapping is a Python proof-of-concept that captures Wi-Fi Probe Requests, extracts SSIDs, and visualises them on real maps. Built with enhanced filtering, individual map generation, and comprehensive logging. It demonstrates how SSIDs can link to locations while emphasising privacy: all tests use only synthetic or self-produced data.

**Important:** All experiments and demonstrations use **synthetic/dummy datasets only**. No real third-party data is collected.

---

## Features
- **Enhanced SSID Filtering:** Advanced validation to filter out illogical, placeholder, or invalid SSIDs
- **Individual Map Generation:** Creates separate timestamped maps for each successful WiGLE API hit
- **Improved Naming Convention:** Maps named with format `WiFiGeoMap_{SSID}_{timestamp}.html`
- **Comprehensive Logging:** Detailed session logs tracking filtering, API queries, and map generation
- **Batch Processing:** Processes all valid SSIDs from capture data automatically
- **Data Validation:** Validates coordinates and filters suspicious location data
- **Summary Statistics:** Provides detailed success rates and processing summaries

### Core Functionality
- Capture Wi-Fi Probe Requests (via `tcpdump`)
- Extract SSID information from probe requests with advanced filtering
- Map SSIDs to locations using WiGLE API with caching
- Generate individual maps for each successful location query
- Create summary maps showing all discovered locations
- Comprehensive session logging and data validation

---

## Tech Stack
- **Language:** Python 3
- **Capture:** `tcpdump`, or PCAP file imports
- **Libraries:** 
  - `folium` for interactive map generation
  - `requests` for WiGLE API calls
  - `json` for caching and logging
  - `datetime` for timestamping
  - `pathlib` for file management
- **Mapping:** Folium with OpenStreetMap tiles

---

## Ethics

- No real user/device data is collected.
- Synthetic captures are generated via controlled tests (e.g., connecting personal devices to fake SSIDs).
- The prototype can technically capture real data, but this feature is not used in this project.

---

## Timeline

- Literature review & background research
- Tool design (CaptureManager, SSIDExtractor, GeoMapper, MapGUI)
- Implementation (synthetic data only)
- Evaluation & ethics review
- Final demo + report

---

## Author

Taran Chana
BSc Computer Science, Aston University
