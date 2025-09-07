# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class MonitorCreate(BaseModel):
    flow: str
    applicant_id: Optional[str] = None  # ✅ Make optional with default
    config: Optional[Dict[str, Any]] = None  # ✅ Added config field

class Monitor(BaseModel):
    id: int
    flow: str
    applicant_id: Optional[str] = None  # ✅ Added missing field
    run_id: str
    status: str
    config: Optional[str] = None  # ✅ Added config field
    created_at: datetime

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    applicant_id: str
    run_id: str
    form_data: Optional[Dict[str, Any]] = None  # ✅ Added form_data

class Booking(BaseModel):
    id: int
    applicant_id: str
    run_id: str
    status: str
    form_data: Optional[str] = None  # ✅ Added form_data
    pdf_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True