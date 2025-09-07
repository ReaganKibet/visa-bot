#!/usr/bin/env python3
"""
Cleanup script to stop all active monitors
"""

import requests
import json

API_BASE = "http://localhost:8000"

def get_all_monitors():
    """Get all monitors"""
    try:
        response = requests.get(f"{API_BASE}/monitors/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get monitors: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting monitors: {e}")
        return []

def stop_monitor(monitor_id):
    """Stop a specific monitor"""
    try:
        response = requests.post(f"{API_BASE}/monitors/{monitor_id}/stop")
        if response.status_code == 200:
            print(f"✅ Stopped monitor {monitor_id}")
            return True
        else:
            print(f"❌ Failed to stop monitor {monitor_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error stopping monitor {monitor_id}: {e}")
        return False

def main():
    print("🧹 Cleaning up active monitors...")
    print("=" * 40)
    
    # Get all monitors
    monitors = get_all_monitors()
    
    if not monitors:
        print("✅ No monitors found")
        return
    
    print(f"📊 Found {len(monitors)} monitors")
    
    # Stop all active monitors
    active_monitors = [m for m in monitors if m['status'] == 'active']
    
    if not active_monitors:
        print("✅ No active monitors to stop")
        return
    
    print(f"🛑 Stopping {len(active_monitors)} active monitors...")
    
    for monitor in active_monitors:
        stop_monitor(monitor['id'])
    
    print("\n✅ Cleanup completed!")
    print("Now you can start a fresh monitor from the dashboard.")

if __name__ == "__main__":
    main()
