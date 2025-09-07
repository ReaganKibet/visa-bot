# test_system.py - Final fixed version
import requests
import time
import json

def test_system():
    print("🧪 Testing VFS Visa Bot System")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # ✅ Test API health
        print("🔍 Testing API connection...")
        response = requests.get(f"{base_url}/status/")
        if response.status_code == 200:
            print("✅ API is healthy")
            print(f"   Response: {response.json()['status']}")
        else:
            print(f"❌ API unhealthy: {response.status_code}")
            return
        
        # ✅ Get current monitors
        print("\n📊 Testing Monitor Management")
        print("-" * 30)
        
        response = requests.get(f"{base_url}/monitors/")
        if response.status_code == 200:
            monitors = response.json()
            print(f"✅ Found {len(monitors)} monitors")
            
            # Show active monitors
            active_monitors = [m for m in monitors if m['status'] == 'active']
            stopped_monitors = [m for m in monitors if m['status'] == 'stopped']
            
            print(f"   - Active: {len(active_monitors)}")
            print(f"   - Stopped: {len(stopped_monitors)}")
            
            # Show last 3 monitors
            for monitor in monitors[-3:] if monitors else []:
                print(f"   - ID: {monitor['id']}, Status: {monitor['status']}, Flow: {monitor['flow']}")
        
        # ✅ Test monitor status endpoint
        print("\n🔍 Testing Monitor Status...")
        response = requests.get(f"{base_url}/monitors/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Monitor Status:")
            print(f"   - Active Monitor ID: {status['active_monitor']['id']}")
            print(f"   - WebSocket Connections: {status['websocket_connections']}")
        
        # ✅ Create new monitor with correct schema
        print("\n🚀 Testing Monitor Creation...")
        monitor_data = {
            "flow": "mozambique-to-portugal",
            "applicant_id": f"test_user_{int(time.time())}",  # ✅ Unique applicant_id
            "config": {"check_interval": 60}
        }
        
        response = requests.post(f"{base_url}/monitors/", json=monitor_data)
        if response.status_code == 200:
            monitor = response.json()
            print(f"✅ Monitor created successfully!")
            print(f"   - ID: {monitor['id']}")
            print(f"   - Run ID: {monitor['run_id']}")
            print(f"   - Status: {monitor['status']}")
            print(f"   - Applicant: {monitor['applicant_id']}")
            
            # ✅ Test booking creation with correct schema
            print("\n📋 Testing Booking Creation...")
            booking_data = {
                "applicant_id": monitor['applicant_id'],  # ✅ Use same applicant_id
                "run_id": monitor['run_id'],  # ✅ Use correct run_id
                "form_data": {"name": "Test User", "email": "test@example.com"}
            }
            
            response = requests.post(f"{base_url}/bookings/", json=booking_data)
            if response.status_code == 200:
                booking = response.json()
                print(f"✅ Booking created successfully!")
                print(f"   - ID: {booking['id']}")
                print(f"   - Status: {booking['status']}")
                print(f"   - Applicant: {booking['applicant_id']}")
            else:
                print(f"❌ Booking creation failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
            
            # ✅ Wait a moment for monitor to start
            print("\n⏳ Waiting 5 seconds for monitor to start...")
            time.sleep(5)
            
            # ✅ Test webhook endpoint
            print("\n🔗 Testing Webhook...")
            webhook_data = {
                "event": "test_event",
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "🧪 Test webhook message from system test"
            }
            
            response = requests.post(f"{base_url}/webhooks/monitor-event", json=webhook_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Webhook working!")
                print(f"   - Status: {result['status']}")
                print(f"   - Active Connections: {result['connections']}")
            else:
                print(f"❌ Webhook failed: {response.status_code}")
            
            # ✅ Stop the monitor
            print(f"\n🛑 Stopping Monitor {monitor['id']}...")
            response = requests.post(f"{base_url}/monitors/{monitor['id']}/stop")
            if response.status_code == 200:
                print(f"✅ Monitor stopped successfully")
            else:
                print(f"❌ Failed to stop monitor: {response.status_code}")
                
        else:
            print(f"❌ Monitor creation failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Response: {response.text}")
        
        print(f"\n🎉 System test completed!")
        print(f"\n📝 Next Steps:")
        print(f"   1. Open dashboard: http://localhost:3000")
        print(f"   2. Check API docs: http://localhost:8000/docs")
        print(f"   3. Monitor logs: docker-compose logs -f")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the system is running.")
        print("   Try: docker-compose up -d")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system()