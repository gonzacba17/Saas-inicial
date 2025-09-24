#!/usr/bin/env python3
"""
Script to create admin user for local development.
Run this after setting up the database.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.db.db import get_db, create_tables, User, UserRole, UserCRUD
from app.services import get_password_hash, get_user_by_email
from app.core.config import settings

def create_admin_user():
    """Create admin user if it doesn't exist."""
    
    # Create database tables first
    print("Creating database tables...")
    create_tables()
    print("✅ Database tables created successfully")
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Check if admin user already exists
        admin_email = "admin@saas.test"
        existing_admin = get_user_by_email(db, admin_email)
        
        if existing_admin:
            print(f"⚠️  Admin user already exists: {admin_email}")
            print(f"   User ID: {existing_admin.id}")
            print(f"   Username: {existing_admin.username}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Active: {existing_admin.is_active}")
            print(f"   Superuser: {existing_admin.is_superuser}")
            return existing_admin
        
        # Create admin user
        print(f"Creating admin user: {admin_email}")
        
        admin_data = {
            "email": admin_email,
            "username": "admin",
            "hashed_password": get_password_hash("Admin1234!"),
            "role": UserRole.admin,
            "is_active": True,
            "is_superuser": True
        }
        
        admin_user = UserCRUD.create(db, admin_data)
        
        print("✅ Admin user created successfully!")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   👤 Username: {admin_user.username}")
        print(f"   🔑 Password: Admin1234!")
        print(f"   🏷️  Role: {admin_user.role}")
        print(f"   🆔 User ID: {admin_user.id}")
        print(f"   ✅ Active: {admin_user.is_active}")
        print(f"   🔐 Superuser: {admin_user.is_superuser}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Setting up SaaS Cafeterías - Local Development")
    print("=" * 50)
    print(f"Database URL: {settings.db_url}")
    print(f"Environment: {settings.environment}")
    print("=" * 50)
    
    try:
        admin_user = create_admin_user()
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the backend server:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
        print("2. Access the API documentation:")
        print("   http://localhost:8000/docs")
        print("3. Login with admin credentials:")
        print("   Email: admin@saas.test")
        print("   Password: Admin1234!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)