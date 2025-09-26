#!/usr/bin/env python3
"""
Improved comprehensive auth tests
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
from app.services import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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
def sample_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }

@pytest.fixture
def admin_user():
    return {
        "username": "admin",
        "email": "admin@example.com", 
        "password": "AdminPassword123!",
        "role": "admin"
    }

class TestUserRegistration:
    def test_register_user_success(self, client, sample_user):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user["username"]
        assert data["email"] == sample_user["email"]
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, sample_user):
        """Test registration with duplicate username"""
        # Register first user
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Try to register with same username
        duplicate_user = sample_user.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/api/v1/auth/register", json=duplicate_user)
        assert response.status_code == 400

    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Try to register with same email
        duplicate_user = sample_user.copy()
        duplicate_user["username"] = "differentuser"
        response = client.post("/api/v1/auth/register", json=duplicate_user)
        assert response.status_code == 400

    def test_register_weak_password(self, client, sample_user):
        """Test registration with weak password"""
        weak_user = sample_user.copy()
        weak_user["password"] = "123"
        response = client.post("/api/v1/auth/register", json=weak_user)
        assert response.status_code == 422

    def test_register_invalid_email(self, client, sample_user):
        """Test registration with invalid email format"""
        invalid_user = sample_user.copy()
        invalid_user["email"] = "invalid-email"
        response = client.post("/api/v1/auth/register", json=invalid_user)
        assert response.status_code == 422

class TestUserLogin:
    def test_login_success(self, client, sample_user):
        """Test successful login"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Login
        login_data = {
            "username": sample_user["username"],
            "password": sample_user["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_email(self, client, sample_user):
        """Test login with email instead of username"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Login with email
        login_data = {
            "username": sample_user["email"],
            "password": sample_user["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200

    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user)
        
        # Try login with wrong password
        login_data = {
            "username": sample_user["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "username": "nonexistent",
            "password": "password"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

class TestTokenValidation:
    def test_get_current_user_valid_token(self, client, sample_user):
        """Test getting current user with valid token"""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user)
        login_response = client.post("/api/v1/auth/login", data={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        token = login_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user["username"]
        assert data["email"] == sample_user["email"]

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

class TestUserRoles:
    def test_user_default_role(self, client, sample_user):
        """Test that new users get default role"""
        client.post("/api/v1/auth/register", json=sample_user)
        login_response = client.post("/api/v1/auth/login", data={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        data = response.json()
        assert data["role"] == "user"

    def test_admin_user_registration(self, client, admin_user):
        """Test admin user creation"""
        response = client.post("/api/v1/auth/register", json=admin_user)
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "admin"

class TestPasswordSecurity:
    def test_password_hashing(self, client, sample_user):
        """Test that passwords are properly hashed"""
        response = client.post("/api/v1/auth/register", json=sample_user)
        assert response.status_code == 201
        
        # Password should not be in response
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data
        
        # Should be able to login with original password
        login_response = client.post("/api/v1/auth/login", data={
            "username": sample_user["username"],
            "password": sample_user["password"]
        })
        assert login_response.status_code == 200

class TestErrorHandling:
    def test_malformed_registration_data(self, client):
        """Test registration with malformed data"""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422

    def test_malformed_login_data(self, client):
        """Test login with malformed data"""
        response = client.post("/api/v1/auth/login", data={})
        assert response.status_code == 422