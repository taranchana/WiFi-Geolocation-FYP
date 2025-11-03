# WiFi-Geolocation-FYP
WiFi Geo Mapping is a Python proof-of-concept that captures Wi-Fi Probe Requests, extracts SSIDs, and visualises them on real maps. Built with tcpdump and modular design, it demonstrates how SSIDs can link to locations while emphasising privacy: all tests use only synthetic or self-produced data.

**Important:** All experiments and demonstrations use **synthetic/dummy datasets only**. No real third-party data is collected.

---

## Features
- Capture Wi-Fi Probe Requests (via `tcpdump`).
- Extract SSID information from probe requests.
- Map SSIDs to locations using a geolocation API or mock dataset.
- Visualise results on an **interactive map**.
- Ethical-by-design: prototype capable of live capture but **restricted to synthetic/self-produced data only**.

---

## Tech Stack
- **Language:** Python 3
- **Capture:** `tcpdump`, or PCAP file imports
- **Libraries:** Scapy / pyshark for packet parsing, requests for API calls, Tkinter/PyQt or Flask for GUI
- **Mapping:** OpenStreetMap, Leaflet.js, or Google Maps embed

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
