"""
Database migration script to add booking_type column to resources table.
Run this script to add the booking_type column to your database.

Usage:
    python migrate_add_booking_type.py
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config


def migrate_database():
    """Add booking_type column to resources table."""
    # Get database URI from config
    database_uri = Config.SQLALCHEMY_DATABASE_URI
    
    # Handle SQLite path - if it's relative, make it absolute
    if database_uri.startswith('sqlite:///'):
        db_path = database_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            # Check if it's in instance/ directory
            instance_path = os.path.join(os.path.dirname(__file__), 'instance', db_path)
            if os.path.exists(instance_path):
                database_uri = f'sqlite:///{os.path.abspath(instance_path)}'
            else:
                database_uri = f'sqlite:///{os.path.abspath(db_path)}'
    
    print(f"Connecting to database: {database_uri}")
    
    # Create engine and session
    engine = create_engine(database_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if column already exists
        if 'sqlite' in database_uri.lower():
            # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
            # Check if column exists first
            result = session.execute(text("PRAGMA table_info(resources)"))
            columns = [row[1] for row in result]
            
            if 'booking_type' in columns:
                print("[INFO] Column 'booking_type' already exists. No migration needed.")
                return
            
            # Add column for SQLite
            print("Adding booking_type column to resources table (SQLite)...")
            session.execute(text("ALTER TABLE resources ADD COLUMN booking_type VARCHAR DEFAULT 'open'"))
            session.commit()
            print("[SUCCESS] Successfully added booking_type column")
            
        else:
            # PostgreSQL or other databases
            print("Adding booking_type column to resources table (PostgreSQL)...")
            session.execute(text("ALTER TABLE resources ADD COLUMN IF NOT EXISTS booking_type VARCHAR DEFAULT 'open'"))
            session.commit()
            print("[SUCCESS] Successfully added booking_type column")
        
        # Update existing resources to have 'open' as default
        print("Updating existing resources to have booking_type='open'...")
        session.execute(text("UPDATE resources SET booking_type = 'open' WHERE booking_type IS NULL"))
        session.commit()
        print("[SUCCESS] Successfully updated existing resources")
        
        print("\n[SUCCESS] Migration completed successfully!")
        print("You can now restart your application.")
        
    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Error during migration: {e}")
        print("Please check your database connection and try again.")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add booking_type column")
    print("=" * 60)
    print()
    migrate_database()

