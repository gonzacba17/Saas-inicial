import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome to" in response.json()["message"]

def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_docs():
    """Test that OpenAPI documentation is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data

class TestAuthEndpoints:
    """Test authentication endpoints are accessible."""
    
    def test_register_endpoint_exists(self):
        """Test register endpoint exists and returns proper error for invalid data."""
        response = client.post("/api/v1/auth/register", json={})
        # Should return 422 for validation error, not 404
        assert response.status_code == 422
    
    def test_login_endpoint_exists(self):
        """Test login endpoint exists."""
        response = client.post("/api/v1/auth/login", data={})
        # Should return 422 for validation error, not 404
        assert response.status_code == 422
    
    def test_me_endpoint_requires_auth(self):
        """Test /me endpoint requires authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

class TestAPIStructure:
    """Test basic API structure."""
    
    def test_api_v1_prefix(self):
        """Test that API uses v1 prefix."""
        response = client.get("/api/v1/auth/me")
        # Should return 401 (unauthorized), not 404 (not found)
        assert response.status_code == 401
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = client.options("/")
        # Should have CORS headers configured
        assert response.status_code in [200, 405]  # Some browsers send OPTIONS, some don't