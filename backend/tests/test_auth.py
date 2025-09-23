"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # Should succeed or fail if user already exists
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data

def test_login_user():
    """Test user login."""
    # First ensure user exists
    user_data = {
        "email": "test@example.com", 
        "username": "testuser",
        "password": "testpass123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Test login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401

def test_get_current_user():
    """Test getting current user info."""
    # Login first to get token
    user_data = {
        "email": "test@example.com",
        "username": "testuser", 
        "password": "testpass123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

def test_unauthorized_access():
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401