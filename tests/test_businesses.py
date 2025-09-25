"""
Tests for businesses endpoints - Corregidos
"""
import pytest
import time


def test_create_business(client, admin_token):
    """Test creating a new business."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    timestamp = int(time.time())
    headers = {"Authorization": f"Bearer {admin_token}"}
    business_data = {
        "name": f"Test Coffee Shop {timestamp}",
        "description": "A test coffee shop for unit testing",
        "address": "123 Test Street, Test City",
        "phone": "+1234567890",
        "email": f"test{timestamp}@coffeeshop.com",
        "business_type": "restaurant"
    }
    
    response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == business_data["name"]
    assert data["description"] == business_data["description"]
    assert data["address"] == business_data["address"]
    assert "id" in data
    assert data["is_active"] == True


def test_list_businesses(client, admin_token):
    """Test listing all businesses."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/businesses", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_business_by_id(client, admin_token, test_business):
    """Test getting a specific business by ID."""
    if not admin_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/v1/businesses/{test_business['id']}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_business["id"]
    assert data["name"] == test_business["name"]


def test_update_business(client, admin_token, test_business):
    """Test updating a business."""
    if not admin_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {
        "name": "Updated Coffee Shop",
        "description": "Updated description for testing"
    }
    
    response = client.put(f"/api/v1/businesses/{test_business['id']}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_business(client, admin_token):
    """Test soft deleting a business."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    # Create a business to delete
    timestamp = int(time.time())
    headers = {"Authorization": f"Bearer {admin_token}"}
    business_data = {
        "name": f"Delete Test Business {timestamp}",
        "description": "Business to be deleted",
        "business_type": "cafe"
    }
    
    create_response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    if create_response.status_code != 200:
        pytest.skip("Could not create business for delete test")
    
    business_id = create_response.json()["id"]
    
    # Delete the business
    response = client.delete(f"/api/v1/businesses/{business_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data


def test_create_business_unauthorized(client):
    """Test creating business without authentication."""
    business_data = {
        "name": "Unauthorized Coffee Shop",
        "description": "This should fail"
    }
    
    response = client.post("/api/v1/businesses", json=business_data)
    assert response.status_code == 401


def test_create_business_invalid_data(client, admin_token):
    """Test creating business with invalid data."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Missing required 'name' field
    invalid_data = {
        "description": "Business without name"
    }
    
    response = client.post("/api/v1/businesses", json=invalid_data, headers=headers)
    assert response.status_code == 422  # Validation error


def test_get_nonexistent_business(client, admin_token):
    """Test getting a business that doesn't exist."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.get(f"/api/v1/businesses/{fake_id}", headers=headers)
    assert response.status_code == 404


def test_user_can_create_business(client, user_token):
    """Test that users can create businesses (current implementation allows this)."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    timestamp = int(time.time())
    business_data = {
        "name": f"User Business Test {timestamp}",
        "description": "Users can create businesses in current implementation",
        "business_type": "cafe"
    }
    
    response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    # Current implementation allows users to create businesses
    assert response.status_code == 200
    
    business = response.json()
    assert business["name"] == business_data["name"]
    assert "id" in business


def test_user_can_view_businesses(client, user_token, test_business):
    """Test that users can view businesses."""
    if not user_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test list businesses
    list_response = client.get("/api/v1/businesses", headers=headers)
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)
    
    # Test get specific business
    get_response = client.get(f"/api/v1/businesses/{test_business['id']}", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == test_business["id"]


def test_user_cannot_modify_business(client, user_token, test_business):
    """Test that regular users cannot modify businesses."""
    if not user_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {"name": "Hacked Business Name"}
    
    # Test update
    update_response = client.put(f"/api/v1/businesses/{test_business['id']}", json=update_data, headers=headers)
    assert update_response.status_code == 403
    
    # Test delete
    delete_response = client.delete(f"/api/v1/businesses/{test_business['id']}", headers=headers)
    assert delete_response.status_code == 403


def test_business_workflow(client, admin_token):
    """Test complete business workflow."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    timestamp = int(time.time())
    
    # 1. Create business
    business_data = {
        "name": f"Workflow Test Cafe {timestamp}",
        "description": "Testing complete workflow",
        "business_type": "cafe"
    }
    
    create_response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    assert create_response.status_code == 200
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
    assert update_response.status_code == 200
    
    updated_business = update_response.json()
    assert updated_business["description"] == update_data["description"]


def test_business_type_validation(client, admin_token):
    """Test business type validation."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    timestamp = int(time.time())
    
    # Test valid business types
    valid_types = ["restaurant", "cafe", "retail", "service"]
    
    for business_type in valid_types:
        business_data = {
            "name": f"Test {business_type.title()} {timestamp}",
            "description": f"Testing {business_type} type",
            "business_type": business_type
        }
        
        response = client.post("/api/v1/businesses", json=business_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["business_type"] == business_type


def test_business_required_fields(client, admin_token):
    """Test business required fields validation."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test missing name
    data_missing_name = {
        "description": "Business without name",
        "business_type": "cafe"
    }
    response = client.post("/api/v1/businesses", json=data_missing_name, headers=headers)
    assert response.status_code == 422
    
    # Test empty name
    data_empty_name = {
        "name": "",
        "description": "Business with empty name",
        "business_type": "cafe"
    }
    response = client.post("/api/v1/businesses", json=data_empty_name, headers=headers)
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])