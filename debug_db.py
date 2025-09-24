#!/usr/bin/env python3
"""
Debug script para verificar qué database está usando la aplicación
"""
import os
import sys
sys.path.insert(0, 'backend')

# Set environment variables
os.environ['USE_SQLITE'] = 'true'
os.environ['PYTHONPATH'] = 'backend'

from app.core.config import settings

print(f"USE_SQLITE: {os.getenv('USE_SQLITE')}")
print(f"Database URL: {settings.db_url}")
print(f"Sqlite file: {settings.sqlite_file}")

# Test database connection
from app.db.db import SessionLocal
from sqlalchemy import text

def test_db_connection():
    try:
        db = SessionLocal()
        # Try to execute a simple query
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables found: {tables}")
        db.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    success = test_db_connection()
    if success:
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")