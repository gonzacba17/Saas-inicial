#!/usr/bin/env python3
"""
Script de debugging para verificar que el backend funciona correctamente
"""
import os
import sys
from pathlib import Path
import asyncio
import httpx

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from app.core.config import settings
        print(f"✅ Config loaded - Environment: {settings.environment}")
        print(f"✅ Database URL: {settings.db_url}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from app.db.db import User, UserRole, create_tables, get_db
        print("✅ Database models imported")
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    try:
        from app.schemas import UserCreate, User as UserSchema, Token
        print("✅ Schemas imported")
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        return False
    
    try:
        from app.services import get_password_hash, create_user, authenticate_user
        print("✅ Services imported")
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        return False
    
    try:
        from app.api.v1.auth import router
        print("✅ Auth router imported")
    except Exception as e:
        print(f"❌ Auth router import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database connection and operations"""
    print("\n🔍 Testing database...")
    
    try:
        from app.db.db import create_tables, get_db, UserCRUD
        from app.services import get_user_by_email
        
        # Create tables
        create_tables()
        print("✅ Database tables created/verified")
        
        # Test database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Check if admin user exists
        admin_user = get_user_by_email(db, "admin@saas.test")
        if admin_user:
            print(f"✅ Admin user exists: {admin_user.username} ({admin_user.email})")
            print(f"   Role: {admin_user.role}")
            print(f"   Active: {admin_user.is_active}")
        else:
            print("⚠️  Admin user not found")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API server: {e}")
            print("   Make sure the server is running with: python -m uvicorn app.main:app --reload")
            return False
        
        try:
            # Test OpenAPI docs
            response = await client.get(f"{base_url}/api/v1/openapi.json")
            if response.status_code == 200:
                print("✅ OpenAPI schema accessible")
            else:
                print(f"⚠️  OpenAPI schema issue: {response.status_code}")
        except Exception as e:
            print(f"⚠️  OpenAPI test failed: {e}")
        
        try:
            # Test login endpoint with admin credentials
            login_data = {
                "username": "admin",
                "password": "Admin1234!"
            }
            response = await client.post(f"{base_url}/api/v1/auth/login", data=login_data)
            if response.status_code == 200:
                result = response.json()
                print("✅ Login endpoint working")
                print(f"   Token type: {result.get('token_type')}")
                print(f"   User role: {result.get('role')}")
            else:
                print(f"❌ Login endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    return True

def test_cors_config():
    """Test CORS configuration"""
    print("\n🔍 Testing CORS configuration...")
    
    try:
        from app.middleware.security import setup_cors
        from app.core.config import settings
        print("✅ CORS middleware imported")
        
        # Check allowed origins
        if hasattr(settings, 'allowed_origins_list'):
            origins = settings.allowed_origins_list
            print(f"✅ Allowed origins: {origins}")
            
            frontend_origins = ['http://localhost:5173', 'http://localhost:3000']
            for origin in frontend_origins:
                if origin in origins:
                    print(f"✅ Frontend origin {origin} is allowed")
                else:
                    print(f"⚠️  Frontend origin {origin} not in allowed origins")
        
        return True
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SaaS Cafeterías Backend Debugging")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test database
    if not test_database():
        all_passed = False
    
    # Test CORS
    if not test_cors_config():
        all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All basic tests passed!")
        print("\n📝 Next steps:")
        print("1. Start the server: python -m uvicorn app.main:app --reload")
        print("2. Test API endpoints by running: python debug_backend.py --test-api")
        print("3. Access API docs: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Fix the issues above before starting the server.")
    
    # Test API if server is supposed to be running
    if len(sys.argv) > 1 and sys.argv[1] == "--test-api":
        print("\n🌐 Testing API endpoints (server must be running)...")
        api_result = asyncio.run(test_api_endpoints())
        if api_result:
            print("\n🎉 API tests passed! Backend is working correctly.")
        else:
            print("\n❌ API tests failed. Check server logs.")

if __name__ == "__main__":
    main()