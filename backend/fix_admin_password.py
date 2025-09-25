#!/usr/bin/env python3
"""
Script para corregir la contraseña del usuario admin.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.db import User, UserRole
from app.services import get_password_hash, verify_password

def fix_admin_password():
    """Fix admin password."""
    print("🔧 Fixing admin password...")
    
    # Create database connection
    engine = create_engine(settings.db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Find admin user
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Admin user found: {admin.email}")
        
        # Generate new password hash
        new_password = "Admin1234!"
        new_hash = get_password_hash(new_password)
        
        # Test that the new hash works
        if not verify_password(new_password, new_hash):
            print("❌ Password hash verification failed!")
            return False
        
        # Update admin password
        admin.hashed_password = new_hash
        db.commit()
        
        print(f"✅ Admin password updated successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password: {new_password}")
        
        # Verify the update worked
        db.refresh(admin)
        if verify_password(new_password, admin.hashed_password):
            print("✅ Password verification successful!")
            return True
        else:
            print("❌ Password verification failed after update!")
            return False

if __name__ == "__main__":
    success = fix_admin_password()
    sys.exit(0 if success else 1)