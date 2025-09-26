"""
Configuración de tests para pytest - Corregida
"""
import os
import sys
import pytest
import asyncio
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set environment variables for testing
os.environ['USE_SQLITE'] = 'true'
os.environ['ENVIRONMENT'] = 'test'
os.environ['DEBUG'] = 'false'
os.environ['PYTHONPATH'] = 'backend'

# Add backend to Python path
project_root = Path(__file__).parent.parent
backend_path = project_root / 'backend'
sys.path.insert(0, str(backend_path))

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_saas_cafeterias.db"

@pytest.fixture(scope="session")
def test_database():
    """Setup test database before running tests."""
    from app.db.db import Base, engine
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup after tests (optional - keep for debugging)
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function") 
def client(test_database):
    """FastAPI test client with fresh database per test."""
    from app.main import app
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def admin_token(client):
    """Get admin authentication token."""
    # Try to create admin user first
    admin_data = {
        "email": "admin@example.com",
        "username": "admin", 
        "password": "Admin1234!",
        "role": "admin"
    }
    
    # Register admin (may fail if exists)
    client.post("/api/v1/auth/register", json=admin_data)
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", data={
        "username": "admin",
        "password": "Admin1234!"
    })
    
    if login_response.status_code == 200:
        return login_response.json()["access_token"]
    return None

@pytest.fixture(scope="function") 
def user_token(client):
    """Get regular user authentication token."""
    import time
    
    user_data = {
        "email": f"testuser{int(time.time())}@test.com",
        "username": f"testuser{int(time.time())}",
        "password": "TestPass123!"
    }
    
    # Register user
    register_response = client.post("/api/v1/auth/register", json=user_data)
    if register_response.status_code != 200:
        return None
        
    # Login to get token
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    
    if login_response.status_code == 200:
        return login_response.json()["access_token"]
    return None

@pytest.fixture(scope="function")
def test_business(client, admin_token):
    """Create a test business."""
    if not admin_token:
        return None
        
    headers = {"Authorization": f"Bearer {admin_token}"}
    business_data = {
        "name": "Test Business",
        "description": "A test business",
        "address": "123 Test St",
        "business_type": "cafe"
    }
    
    response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

@pytest.fixture(scope="function")
def test_product(client, admin_token, test_business):
    """Create a test product."""
    if not admin_token or not test_business:
        return None
        
    headers = {"Authorization": f"Bearer {admin_token}"}
    product_data = {
        "business_id": test_business["id"],
        "name": "Test Product",
        "description": "A test product", 
        "price": 10.99,
        "category": "test"
    }
    
    response = client.post("/api/v1/products", json=product_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

@pytest.fixture(scope="function")
def test_order(client, user_token, test_business, test_product):
    """Create a test order."""
    if not user_token or not test_business or not test_product:
        return None
        
    headers = {"Authorization": f"Bearer {user_token}"}
    order_data = {
        "business_id": test_business["id"],
        "items": [
            {
                "product_id": test_product["id"],
                "quantity": 2,
                "unit_price": test_product["price"]
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()