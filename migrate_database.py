# migrate_database.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import Base

def migrate_database():
    """Add missing columns to existing tables"""
    print("🔄 Starting database migration...")
    
    with engine.connect() as conn:
        try:
            # ✅ Add missing columns to monitors table
            print("📝 Adding missing columns to monitors table...")
            
            # Check if applicant_id column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='monitors' AND column_name='applicant_id';
            """))
            
            if not result.fetchone():
                conn.execute(text("ALTER TABLE monitors ADD COLUMN applicant_id VARCHAR;"))
                print("✅ Added applicant_id column")
            
            # Check if config column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='monitors' AND column_name='config';
            """))
            
            if not result.fetchone():
                conn.execute(text("ALTER TABLE monitors ADD COLUMN config TEXT;"))
                print("✅ Added config column")
            
            # ✅ Add missing columns to bookings table
            print("📝 Adding missing columns to bookings table...")
            
            # Check if form_data column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='bookings' AND column_name='form_data';
            """))
            
            if not result.fetchone():
                conn.execute(text("ALTER TABLE bookings ADD COLUMN form_data TEXT;"))
                print("✅ Added form_data column")
            
            conn.commit()
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

def recreate_tables():
    """Drop and recreate all tables (WARNING: This will delete all data!)"""
    print("⚠️  RECREATING ALL TABLES - THIS WILL DELETE ALL DATA!")
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Dropped all existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Created all tables with new schema")
        
    except Exception as e:
        print(f"❌ Table recreation failed: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration script')
    parser.add_argument('--recreate', action='store_true', 
                       help='Recreate all tables (WARNING: Deletes all data)')
    
    args = parser.parse_args()
    
    if args.recreate:
        recreate_tables()
    else:
        migrate_database()