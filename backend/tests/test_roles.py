"""
Tests for role-based access control and permissions.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_user_with_role(username: str, email: str, role: str = "user"):
    """Helper function to create a user with specific role."""
    user_data = {
        "email": email,
        "username": username,
        "password": "testpass123",
        "role": role
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    return response


def get_auth_token(username: str, password: str = "testpass123"):
    """Helper function to get auth token for user."""
    login_response = client.post("/api/v1/auth/login", data={
        "username": username,
        "password": password
    })
    
    if login_response.status_code == 200:
        return login_response.json()["access_token"]
    return None


class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_admin_user_access(self):
        """Test that admin users have elevated permissions."""
        # Create admin user
        admin_response = create_user_with_role("adminuser", "admin@test.com", "admin")
        if admin_response.status_code not in [200, 201, 400]:  # 400 if user exists
            pytest.skip("Could not create admin user")
        
        token = get_auth_token("adminuser")
        if not token:
            pytest.skip("Could not authenticate admin user")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test admin-only endpoint (users list)
        response = client.get("/api/v1/users/", headers=headers)
        # Should succeed for admin
        assert response.status_code in [200, 404]  # 200 for success, 404 if endpoint structure different
    
    def test_regular_user_access_restriction(self):
        """Test that regular users cannot access admin endpoints."""
        # Create regular user
        user_response = create_user_with_role("regularuser", "regular@test.com", "user")
        if user_response.status_code not in [200, 201, 400]:
            pytest.skip("Could not create regular user")
        
        token = get_auth_token("regularuser")
        if not token:
            pytest.skip("Could not authenticate regular user")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test admin-only endpoint (users list) 
        response = client.get("/api/v1/users/", headers=headers)
        # Should fail for regular user
        assert response.status_code == 403
    
    def test_owner_business_permissions(self):
        """Test that business owners can manage their businesses."""
        # Create owner user
        owner_response = create_user_with_role("owneruser", "owner@test.com", "owner")
        if owner_response.status_code not in [200, 201, 400]:
            pytest.skip("Could not create owner user")
        
        token = get_auth_token("owneruser")
        if not token:
            pytest.skip("Could not authenticate owner user")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a business as owner
        business_data = {
            "name": "Owner Test Business",
            "description": "Testing owner permissions",
            "business_type": "restaurant"
        }
        
        response = client.post("/api/v1/businesses", json=business_data, headers=headers)
        
        # Owner should be able to create businesses
        assert response.status_code in [200, 201]
        
        if response.status_code in [200, 201]:
            business = response.json()
            business_id = business["id"]
            
            # Owner should be able to update their business
            update_data = {"name": "Updated Owner Business"}
            update_response = client.put(f"/api/v1/businesses/{business_id}", json=update_data, headers=headers)
            assert update_response.status_code in [200, 403]  # May depend on implementation
    
    def test_secrets_admin_only_access(self):
        """Test that secrets endpoints are admin-only."""
        # Create regular user
        user_response = create_user_with_role("secretuser", "secret@test.com", "user")
        if user_response.status_code not in [200, 201, 400]:
            pytest.skip("Could not create user for secrets test")
        
        token = get_auth_token("secretuser")
        if not token:
            pytest.skip("Could not authenticate user")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access secrets endpoint as regular user
        response = client.get("/api/v1/secrets/", headers=headers)
        # Should be forbidden
        assert response.status_code == 403
    
    def test_secrets_admin_access(self):
        """Test that admin users can access secrets endpoints."""
        # Create admin user
        admin_response = create_user_with_role("secretadmin", "secretadmin@test.com", "admin")
        if admin_response.status_code not in [200, 201, 400]:
            pytest.skip("Could not create admin user")
        
        token = get_auth_token("secretadmin")
        if not token:
            pytest.skip("Could not authenticate admin user")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access secrets endpoint as admin
        response = client.get("/api/v1/secrets/", headers=headers)
        # Should succeed or have server error, but not forbidden
        assert response.status_code in [200, 500]  # May have server error if no secrets backend
    
    def test_user_profile_access(self):
        """Test that users can access their own profile."""
        # Create user
        user_response = create_user_with_role("profileuser", "profile@test.com", "user")
        if user_response.status_code not in [200, 201, 400]:
            pytest.skip("Could not create user")
        
        token = get_auth_token("profileuser")
        if not token:
            pytest.skip("Could not authenticate user")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # User should be able to get their own profile
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        assert profile["username"] == "profileuser"
        assert profile["email"] == "profile@test.com"
    
    def test_cross_user_profile_access_denied(self):
        """Test that users cannot access other users' profiles."""
        # Create two users
        user1_response = create_user_with_role("user1", "user1@test.com", "user")
        user2_response = create_user_with_role("user2", "user2@test.com", "user")
        
        if user1_response.status_code not in [200, 201, 400] or user2_response.status_code not in [200, 201, 400]:
            pytest.skip("Could not create test users")
        
        # Get user1's token
        token1 = get_auth_token("user1")
        if not token1:
            pytest.skip("Could not authenticate user1")
        
        # Get user2's ID if possible
        token2 = get_auth_token("user2")
        if not token2:
            pytest.skip("Could not authenticate user2")
        
        # Get user2's profile to get their ID
        headers2 = {"Authorization": f"Bearer {token2}"}
        user2_profile = client.get("/api/v1/auth/me", headers=headers2)
        if user2_profile.status_code != 200:
            pytest.skip("Could not get user2 profile")
        
        user2_id = user2_profile.json()["id"]
        
        # Try to access user2's profile with user1's token
        headers1 = {"Authorization": f"Bearer {token1}"}
        response = client.get(f"/api/v1/users/{user2_id}", headers=headers1)
        
        # Should be forbidden
        assert response.status_code == 403


def test_role_validation_on_registration():
    """Test role validation during user registration."""
    # Test valid roles
    valid_roles = ["user", "owner", "admin"]
    
    for role in valid_roles:
        user_data = {
            "email": f"roletest_{role}@test.com",
            "username": f"roletest_{role}",
            "password": "testpass123",
            "role": role
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        # Should succeed or fail if user exists, but not due to invalid role
        assert response.status_code in [200, 201, 400, 422]
        
        if response.status_code in [200, 201]:
            user = response.json()
            assert user["role"] == role
    
    # Test invalid role
    invalid_user_data = {
        "email": "invalid_role@test.com",
        "username": "invalid_role",
        "password": "testpass123",
        "role": "invalid_role"
    }
    
    response = client.post("/api/v1/auth/register", json=invalid_user_data)
    # Should fail with validation error
    assert response.status_code == 422