#!/usr/bin/env python3
"""
Script para actualizar el email del usuario admin existente
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.db.db import get_db, create_tables, User, UserRole, UserCRUD
from app.services import get_user_by_email, get_user_by_username

def fix_admin_email():
    """Update admin user email if it exists."""
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Check if admin user with old email exists
        old_admin = get_user_by_email(db, "admin@saas.test")
        if old_admin:
            print(f"Found old admin with email: {old_admin.email}")
            # Update email
            old_admin.email = "admin@example.com"
            db.commit()
            db.refresh(old_admin)
            print(f"✅ Admin email updated to: {old_admin.email}")
            return old_admin
        
        # Check by username
        admin_by_username = get_user_by_username(db, "admin")
        if admin_by_username:
            print(f"Found admin by username with email: {admin_by_username.email}")
            if admin_by_username.email == "admin@saas.test":
                admin_by_username.email = "admin@example.com"
                db.commit()
                db.refresh(admin_by_username)
                print(f"✅ Admin email updated to: {admin_by_username.email}")
            return admin_by_username
        
        print("No admin user found to update")
        return None
        
    except Exception as e:
        print(f"❌ Error updating admin email: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Fixing admin email...")
    try:
        admin_user = fix_admin_email()
        if admin_user:
            print("\n✅ Admin user fixed successfully!")
            print(f"   📧 Email: {admin_user.email}")
            print(f"   👤 Username: {admin_user.username}")
            print(f"   🏷️  Role: {admin_user.role}")
            print(f"   🆔 User ID: {admin_user.id}")
        print("\n📝 You can now login with:")
        print("   Email: admin@example.com")
        print("   Username: admin")
        print("   Password: Admin1234!")
        
    except Exception as e:
        print(f"\n❌ Fix failed: {e}")
        sys.exit(1)