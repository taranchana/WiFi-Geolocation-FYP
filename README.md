# WiFi-Geolocation-FYP
WiFi Geo Mapping is a Python proof-of-concept that captures Wi-Fi Probe Requests, extracts SSIDs, and visualises them on real maps. Built with enhanced filtering, individual map generation, and comprehensive logging. It demonstrates how SSIDs can link to locations while emphasising privacy: all tests use only synthetic or self-produced data.

**Important:** All experiments and demonstrations use **synthetic/dummy datasets only**. No real third-party data is collected.

This is an educational research prototype demonstrating Wi-Fi SSID geolocation as a privacy-awareness tool. It uses only synthetic and self-generated data. 

**Important:** Do not use this code to monitor third-party devices or networks without explicit consent. Doing so may violate UK GDPR and equivalent regulations.

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
- Capture Wi-Fi Probe Requests (via `tshark`)
- Extract SSID information from probe requests with advanced filtering
- Map SSIDs to locations using WiGLE API with caching
- Generate individual maps for each successful location query
- Create summary maps showing all discovered locations
- Comprehensive session logging and data validation

---

## Prerequisites
- Python 3.9+
- [`tshark`](https://www.wireshark.org/docs/man-pages/tshark.html) (part of Wireshark) — required if capturing live probe requests
- A [WiGLE](https://wigle.net/) account with API credentials

---

## WiGLE API Key Setup
This project uses the [WiGLE network search API](https://api.wigle.net/) to resolve SSID locations. You will need a free account at [wigle.net](https://wigle.net/) to obtain credentials.

Once logged in, find your credentials under **My Account → API Token**. You need both your **API Name** and **API Token**.

### Setting up your environment variable
Create a `.env` file in the project root:
```
WIGLE_API_NAME=your_api_name_here
WIGLE_API_TOKEN=your_api_token_here
```

The project loads these automatically via `python-dotenv`. If either variable is missing, the app falls back to **mock mode** — it skips all WiGLE queries but still runs the rest of the pipeline, which is useful for testing.

> **Important:** Never commit your `.env` file. Add it to `.gitignore`:
> ```
> echo ".env" >> .gitignore
> ```

---

## Installation
```bash
# Clone the repository
git clone https://github.com/taranchana/WiFi-Geolocation-FYP
cd WiFi-Geolocation-FYP

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file with WiGLE credentials (see above)
```

---

## Running the Project
```bash
python main.py
```
This will load `data/wifi-ssid-captures.txt`, extract and filter SSIDs, query WiGLE for each one (with an 8-second delay between calls to respect rate limits), generate maps, and open the summary map in your browser.

### Optional: Upload server
If you want to push a capture file from a remote device (e.g. a Raspberry Pi running `tshark`), start the Flask upload server:
```bash
python upload_server.py
```
Then POST a file to it from your capture device:
```bash
curl -X POST -F "file=@your_capture.txt" http://<server-ip>:5000/upload
```

---

## Capture Data Format
The input file (`data/wifi-ssid-captures.txt`) should have one entry per line with SSIDs in the format:
```
SSID="NetworkName"
```
To generate this with `tshark` (requires a wireless adapter in monitor mode):
```bash
tshark -i <interface> -Y "wlan.fc.type_subtype == 0x04" -T fields -e wlan_mgt.ssid > data/wifi-ssid-captures.txt
```

---

## Tech Stack
- **Language:** Python 3
- **Capture:** `tshark`
- **Libraries:**
  - `folium` for interactive map generation
  - `requests` for WiGLE API calls
  - `python-dotenv` for loading API credentials from `.env`
  - `json` for caching and logging
  - `datetime` for timestamping
  - `pathlib` for file management
- **Mapping:** Folium with OpenStreetMap tiles

---

## Output
- **Individual maps** → `data/maps/WiFiGeoMap_{SSID}_{timestamp}.html`
- **Summary map** → `data/maps/Full Map/WiFiGeoMap_all_locations.html`
- **WiGLE cache** → `data/wigle_cache.json` (avoids re-querying known SSIDs)
- **Session logs** → `data/logs/processing_log_{timestamp}.json`

---

## Ethics

- No real user/device data is collected.
- Synthetic captures are generated via controlled tests (e.g., connecting personal devices to fake SSIDs).
- The prototype can technically capture real data, but this feature is not used in this project.

---

## Author

Taran Chana
BSc Computer Science, Aston University
