"""
Database migration script for HDL PO Receipt Tool
Run this to set up or update the database schema
"""

import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql
import config

def run_migration():
    """Execute the SQL schema file"""
    schema_file = Path(__file__).parent / "schema.sql"

    if not schema_file.exists():
        print(f"Error: Schema file not found at {schema_file}")
        return False

    try:
        # Parse DATABASE_URL
        # Format: postgresql://user:password@host:port/dbname
        db_url = config.DATABASE_URL

        print(f"Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"Reading schema from {schema_file}")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        print("Executing schema...")
        cursor.execute(schema_sql)

        print("Migration completed successfully!")

        # Verify tables were created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\nCreated {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("HDL PO Receipt Tool - Database Migration")
    print("=" * 50)

    if not config.DATABASE_URL:
        print("Error: DATABASE_URL not set in environment")
        sys.exit(1)

    success = run_migration()
    sys.exit(0 if success else 1)
