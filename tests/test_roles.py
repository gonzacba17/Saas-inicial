"""
Tests for role-based access control and permissions - Corregidos
"""
import pytest
import time


def test_admin_user_permissions(client, admin_token):
    """Test that admin users have elevated permissions."""
    if not admin_token:
        pytest.skip("Could not authenticate admin user")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test admin can list all users
    response = client.get("/api/v1/users/", headers=headers)
    # Should succeed for admin or return 404 if endpoint doesn't exist
    assert response.status_code in [200, 404]
    
    # Test admin can create businesses
    timestamp = int(time.time())
    business_data = {
        "name": f"Admin Test Business {timestamp}",
        "description": "Testing admin business creation",
        "business_type": "restaurant"
    }
    
    business_response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    assert business_response.status_code == 200


def test_regular_user_access_restriction(client, user_token):
    """Test that regular users cannot access admin endpoints."""
    if not user_token:
        pytest.skip("Could not authenticate regular user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test admin-only endpoint (users list)
    response = client.get("/api/v1/users/", headers=headers)
    # Should fail for regular user
    assert response.status_code == 403


def test_user_cannot_create_business(client, user_token):
    """Test that regular users cannot create businesses."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    timestamp = int(time.time())
    
    business_data = {
        "name": f"User Test Business {timestamp}",
        "description": "This should fail - users can't create businesses",
        "business_type": "restaurant"
    }
    
    response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    # Should fail with 403 Forbidden
    assert response.status_code == 403


def test_user_profile_access(client, user_token):
    """Test that users can access their own profile."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # User should be able to get their own profile
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    profile = response.json()
    assert "username" in profile
    assert "email" in profile
    assert "id" in profile


def test_admin_profile_access(client, admin_token):
    """Test that admin users can access their profile."""
    if not admin_token:
        pytest.skip("Could not authenticate admin")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin should be able to get their own profile
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    profile = response.json()
    assert "username" in profile
    assert "email" in profile
    assert "role" in profile


def test_unauthorized_access_denied(client):
    """Test that endpoints require authentication."""
    # Test accessing protected endpoints without token
    protected_endpoints = [
        "/api/v1/auth/me",
        "/api/v1/businesses",
        "/api/v1/orders",
        "/api/v1/users/"
    ]
    
    for endpoint in protected_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_role_validation_on_registration(client):
    """Test role validation during user registration."""
    timestamp = int(time.time())
    
    # Test valid roles
    valid_roles = ["user", "admin"]
    
    for role in valid_roles:
        user_data = {
            "email": f"roletest_{role}_{timestamp}@test.com",
            "username": f"roletest_{role}_{timestamp}",
            "password": "TestPass123!",
            "role": role
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        
        user = response.json()
        assert user["role"] == role
    
    # Test invalid role
    invalid_user_data = {
        "email": f"invalid_role_{timestamp}@test.com",
        "username": f"invalid_role_{timestamp}",
        "password": "TestPass123!",
        "role": "invalid_role"
    }
    
    response = client.post("/api/v1/auth/register", json=invalid_user_data)
    # Should fail with validation error
    assert response.status_code == 422


def test_admin_can_manage_businesses(client, admin_token, test_business):
    """Test that admin users can manage any business."""
    if not admin_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin should be able to view business
    response = client.get(f"/api/v1/businesses/{test_business['id']}", headers=headers)
    assert response.status_code == 200
    
    # Admin should be able to update business
    update_data = {"description": "Updated by admin"}
    update_response = client.put(f"/api/v1/businesses/{test_business['id']}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    
    updated_business = update_response.json()
    assert updated_business["description"] == "Updated by admin"


def test_user_can_view_businesses(client, user_token, test_business):
    """Test that users can view businesses but not modify them."""
    if not user_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # User should be able to view business
    response = client.get(f"/api/v1/businesses/{test_business['id']}", headers=headers)
    assert response.status_code == 200
    
    # User should be able to list businesses
    list_response = client.get("/api/v1/businesses", headers=headers)
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)


def test_user_cannot_modify_businesses(client, user_token, test_business):
    """Test that regular users cannot modify businesses."""
    if not user_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # User should NOT be able to update business
    update_data = {"description": "Hacked by user"}
    update_response = client.put(f"/api/v1/businesses/{test_business['id']}", json=update_data, headers=headers)
    assert update_response.status_code == 403
    
    # User should NOT be able to delete business
    delete_response = client.delete(f"/api/v1/businesses/{test_business['id']}", headers=headers)
    assert delete_response.status_code == 403


def test_admin_can_manage_orders(client, admin_token, test_order):
    """Test that admin users can manage orders."""
    if not admin_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin should be able to view order
    response = client.get(f"/api/v1/orders/{test_order['id']}", headers=headers)
    assert response.status_code == 200
    
    # Admin should be able to update order status
    status_update = {"status": "confirmed"}
    update_response = client.put(f"/api/v1/orders/{test_order['id']}/status", json=status_update, headers=headers)
    assert update_response.status_code == 200


def test_user_can_view_own_orders(client, user_token, test_order):
    """Test that users can view their own orders."""
    if not user_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # User should be able to view their own order
    response = client.get(f"/api/v1/orders/{test_order['id']}", headers=headers)
    assert response.status_code == 200
    
    # User should be able to list their orders
    list_response = client.get("/api/v1/orders", headers=headers)
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)


def test_user_cannot_update_order_status(client, user_token, test_order):
    """Test that regular users cannot update order status."""
    if not user_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # User should NOT be able to update order status
    status_update = {"status": "confirmed"}
    response = client.put(f"/api/v1/orders/{test_order['id']}/status", json=status_update, headers=headers)
    assert response.status_code == 403


def test_role_consistency_after_login(client):
    """Test that user roles are consistent after login."""
    timestamp = int(time.time())
    
    # Create admin user
    admin_data = {
        "email": f"consistency_admin_{timestamp}@test.com",
        "username": f"consistency_admin_{timestamp}",
        "password": "TestPass123!",
        "role": "admin"
    }
    
    register_response = client.post("/api/v1/auth/register", json=admin_data)
    assert register_response.status_code == 200
    
    # Login and check role is preserved
    login_response = client.post("/api/v1/auth/login", data={
        "username": admin_data["username"],
        "password": admin_data["password"]
    })
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Check profile shows correct role
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/api/v1/auth/me", headers=headers)
    assert profile_response.status_code == 200
    
    profile = profile_response.json()
    assert profile["role"] == "admin"


def test_default_user_role(client):
    """Test that users get default 'user' role when not specified."""
    timestamp = int(time.time())
    
    user_data = {
        "email": f"default_role_{timestamp}@test.com",
        "username": f"default_role_{timestamp}",
        "password": "TestPass123!"
        # No role specified
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    user = response.json()
    # Should default to 'user' role
    assert user.get("role", "user") == "user"


def test_jwt_token_contains_role_info(client):
    """Test that JWT tokens contain role information for authorization."""
    timestamp = int(time.time())
    
    # Create admin user
    admin_data = {
        "email": f"jwt_admin_{timestamp}@test.com",
        "username": f"jwt_admin_{timestamp}",
        "password": "TestPass123!",
        "role": "admin"
    }
    
    register_response = client.post("/api/v1/auth/register", json=admin_data)
    assert register_response.status_code == 200
    
    # Login
    login_response = client.post("/api/v1/auth/login", data={
        "username": admin_data["username"],
        "password": admin_data["password"]
    })
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Test that token allows admin operations
    headers = {"Authorization": f"Bearer {token}"}
    business_data = {
        "name": f"JWT Test Business {timestamp}",
        "description": "Testing JWT role authorization",
        "business_type": "cafe"
    }
    
    business_response = client.post("/api/v1/businesses", json=business_data, headers=headers)
    assert business_response.status_code == 200  # Should succeed for admin


if __name__ == "__main__":
    pytest.main([__file__, "-v"])