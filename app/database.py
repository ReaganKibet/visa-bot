# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Load environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vfsuser:vfspass@db/vfsbot")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create Base class for models
Base = declarative_base()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Optional: create tables (for dev only)
def init_db():
    Base.metadata.create_all(bind=engine)