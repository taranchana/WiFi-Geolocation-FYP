import json
import os
from datetime import datetime
from pathlib import Path

class DataValidator:
    """
    Handles data validation, logging, and processing statistics for WiFi geolocation data.
    """
    
    def __init__(self, log_dir="data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"processing_log_{self.session_id}.json"
        
        self.processing_stats = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "total_lines_read": 0,
            "total_ssids_extracted": 0,
            "valid_ssids": [],
            "filtered_ssids": {},
            "api_queries": [],
            "successful_locations": [],
            "failed_lookups": [],
            "maps_generated": [],
            "end_time": None
        }

    def log_extraction_results(self, extractor, total_lines, valid_ssids):
        """Log SSID extraction results."""
        self.processing_stats["total_lines_read"] = total_lines
        self.processing_stats["total_ssids_extracted"] = len(valid_ssids)
        self.processing_stats["valid_ssids"] = valid_ssids
        self.processing_stats["filtered_ssids"] = dict(extractor.filter_reasons)
        
        print(f"[DataValidator] Logged extraction of {len(valid_ssids)} valid SSIDs")

    def log_api_query(self, ssid, success, location_data=None, error=None):
        """Log individual API query results."""
        query_result = {
            "ssid": ssid,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        if success and location_data:
            query_result["location"] = location_data
            self.processing_stats["successful_locations"].append(location_data)
        elif error:
            query_result["error"] = error
            self.processing_stats["failed_lookups"].append({
                "ssid": ssid,
                "error": error,
                "timestamp": query_result["timestamp"]
            })
        
        self.processing_stats["api_queries"].append(query_result)

    def log_map_generation(self, map_path, map_type="individual", ssid=None):
        """Log map generation."""
        map_entry = {
            "path": str(map_path),
            "type": map_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if ssid:
            map_entry["ssid"] = ssid
            
        self.processing_stats["maps_generated"].append(map_entry)
        print(f"[DataValidator] Logged {map_type} map generation: {map_path}")

    def validate_coordinates(self, lat, lon):
        """Validate coordinate data for reasonableness."""
        try:
            lat, lon = float(lat), float(lon)
            
            # Basic coordinate validation
            if not (-90 <= lat <= 90):
                return False, f"Invalid latitude: {lat}"
            if not (-180 <= lon <= 180):
                return False, f"Invalid longitude: {lon}"
                
            # Check for obviously invalid coordinates (0,0 is suspicious)
            if lat == 0 and lon == 0:
                return False, "Suspicious coordinates (0,0)"
                
            return True, "Valid coordinates"
            
        except (ValueError, TypeError):
            return False, "Non-numeric coordinates"

    def get_processing_summary(self):
        """Get a summary of processing results."""
        total_queries = len(self.processing_stats["api_queries"])
        successful_queries = len(self.processing_stats["successful_locations"])
        failed_queries = len(self.processing_stats["failed_lookups"])
        
        summary = {
            "session_id": self.session_id,
            "ssids": {
                "total_extracted": self.processing_stats["total_ssids_extracted"],
                "valid_after_filtering": len(self.processing_stats["valid_ssids"]),
                "filter_reasons": self.processing_stats["filtered_ssids"]
            },
            "api_queries": {
                "total": total_queries,
                "successful": successful_queries,
                "failed": failed_queries,
                "success_rate": f"{(successful_queries/total_queries*100):.1f}%" if total_queries > 0 else "0%"
            },
            "maps": {
                "total_generated": len(self.processing_stats["maps_generated"]),
                "individual_maps": len([m for m in self.processing_stats["maps_generated"] if m["type"] == "individual"]),
                "summary_maps": len([m for m in self.processing_stats["maps_generated"] if m["type"] == "summary"])
            }
        }
        
        return summary

    def save_session_log(self):
        """Save the complete processing session to a log file."""
        self.processing_stats["end_time"] = datetime.now().isoformat()
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.processing_stats, f, indent=2, ensure_ascii=False)
            
            print(f"[DataValidator] Session log saved to: {self.log_file}")
            return str(self.log_file)
            
        except Exception as e:
            print(f"[DataValidator] Error saving session log: {e}")
            return None

    def print_session_summary(self):
        """Print a human-readable session summary."""
        summary = self.get_processing_summary()
        
        print("\n" + "="*60)
        print("WiFi GEOLOCATION PROCESSING SUMMARY")
        print("="*60)
        print(f"Session ID: {summary['session_id']}")
        print()
        print("SSID Extraction:")
        print(f"  • Total SSIDs extracted: {summary['ssids']['total_extracted']}")
        print(f"  • Valid after filtering: {summary['ssids']['valid_after_filtering']}")
        if summary['ssids']['filter_reasons']:
            print("  • Filter reasons:")
            for reason, count in summary['ssids']['filter_reasons'].items():
                print(f"    - {reason}: {count}")
        print()
        print("API Queries:")
        print(f"  • Total queries: {summary['api_queries']['total']}")
        print(f"  • Successful: {summary['api_queries']['successful']}")
        print(f"  • Failed: {summary['api_queries']['failed']}")
        print(f"  • Success rate: {summary['api_queries']['success_rate']}")
        print()
        print("Map Generation:")
        print(f"  • Total maps generated: {summary['maps']['total_generated']}")
        print(f"  • Individual maps: {summary['maps']['individual_maps']}")
        print(f"  • Summary maps: {summary['maps']['summary_maps']}")
        print("="*60)