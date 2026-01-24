"""
Database initialization script
Run this to create all tables in the database
"""
import os
os.environ['STREAMLIT_RUNTIME_EXISTS'] = 'false'

from database.db import init_db

if __name__ == "__main__":
    print("Initializing database tables...")
    try:
        init_db()
        print("[SUCCESS] Database tables created successfully!")
        print("[SUCCESS] Your Supabase database is ready to use!")
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        raise
