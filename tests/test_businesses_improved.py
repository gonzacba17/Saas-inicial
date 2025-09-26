#!/usr/bin/env python3
"""
Improved comprehensive business tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.db import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_businesses.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture
def auth_user(client):
    """Create and login a test user"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    client.post("/api/v1/auth/register", json=user_data)
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_user(client):
    """Create and login an admin user"""
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "role": "admin"
    }
    client.post("/api/v1/auth/register", json=admin_data)
    login_response = client.post("/api/v1/auth/login", data={
        "username": admin_data["username"],
        "password": admin_data["password"]
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_business():
    return {
        "name": "Test Coffee Shop",
        "description": "A great coffee shop for testing",
        "address": "123 Test Street",
        "phone": "+1234567890",
        "email": "test@coffeeshop.com",
        "business_type": "restaurant"
    }

class TestBusinessCreation:
    def test_create_business_success(self, client, auth_user, sample_business):
        """Test successful business creation"""
        response = client.post("/api/v1/businesses/", json=sample_business, headers=auth_user)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_business["name"]
        assert data["description"] == sample_business["description"]
        assert data["address"] == sample_business["address"]
        assert "id" in data
        assert "created_at" in data

    def test_create_business_unauthorized(self, client, sample_business):
        """Test business creation without authentication"""
        response = client.post("/api/v1/businesses/", json=sample_business)
        assert response.status_code == 401

    def test_create_business_missing_required_fields(self, client, auth_user):
        """Test business creation with missing required fields"""
        incomplete_business = {"description": "Missing name"}
        response = client.post("/api/v1/businesses/", json=incomplete_business, headers=auth_user)
        assert response.status_code == 422

    def test_create_business_invalid_type(self, client, auth_user, sample_business):
        """Test business creation with invalid business type"""
        invalid_business = sample_business.copy()
        invalid_business["business_type"] = "invalid_type"
        response = client.post("/api/v1/businesses/", json=invalid_business, headers=auth_user)
        # Should either reject or default to valid type
        assert response.status_code in [201, 422]

class TestBusinessRetrieval:
    def test_list_businesses_empty(self, client, auth_user):
        """Test listing businesses when none exist"""
        response = client.get("/api/v1/businesses/", headers=auth_user)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_businesses_with_data(self, client, auth_user, sample_business):
        """Test listing businesses with data"""
        # Create a business first
        client.post("/api/v1/businesses/", json=sample_business, headers=auth_user)
        
        response = client.get("/api/v1/businesses/", headers=auth_user)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == sample_business["name"]

    def test_get_business_by_id(self, client, auth_user, sample_business):
        """Test getting specific business by ID"""
        # Create a business first
        create_response = client.post("/api/v1/businesses/", json=sample_business, headers=auth_user)
        business_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/businesses/{business_id}", headers=auth_user)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == business_id
        assert data["name"] == sample_business["name"]

    def test_get_nonexistent_business(self, client, auth_user):
        """Test getting non-existent business"""
        response = client.get("/api/v1/businesses/nonexistent-id", headers=auth_user)
        assert response.status_code == 404

    def test_list_businesses_unauthorized(self, client):
        """Test listing businesses without authentication"""
        response = client.get("/api/v1/businesses/")
        assert response.status_code == 401

class TestBusinessUpdate:
    def test_update_business_success(self, client, auth_user, sample_business):
        """Test successful business update"""
        # Create a business first
        create_response = client.post("/api/v1/businesses/", json=sample_business, headers=auth_user)
        business_id = create_response.json()["id"]
        
        # Update the business
        update_data = {"name": "Updated Coffee Shop", "description": "Updated description"}
        response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=auth_user)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_nonexistent_business(self, client, auth_user):
        """Test updating non-existent business"""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/businesses/nonexistent-id", json=update_data, headers=auth_user)
        assert response.status_code == 404

    def test_update_business_unauthorized(self, client, sample_business):
        """Test updating business without authentication"""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/v1/businesses/some-id", json=update_data)
        assert response.status_code == 401

class TestBusinessDeletion:
    def test_delete_business_success(self, client, auth_user, sample_business):
        """Test successful business deletion"""
        # Create a business first
        create_response = client.post("/api/v1/businesses/", json=sample_business, headers=auth_user)
        business_id = create_response.json()["id"]
        
        # Delete the business
        response = client.delete(f"/api/v1/businesses/{business_id}", headers=auth_user)
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/businesses/{business_id}", headers=auth_user)
        assert get_response.status_code == 404

    def test_delete_nonexistent_business(self, client, auth_user):
        """Test deleting non-existent business"""
        response = client.delete("/api/v1/businesses/nonexistent-id", headers=auth_user)
        assert response.status_code == 404

    def test_delete_business_unauthorized(self, client):
        """Test deleting business without authentication"""
        response = client.delete("/api/v1/businesses/some-id")
        assert response.status_code == 401

class TestBusinessOwnership:
    def test_business_owner_permissions(self, client, auth_user, sample_business):
        """Test that business owner can manage their business"""
        # Create business
        create_response = client.post("/api/v1/businesses/", json=sample_business, headers=auth_user)
        business_id = create_response.json()["id"]
        
        # Owner should be able to update
        update_data = {"name": "Updated by Owner"}
        response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=auth_user)
        assert response.status_code == 200

    def test_non_owner_permissions(self, client, sample_business):
        """Test that non-owners cannot modify businesses they don't own"""
        # Create first user and business
        user1_data = {"username": "user1", "email": "user1@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user1_data)
        login1_response = client.post("/api/v1/auth/login", data={
            "username": user1_data["username"],
            "password": user1_data["password"]
        })
        user1_headers = {"Authorization": f"Bearer {login1_response.json()['access_token']}"}
        
        create_response = client.post("/api/v1/businesses/", json=sample_business, headers=user1_headers)
        business_id = create_response.json()["id"]
        
        # Create second user
        user2_data = {"username": "user2", "email": "user2@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user2_data)
        login2_response = client.post("/api/v1/auth/login", data={
            "username": user2_data["username"],
            "password": user2_data["password"]
        })
        user2_headers = {"Authorization": f"Bearer {login2_response.json()['access_token']}"}
        
        # User2 should not be able to update user1's business
        update_data = {"name": "Hacked Business"}
        response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=user2_headers)
        assert response.status_code in [403, 404]  # Forbidden or Not Found

class TestBusinessValidation:
    def test_business_name_validation(self, client, auth_user):
        """Test business name validation"""
        # Empty name
        business_data = {"name": "", "business_type": "restaurant"}
        response = client.post("/api/v1/businesses/", json=business_data, headers=auth_user)
        assert response.status_code == 422
        
        # Very long name
        business_data = {"name": "x" * 1000, "business_type": "restaurant"}
        response = client.post("/api/v1/businesses/", json=business_data, headers=auth_user)
        assert response.status_code in [201, 422]  # Should handle gracefully

    def test_business_email_validation(self, client, auth_user, sample_business):
        """Test business email validation"""
        invalid_business = sample_business.copy()
        invalid_business["email"] = "invalid-email"
        response = client.post("/api/v1/businesses/", json=invalid_business, headers=auth_user)
        assert response.status_code == 422

    def test_business_phone_validation(self, client, auth_user, sample_business):
        """Test business phone validation"""
        # Test with invalid phone format
        invalid_business = sample_business.copy()
        invalid_business["phone"] = "invalid-phone"
        response = client.post("/api/v1/businesses/", json=invalid_business, headers=auth_user)
        # Should either accept or validate phone format
        assert response.status_code in [201, 422]