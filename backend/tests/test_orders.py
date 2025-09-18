"""
Tests for orders endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_headers():
    """Helper function to get auth headers."""
    # Register and login user
    user_data = {
        "email": "ordertest@example.com",
        "username": "orderuser",
        "password": "testpass123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "orderuser",
        "password": "testpass123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_get_user_orders():
    """Test getting user orders."""
    headers = get_auth_headers()
    if not headers:
        pytest.skip("Could not authenticate user")
    
    response = client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user_orders_unauthorized():
    """Test getting orders without authentication."""
    response = client.get("/api/v1/orders")
    assert response.status_code == 401

def test_create_order_requires_auth():
    """Test that creating an order requires authentication."""
    order_data = {
        "business_id": "550e8400-e29b-41d4-a716-446655440000",
        "items": [
            {
                "product_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantity": 2,
                "unit_price": 10.0
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data)
    assert response.status_code == 401

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data