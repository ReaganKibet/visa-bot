# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.database import Base

class Monitor(Base):
    __tablename__ = "monitors"
    id = Column(Integer, primary_key=True, index=True)
    flow = Column(String, index=True)
    applicant_id = Column(String, index=True)  # ✅ Added missing field
    run_id = Column(String, unique=True)
    status = Column(String, default="active")
    config = Column(Text, nullable=True)  # ✅ Store JSON config as text
    created_at = Column(DateTime, default=func.now())

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(String, index=True)
    run_id = Column(String)
    status = Column(String, default="queued")
    form_data = Column(Text, nullable=True)  # ✅ Store form data as JSON
    pdf_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())