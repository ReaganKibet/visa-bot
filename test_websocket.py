#!/usr/bin/env python3
"""
Test WebSocket connection to verify logs are being sent
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/monitor-updates"
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket!")
            print("📡 Listening for messages...")
            print("(Start monitoring from the frontend to see logs)")
            print("-" * 50)
            
            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                timestamp = data.get('timestamp', 'N/A')
                event = data.get('event', 'unknown')
                msg = data.get('message', 'No message')
                
                print(f"[{timestamp}] {event}: {msg}")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("Make sure the API is running: docker-compose up")

if __name__ == "__main__":
    asyncio.run(test_websocket())
