"""
Tests for authentication endpoints - Corregidos
"""
import pytest
import time


def test_register_user(client):
    """Test user registration."""
    timestamp = int(time.time())
    user_data = {
        "email": f"test{timestamp}@example.com",
        "username": f"testuser{timestamp}",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data


def test_login_user(client):
    """Test user login."""
    timestamp = int(time.time())
    user_data = {
        "email": f"login{timestamp}@example.com", 
        "username": f"loginuser{timestamp}",
        "password": "TestPass123!"
    }
    
    # Register user first
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    # Test login
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    timestamp = int(time.time())
    login_data = {
        "username": f"nonexistent{timestamp}",
        "password": "wrongpass"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401


def test_get_current_user(client, user_token):
    """Test getting current user info."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "email" in data
    assert "id" in data


def test_unauthorized_access(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_register_duplicate_user(client):
    """Test registering user with duplicate email/username."""
    timestamp = int(time.time())
    user_data = {
        "email": f"duplicate{timestamp}@example.com",
        "username": f"duplicateuser{timestamp}",
        "password": "TestPass123!"
    }
    
    # Register user first time
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 200
    
    # Try to register same user again
    response2 = client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400


def test_register_admin_user(client):
    """Test registering admin user."""
    timestamp = int(time.time())
    admin_data = {
        "email": f"admin{timestamp}@example.com",
        "username": f"adminuser{timestamp}",
        "password": "AdminPass123!",
        "role": "admin"
    }
    
    response = client.post("/api/v1/auth/register", json=admin_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == admin_data["email"]
    assert data["username"] == admin_data["username"]
    assert "role" in data


def test_weak_password_validation(client):
    """Test password validation."""
    timestamp = int(time.time())
    weak_password_data = {
        "email": f"weak{timestamp}@example.com",
        "username": f"weakuser{timestamp}",
        "password": "123"  # Too weak
    }
    
    response = client.post("/api/v1/auth/register", json=weak_password_data)
    # Should fail with validation error
    assert response.status_code in [400, 422]


def test_invalid_email_format(client):
    """Test registration with invalid email format."""
    timestamp = int(time.time())
    invalid_email_data = {
        "email": "invalid-email-format",
        "username": f"emailtest{timestamp}",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/v1/auth/register", json=invalid_email_data)
    # Should fail with validation error
    assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])