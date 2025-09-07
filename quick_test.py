#!/usr/bin/env python3
"""
Quick test to verify the system is working
"""

import requests
import time

def test_system():
    print("🧪 Quick System Test")
    print("=" * 30)
    
    # Test 1: Create a monitor
    print("1. Creating monitor...")
    try:
        response = requests.post("http://localhost:8000/monitors/", json={
            "flow": "mozambique-to-portugal"
        })
        if response.status_code == 200:
            monitor = response.json()
            print(f"✅ Monitor created: ID {monitor['id']}")
            monitor_id = monitor['id']
        else:
            print(f"❌ Monitor creation failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Create a booking
    print("2. Creating booking...")
    try:
        response = requests.post("http://localhost:8000/bookings/", json={
            "applicant_id": "TEST-001",
            "run_id": f"run_{monitor_id}"
        })
        if response.status_code == 200:
            booking = response.json()
            print(f"✅ Booking created: ID {booking['id']}")
        else:
            print(f"❌ Booking creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Test completed!")
    print("Check the dashboard at http://localhost:3000")
    print("You should see logs appearing in real-time!")

if __name__ == "__main__":
    test_system()
