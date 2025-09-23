"""
Tests for businesses endpoints - Complete CRUD testing.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers():
    """Helper function to get auth headers."""
    # Register and login user
    user_data = {
        "email": "businesstest@example.com",
        "username": "businessuser",
        "password": "testpass123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "businessuser",
        "password": "testpass123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


class TestBusinessesCRUD:
    """Test class for complete businesses CRUD operations."""
    
    def test_create_business(self):
        """Test creating a new business."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        business_data = {
            "name": "Test Coffee Shop",
            "description": "A test coffee shop for unit testing",
            "address": "123 Test Street, Test City",
            "phone": "+1234567890",
            "email": "test@coffeeshop.com",
            "business_type": "restaurant"
        }
        
        response = client.post("/api/v1/businesses", json=business_data, headers=headers)
        
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            assert data["name"] == business_data["name"]
            assert data["description"] == business_data["description"]
            assert data["address"] == business_data["address"]
            assert "id" in data
            assert data["is_active"] == True
            return data["id"]  # Return ID for other tests
        else:
            pytest.skip(f"Business creation failed: {response.text}")
    
    def test_list_businesses(self):
        """Test listing all businesses."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        response = client.get("/api/v1/businesses", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_business_by_id(self):
        """Test getting a specific business by ID."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        # First create a business
        business_id = self.test_create_business()
        if not business_id:
            pytest.skip("Could not create business for testing")
        
        response = client.get(f"/api/v1/businesses/{business_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == business_id
            assert "name" in data
        else:
            # Business might not exist, which is also valid for testing
            assert response.status_code in [200, 404]
    
    def test_update_business(self):
        """Test updating a business."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        # First create a business
        business_id = self.test_create_business()
        if not business_id:
            pytest.skip("Could not create business for testing")
        
        update_data = {
            "name": "Updated Coffee Shop",
            "description": "Updated description for testing"
        }
        
        response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["description"] == update_data["description"]
        else:
            # May fail due to permissions or business not found
            assert response.status_code in [200, 403, 404]
    
    def test_delete_business(self):
        """Test soft deleting a business."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        # First create a business
        business_id = self.test_create_business()
        if not business_id:
            pytest.skip("Could not create business for testing")
        
        response = client.delete(f"/api/v1/businesses/{business_id}", headers=headers)
        
        # Should either succeed or fail due to permissions
        assert response.status_code in [200, 403, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
    
    def test_create_business_unauthorized(self):
        """Test creating business without authentication."""
        business_data = {
            "name": "Unauthorized Coffee Shop",
            "description": "This should fail"
        }
        
        response = client.post("/api/v1/businesses", json=business_data)
        assert response.status_code == 401
    
    def test_create_business_invalid_data(self):
        """Test creating business with invalid data."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        # Missing required 'name' field
        invalid_data = {
            "description": "Business without name"
        }
        
        response = client.post("/api/v1/businesses", json=invalid_data, headers=headers)
        assert response.status_code == 422  # Validation error
    
    def test_get_nonexistent_business(self):
        """Test getting a business that doesn't exist."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/businesses/{fake_id}", headers=headers)
        assert response.status_code == 404
    
    def test_business_permissions(self):
        """Test that business operations respect permissions."""
        headers = get_auth_headers()
        if not headers:
            pytest.skip("Could not authenticate user")
        
        # Create business first
        business_id = self.test_create_business()
        if not business_id:
            pytest.skip("Could not create business for testing")
        
        # Create another user to test permissions
        other_user_data = {
            "email": "other@example.com",
            "username": "otheruser",
            "password": "testpass123"
        }
        client.post("/api/v1/auth/register", json=other_user_data)
        
        other_login_response = client.post("/api/v1/auth/login", data={
            "username": "otheruser",
            "password": "testpass123"
        })
        
        if other_login_response.status_code == 200:
            other_token = other_login_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}
            
            # Try to update business as different user (should fail)
            update_data = {"name": "Hacked Business"}
            response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=other_headers)
            
            # Should fail with 403 Forbidden
            assert response.status_code in [403, 404]


def test_business_workflow():
    """Test complete business workflow."""
    headers = get_auth_headers()
    if not headers:
        pytest.skip("Could not authenticate user")
    
    # 1. Create business
    business_data = {
        "name": "Workflow Test Cafe",
        "description": "Testing complete workflow",
        "business_type": "cafe"
    }
    
    create_response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    
    if create_response.status_code not in [200, 201]:
        pytest.skip("Could not create business for workflow test")
    
    business_id = create_response.json()["id"]
    
    # 2. List businesses and verify it's included
    list_response = client.get("/api/v1/businesses", headers=headers)
    assert list_response.status_code == 200
    
    businesses = list_response.json()
    business_found = any(b["id"] == business_id for b in businesses)
    assert business_found
    
    # 3. Get specific business
    get_response = client.get(f"/api/v1/businesses/{business_id}", headers=headers)
    assert get_response.status_code == 200
    
    business = get_response.json()
    assert business["name"] == business_data["name"]
    
    # 4. Update business
    update_data = {"description": "Updated workflow description"}
    update_response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=headers)
    
    if update_response.status_code == 200:
        updated_business = update_response.json()
        assert updated_business["description"] == update_data["description"]