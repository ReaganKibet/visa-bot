# app/main.py
import sys
import json
import uuid
import asyncio
from pathlib import Path
from typing import List
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Add project root
sys.path.append(str(Path(__file__).parent.parent))

# Import modules
from app import models, schemas
from app.database import init_db, engine, SessionLocal
from workers.tasks import start_monitor, trigger_booking

app = FastAPI(title="VFS Appointment Orchestrator")

# WebSocket connections
active_connections: List[WebSocket] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/status/")
def get_status():
    return {
        "status": "healthy",
        "service": "api",
        "timestamp": datetime.utcnow().isoformat()
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Broadcast helper function
async def broadcast_to_websockets(message: dict):
    """Broadcast message to all active WebSocket connections"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    
    # Remove disconnected connections
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)

@app.post("/monitors/", response_model=schemas.Monitor)
async def create_monitor(monitor: schemas.MonitorCreate, db: Session = Depends(get_db)):
    # ✅ Stop existing active monitors
    existing = db.query(models.Monitor).filter(
        models.Monitor.flow == monitor.flow,
        models.Monitor.status == "active"
    ).first()
    
    if existing:
        print(f"⚠️ Stopping existing active monitor ID: {existing.id}")
        existing.status = "stopped"
        db.commit()
    
    # ✅ Generate unique run_id and applicant_id
    run_id = f"run_{uuid.uuid4().hex[:16]}"
    applicant_id = monitor.applicant_id or f"user_{uuid.uuid4().hex[:8]}"
    
    # ✅ Convert config to JSON string
    config_str = json.dumps(monitor.config) if monitor.config else None
    
    db_monitor = models.Monitor(
        flow=monitor.flow,
        applicant_id=applicant_id,
        run_id=run_id,
        status="active",
        config=config_str
    )
    db.add(db_monitor)
    
    try:
        db.commit()
        db.refresh(db_monitor)
        
        # ✅ Start monitoring task
        start_monitor.delay(run_id)
        
        # ✅ Send notification to WebSocket clients (await since we're in async context)
        await broadcast_to_websockets({
            "event": "monitor_created",
            "monitor_id": db_monitor.id,
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"🚀 Monitor {db_monitor.id} started successfully"
        })
        
        return db_monitor
    except Exception as e:
        db.rollback()
        print(f"❌ Monitor creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create monitor: {str(e)}")

@app.post("/bookings/", response_model=schemas.Booking)
async def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    # ✅ Convert form_data to JSON string
    form_data_str = json.dumps(booking.form_data) if booking.form_data else None
    
    db_booking = models.Booking(
        applicant_id=booking.applicant_id,
        run_id=booking.run_id,
        status="queued",
        form_data=form_data_str
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # ✅ Trigger booking task with form data
    trigger_booking.delay(booking.applicant_id, booking.run_id, booking.form_data)
    
    # ✅ Send notification to WebSocket clients
    await broadcast_to_websockets({
        "event": "booking_started",
        "booking_id": db_booking.id,
        "applicant_id": booking.applicant_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"🚀 Booking session started for {booking.applicant_id}"
    })
    
    return db_booking

@app.get("/monitors/")
def get_monitors(db: Session = Depends(get_db)):
    monitors = db.query(models.Monitor).order_by(models.Monitor.created_at.desc()).all()
    return monitors

@app.post("/monitors/{monitor_id}/stop")
def stop_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.query(models.Monitor).filter(models.Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    monitor.status = "stopped"
    db.commit()
    return {"message": "Monitor stopped successfully", "monitor_id": monitor_id}

# ✅ Add endpoint to get real-time status
@app.get("/monitors/status")
def get_monitors_status(db: Session = Depends(get_db)):
    """Get current monitor status and connection info"""
    active_monitor = db.query(models.Monitor).filter(
        models.Monitor.status == "active"
    ).first()
    
    return {
        "active_monitor": {
            "id": active_monitor.id if active_monitor else None,
            "run_id": active_monitor.run_id if active_monitor else None,
            "applicant_id": active_monitor.applicant_id if active_monitor else None,
            "created_at": active_monitor.created_at.isoformat() if active_monitor else None
        },
        "websocket_connections": len(active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }

# ✅ Enhanced WebSocket endpoint
@app.websocket("/ws/monitor-updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"🔌 WebSocket connected. Total connections: {len(active_connections)}")
    
    # ✅ Send connection confirmation
    try:
        await websocket.send_json({
            "event": "connected",
            "message": "✅ WebSocket connected successfully",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # ✅ Keep connection alive
            data = await websocket.receive_text()
            
            # ✅ Handle ping messages
            if data == "ping":
                await websocket.send_json({"event": "pong"})
                
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"🔌 WebSocket removed. Total connections: {len(active_connections)}")

# ✅ Enhanced webhook endpoint
class MonitorEvent(BaseModel):
    event: str
    timestamp: str
    message: str

@app.post("/webhooks/monitor-event")
async def receive_monitor_event(event: MonitorEvent):
    """Receive monitoring events and broadcast to WebSocket clients"""
    print(f"📡 Webhook received: {event.event} - {event.message}")
    
    # ✅ Broadcast to all WebSocket connections
    await broadcast_to_websockets(event.dict())
    
    return {"status": "received", "connections": len(active_connections)}