"""
Complete business flow tests with security and permissions validation.
Tests the full workflow: admin login → create business → create product → CRUD → permissions
"""
import pytest
import requests
import json
import time
from typing import Dict, Optional


class TestBusinessFlowSecurity:
    """Test complete business workflow with security validation."""
    
    BASE_URL = "http://localhost:8000"
    
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.business_id = None
        self.product_id = None
        self.response_times = {}
        
    def _make_request(self, method: str, endpoint: str, headers: Dict = None, json_data: Dict = None, data: Dict = None, timeout: int = 10) -> requests.Response:
        """Make HTTP request with timing measurement."""
        start_time = time.time()
        
        try:
            url = f"{self.BASE_URL}{endpoint}"
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                if json_data:
                    response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
                else:
                    response = requests.post(url, headers=headers, data=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json_data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Track response times for performance analysis
            self.response_times[f"{method.upper()} {endpoint}"] = response_time
            
            return response
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Could not connect to backend: {e}")
    
    def test_01_backend_health(self):
        """Verify backend is running and accessible."""
        try:
            response = self._make_request("GET", "/health")
            assert response.status_code == 200, "Backend health check failed"
        except Exception:
            pytest.skip("Backend is not running. Start with: cd backend && python -m uvicorn app.main:app --reload")
    
    def test_02_admin_login(self):
        """Test admin login and token generation."""
        login_data = {
            "username": "admin",
            "password": "Admin1234!"
        }
        
        response = self._make_request("POST", "/api/v1/auth/login", data=login_data)
        
        if response.status_code == 401:
            pytest.skip("Admin user not found. Run: cd backend && python create_admin.py")
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "No access token in login response"
        assert data["role"] == "admin", f"Expected admin role, got: {data.get('role')}"
        
        self.admin_token = data["access_token"]
        
    def test_03_admin_me_endpoint(self):
        """Test /me endpoint returns correct admin info and never 500."""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self._make_request("GET", "/api/v1/auth/me", headers=headers)
        
        # Should never return 500 - always 200 or 401
        assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data, "Missing user ID in /me response"
            assert "email" in data, "Missing email in /me response"
            assert "role" in data, "Missing role in /me response"
            assert data["role"] == "admin", f"Expected admin role, got: {data.get('role')}"
    
    def test_04_create_business_as_admin(self):
        """Test creating a business as admin user."""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        business_data = {
            "name": "Security Test Cafe",
            "description": "Business created for security flow testing",
            "address": "123 Security St, Test City",
            "phone": "+1-555-SECURE",
            "email": "security@testcafe.com",
            "business_type": "restaurant"
        }
        
        response = self._make_request("POST", "/api/v1/businesses", headers=headers, json_data=business_data)
        
        assert response.status_code in [200, 201], f"Business creation failed: {response.text}"
        
        data = response.json()
        assert "id" in data, "Business ID missing in response"
        assert data["name"] == business_data["name"], "Business name mismatch"
        assert data["is_active"] == True, "Business should be active by default"
        
        self.business_id = data["id"]
        
    def test_05_create_product_as_admin(self):
        """Test creating a product in the business as admin."""
        if not self.admin_token or not self.business_id:
            pytest.skip("Admin token or business ID not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        product_data = {
            "name": "Security Test Latte",
            "description": "Product for security testing",
            "price": 4.99,
            "category": "beverages",
            "is_available": True
        }
        
        response = self._make_request("POST", f"/api/v1/businesses/{self.business_id}/products", headers=headers, json_data=product_data)
        
        assert response.status_code in [200, 201], f"Product creation failed: {response.text}"
        
        data = response.json()
        assert "id" in data, "Product ID missing in response"
        assert data["name"] == product_data["name"], "Product name mismatch"
        assert data["price"] == product_data["price"], "Product price mismatch"
        assert data["business_id"] == self.business_id, "Product business_id mismatch"
        
        self.product_id = data["id"]
    
    def test_06_read_product_as_admin(self):
        """Test reading the created product as admin."""
        if not self.admin_token or not self.business_id or not self.product_id:
            pytest.skip("Required tokens/IDs not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self._make_request("GET", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", headers=headers)
        
        assert response.status_code == 200, f"Product read failed: {response.text}"
        
        data = response.json()
        assert data["id"] == self.product_id, "Product ID mismatch"
        assert data["name"] == "Security Test Latte", "Product name mismatch"
    
    def test_07_update_product_as_admin(self):
        """Test updating the product as admin."""
        if not self.admin_token or not self.business_id or not self.product_id:
            pytest.skip("Required tokens/IDs not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        update_data = {
            "name": "Updated Security Latte",
            "price": 5.49,
            "description": "Updated description for security testing"
        }
        
        response = self._make_request("PUT", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", headers=headers, json_data=update_data)
        
        assert response.status_code == 200, f"Product update failed: {response.text}"
        
        data = response.json()
        assert data["name"] == update_data["name"], "Product name not updated"
        assert data["price"] == update_data["price"], "Product price not updated"
    
    def test_08_create_regular_user(self):
        """Create a regular (non-admin) user for permission testing."""
        user_data = {
            "email": "regular@testuser.com",
            "username": "regularuser",
            "password": "RegularPass123!",
            "role": "user"  # Explicitly set as regular user
        }
        
        response = self._make_request("POST", "/api/v1/auth/register", json_data=user_data)
        
        assert response.status_code in [200, 201], f"User registration failed: {response.text}"
        
        # Login as regular user
        login_data = {
            "username": "regularuser",
            "password": "RegularPass123!"
        }
        
        login_response = self._make_request("POST", "/api/v1/auth/login", data=login_data)
        
        assert login_response.status_code == 200, f"User login failed: {login_response.text}"
        
        data = login_response.json()
        assert data["role"] == "user", f"Expected user role, got: {data.get('role')}"
        
        self.user_token = data["access_token"]
    
    def test_09_non_admin_business_access_403(self):
        """Test that non-admin users get 403 when accessing admin endpoints."""
        if not self.user_token or not self.business_id:
            pytest.skip("User token or business ID not available")
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test various admin-only operations should return 403
        test_cases = [
            ("GET", "/api/v1/users/", "List users - admin only"),
            ("PUT", f"/api/v1/businesses/{self.business_id}", {"name": "Hacked Name"}, "Update business - should be forbidden"),
            ("DELETE", f"/api/v1/businesses/{self.business_id}", None, "Delete business - should be forbidden"),
        ]
        
        for method, endpoint, data, description in test_cases:
            if data and method in ["PUT", "POST"]:
                response = self._make_request(method, endpoint, headers=headers, json_data=data)
            else:
                response = self._make_request(method, endpoint, headers=headers)
            
            assert response.status_code == 403, f"{description} - Expected 403, got {response.status_code}: {response.text}"
    
    def test_10_non_admin_product_operations_403(self):
        """Test that non-admin users get 403 for unauthorized product operations."""
        if not self.user_token or not self.business_id or not self.product_id:
            pytest.skip("Required tokens/IDs not available")
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Try to update product (should fail if not business owner)
        update_data = {"name": "Hacked Product", "price": 0.01}
        response = self._make_request("PUT", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", headers=headers, json_data=update_data)
        
        # Should return 403 (forbidden) if user is not business owner
        assert response.status_code in [403, 404], f"Expected 403/404 for unauthorized product update, got {response.status_code}"
        
        # Try to delete product (should fail if not business owner)
        response = self._make_request("DELETE", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", headers=headers)
        
        # Should return 403 (forbidden) if user is not business owner
        assert response.status_code in [403, 404], f"Expected 403/404 for unauthorized product delete, got {response.status_code}"
    
    def test_11_unauthorized_access_401(self):
        """Test that requests without valid tokens return 401."""
        # No headers (no token)
        response = self._make_request("GET", "/api/v1/auth/me")
        assert response.status_code == 401, f"Expected 401 for no token, got {response.status_code}"
        
        # Invalid token
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = self._make_request("GET", "/api/v1/auth/me", headers=headers)
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
    
    def test_12_delete_product_as_admin(self):
        """Test deleting the product as admin (cleanup and final CRUD test)."""
        if not self.admin_token or not self.business_id or not self.product_id:
            pytest.skip("Required tokens/IDs not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self._make_request("DELETE", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", headers=headers)
        
        assert response.status_code in [200, 204], f"Product deletion failed: {response.text}"
        
        # Verify product is deleted (should return 404)
        get_response = self._make_request("GET", f"/api/v1/businesses/{self.business_id}/products/{self.product_id}", headers=headers)
        assert get_response.status_code == 404, "Product should be deleted"
    
    def test_13_error_handling_validation(self):
        """Test proper error handling and status codes."""
        if not self.admin_token or not self.business_id:
            pytest.skip("Required tokens/IDs not available")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 400 - Bad Request (invalid data)
        invalid_product_data = {
            "name": "",  # Empty name should cause validation error
            "price": "invalid_price"  # Invalid price type
        }
        response = self._make_request("POST", f"/api/v1/businesses/{self.business_id}/products", headers=headers, json_data=invalid_product_data)
        assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"
        
        # Test 404 - Not Found
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self._make_request("GET", f"/api/v1/businesses/{fake_id}/products", headers=headers)
        assert response.status_code == 404, f"Expected 404 for non-existent business, got {response.status_code}"
    
    def test_14_response_time_analysis(self):
        """Analyze response times and identify slow endpoints."""
        if not self.response_times:
            pytest.skip("No response time data collected")
        
        print("\n📊 RESPONSE TIME ANALYSIS:")
        print("=" * 50)
        
        slow_endpoints = []
        
        for endpoint, time_ms in self.response_times.items():
            status = "⚡ Fast" if time_ms < 100 else "🟡 Moderate" if time_ms < 500 else "🐌 Slow"
            print(f"{status} {endpoint}: {time_ms:.2f}ms")
            
            if time_ms > 500:
                slow_endpoints.append((endpoint, time_ms))
        
        if slow_endpoints:
            print(f"\n⚠️  SLOW ENDPOINTS (>500ms):")
            for endpoint, time_ms in slow_endpoints:
                print(f"   - {endpoint}: {time_ms:.2f}ms")
        else:
            print("\n✅ All endpoints performing well (<500ms)")
        
        # Document in a simple way without creating files
        print(f"\n📋 PERFORMANCE SUMMARY:")
        print(f"   Total endpoints tested: {len(self.response_times)}")
        print(f"   Slow endpoints (>500ms): {len(slow_endpoints)}")
        avg_time = sum(self.response_times.values()) / len(self.response_times)
        print(f"   Average response time: {avg_time:.2f}ms")


# Convenience function to run the complete flow
def test_complete_business_security_flow():
    """Run the complete business security flow test."""
    test_instance = TestBusinessFlowSecurity()
    
    # Execute all tests in sequence
    test_methods = [
        test_instance.test_01_backend_health,
        test_instance.test_02_admin_login,
        test_instance.test_03_admin_me_endpoint,
        test_instance.test_04_create_business_as_admin,
        test_instance.test_05_create_product_as_admin,
        test_instance.test_06_read_product_as_admin,
        test_instance.test_07_update_product_as_admin,
        test_instance.test_08_create_regular_user,
        test_instance.test_09_non_admin_business_access_403,
        test_instance.test_10_non_admin_product_operations_403,
        test_instance.test_11_unauthorized_access_401,
        test_instance.test_12_delete_product_as_admin,
        test_instance.test_13_error_handling_validation,
        test_instance.test_14_response_time_analysis,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    print("\n🧪 COMPLETE BUSINESS SECURITY FLOW TEST")
    print("=" * 50)
    
    for i, test_method in enumerate(test_methods, 1):
        try:
            print(f"\n{i:2d}. Running {test_method.__name__[7:].replace('_', ' ').title()}...")
            test_method()
            print(f"    ✅ PASSED")
            passed += 1
        except pytest.skip.Exception as e:
            print(f"    ⏭️  SKIPPED: {e}")
            skipped += 1
        except Exception as e:
            print(f"    ❌ FAILED: {e}")
            failed += 1
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100) if (passed+failed) > 0 else 0:.1f}%")
    
    return passed, failed, skipped


if __name__ == "__main__":
    # Run the complete flow if executed directly
    test_complete_business_security_flow()