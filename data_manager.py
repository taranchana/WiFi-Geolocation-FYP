#!/usr/bin/env python3
"""
WiFi Geolocation Data Manager
Utility script to manage and view generated maps, logs, and cache data.
"""

import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path

class DataManager:
    def __init__(self, project_root="data"):
        self.project_root = Path(project_root)
        self.maps_dir = self.project_root / "maps"
        self.logs_dir = self.project_root / "logs"
        self.cache_file = self.project_root / "wigle_cache.json"
        
    def list_maps(self):
        """List all generated maps."""
        if not self.maps_dir.exists():
            print("No maps directory found.")
            return []
            
        maps = list(self.maps_dir.glob("*.html"))
        maps.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"\nGenerated Maps ({len(maps)} total):")
        print("-" * 60)
        
        for i, map_file in enumerate(maps, 1):
            stat = map_file.stat()
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size_kb = stat.st_size / 1024
            print(f"{i:2d}. {map_file.name}")
            print(f"    Modified: {modified}, Size: {size_kb:.1f} KB")
            
        return maps
    
    def list_logs(self):
        """List all session logs."""
        if not self.logs_dir.exists():
            print("No logs directory found.")
            return []
            
        logs = list(self.logs_dir.glob("*.json"))
        logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"\nSession Logs ({len(logs)} total):")
        print("-" * 60)
        
        for i, log_file in enumerate(logs, 1):
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                
                session_id = log_data.get("session_id", "Unknown")
                successful = len(log_data.get("successful_locations", []))
                total_queries = len(log_data.get("api_queries", []))
                
                print(f"{i:2d}. {log_file.name}")
                print(f"    Session: {session_id}, Success: {successful}/{total_queries}")
                
            except Exception as e:
                print(f"{i:2d}. {log_file.name} (Error reading: {e})")
                
        return logs
    
    def show_cache_stats(self):
        """Show cache statistics."""
        if not self.cache_file.exists():
            print("No cache file found.")
            return
            
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            print(f"\nCache Statistics:")
            print("-" * 30)
            print(f"Total cached SSIDs: {len(cache)}")
            print("\nCached SSIDs:")
            for ssid, data in cache.items():
                lat, lon = data.get("lat", "?"), data.get("lon", "?")
                print(f"  • {ssid}: ({lat}, {lon})")
                
        except Exception as e:
            print(f"Error reading cache: {e}")
    
    def open_map(self, index=None):
        """Open a map in the browser."""
        maps = self.list_maps()
        if not maps:
            print("No maps to open.")
            return
            
        if index is None:
            index = 1  # Open most recent
        elif index < 1 or index > len(maps):
            print(f"Invalid index. Choose 1-{len(maps)}")
            return
            
        map_file = maps[index - 1]
        print(f"\nOpening: {map_file.name}")
        webbrowser.open(map_file.resolve().as_uri())
    
    def open_latest_summary(self):
        """Open the latest summary map."""
        # Check multiple possible locations for summary maps
        summary_maps = []
        
        # Check new location: data/maps/Full Map/
        full_map_dir = self.maps_dir / "Full Map"
        summary_maps.extend(list(full_map_dir.glob("*all_locations*.html")))
        
        # Check maps directory
        summary_maps.extend(list(self.maps_dir.glob("*all_locations*.html")))
        summary_maps.extend(list(self.maps_dir.glob("*Summary*.html")))
        
        # Check parent data directory (where main script used to save summary maps)
        data_dir = self.project_root
        summary_maps.extend(list(data_dir.glob("*all_locations*.html")))
        summary_maps.extend(list(data_dir.glob("*Summary*.html")))
            
        if not summary_maps:
            print("No summary maps found.")
            return
            
        latest = max(summary_maps, key=lambda x: x.stat().st_mtime)
        print(f"\nOpening latest summary map: {latest.name}")
        webbrowser.open(latest.resolve().as_uri())
    
    def view_log(self, index=None):
        """View a session log."""
        logs = self.list_logs()
        if not logs:
            print("No logs to view.")
            return
            
        if index is None:
            index = 1  # View most recent
        elif index < 1 or index > len(logs):
            print(f"Invalid index. Choose 1-{len(logs)}")
            return
            
        log_file = logs[index - 1]
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            
            print(f"\nSession Log: {log_file.name}")
            print("=" * 50)
            print(f"Session ID: {log_data.get('session_id', 'Unknown')}")
            print(f"Start Time: {log_data.get('start_time', 'Unknown')}")
            print(f"End Time: {log_data.get('end_time', 'Unknown')}")
            
            print(f"\nSSID Processing:")
            print(f"  Total extracted: {log_data.get('total_ssids_extracted', 0)}")
            print(f"  Valid SSIDs: {len(log_data.get('valid_ssids', []))}")
            
            filter_reasons = log_data.get('filtered_ssids', {})
            if filter_reasons:
                print("  Filtering reasons:")
                for reason, count in filter_reasons.items():
                    print(f"    - {reason}: {count}")
            
            api_queries = log_data.get('api_queries', [])
            successful = [q for q in api_queries if q.get('success')]
            failed = [q for q in api_queries if not q.get('success')]
            
            print(f"\nAPI Queries:")
            print(f"  Total: {len(api_queries)}")
            print(f"  Successful: {len(successful)}")
            print(f"  Failed: {len(failed)}")
            
            if successful:
                print("\n  Successful locations:")
                for query in successful[:5]:  # Show first 5
                    loc = query.get('location', {})
                    ssid = query.get('ssid', 'Unknown')
                    lat, lon = loc.get('lat', '?'), loc.get('lon', '?')
                    print(f"    • {ssid}: ({lat}, {lon})")
                if len(successful) > 5:
                    print(f"    ... and {len(successful) - 5} more")
                    
        except Exception as e:
            print(f"Error reading log: {e}")
    
    def cleanup_old_files(self, days_old=7):
        """Remove maps and logs older than specified days."""
        from time import time
        cutoff = time() - (days_old * 24 * 60 * 60)
        
        removed_count = 0
        
        # Clean old maps
        for map_file in self.maps_dir.glob("*.html"):
            if map_file.stat().st_mtime < cutoff:
                map_file.unlink()
                removed_count += 1
                print(f"Removed old map: {map_file.name}")
                
        # Clean old logs
        for log_file in self.logs_dir.glob("*.json"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                removed_count += 1
                print(f"Removed old log: {log_file.name}")
        
        print(f"\nCleaned up {removed_count} old files (older than {days_old} days)")


def main():
    """Interactive data manager."""
    manager = DataManager()
    
    while True:
        print("\n" + "=" * 50)
        print("WiFi Geolocation Data Manager")
        print("=" * 50)
        print("1. List maps")
        print("2. List logs")
        print("3. Show cache stats")
        print("4. Open map by index")
        print("5. Open latest summary map")
        print("6. View log by index")
        print("7. Cleanup old files")
        print("8. Quick overview")
        print("9. Exit")
        
        try:
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                manager.list_maps()
            elif choice == "2":
                manager.list_logs()
            elif choice == "3":
                manager.show_cache_stats()
            elif choice == "4":
                maps = manager.list_maps()
                if maps:
                    try:
                        idx = int(input(f"Enter map index (1-{len(maps)}): "))
                        manager.open_map(idx)
                    except ValueError:
                        print("Invalid index.")
            elif choice == "5":
                manager.open_latest_summary()
            elif choice == "6":
                logs = manager.list_logs()
                if logs:
                    try:
                        idx = int(input(f"Enter log index (1-{len(logs)}): "))
                        manager.view_log(idx)
                    except ValueError:
                        print("Invalid index.")
            elif choice == "7":
                try:
                    days = int(input("Remove files older than how many days? (default 7): ") or "7")
                    manager.cleanup_old_files(days)
                except ValueError:
                    print("Invalid number of days.")
            elif choice == "8":
                print("\nQuick Overview:")
                manager.list_maps()
                manager.list_logs()
                manager.show_cache_stats()
            elif choice == "9":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-9.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()