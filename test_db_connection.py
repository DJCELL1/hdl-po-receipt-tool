"""
Quick test to check database connection
"""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

db_url = os.getenv('DATABASE_URL')
print(f"\nDATABASE_URL from .env: {db_url[:50]}..." if db_url else "DATABASE_URL: NOT FOUND")

# Now import config to see what it gets
import config
print(f"\nDATABASE_URL from config: {config.DATABASE_URL[:50]}..." if config.DATABASE_URL else "DATABASE_URL: NOT FOUND")

# Try to connect
try:
    from sqlalchemy import text
    from database.db import engine
    print(f"\nEngine URL: {str(engine.url)[:50]}...")

    # Test connection
    with engine.connect() as conn:
        print("\n✓ Successfully connected to database!")
        result = conn.execute(text("SELECT current_database(), current_user"))
        db_name, db_user = result.fetchone()
        print(f"  Database: {db_name}")
        print(f"  User: {db_user}")
except Exception as e:
    print(f"\n✗ Connection failed: {e}")

print("=" * 60)
