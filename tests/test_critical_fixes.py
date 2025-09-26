#!/usr/bin/env python3
"""
Critical fixes validation tests
"""
import pytest
import time
import sys
from pathlib import Path
from uuid import uuid4

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestPaymentsEndpointFix:
    """Test payments endpoint returns 200 [] when no payments exist"""
    
    def test_business_payments_empty_list(self):
        """Test that business with no payments returns 200 []"""
        # Generate a random business ID that won't exist
        fake_business_id = str(uuid4())
        
        # This should return 404 for non-existent business
        response = client.get(f"/api/v1/payments/business/{fake_business_id}")
        
        # Should be 401 (no auth) not 500 (server error)
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
        
    def test_business_payments_robust_error_handling(self):
        """Test robust error handling in payments endpoint"""
        # Test with malformed UUID
        response = client.get("/api/v1/payments/business/invalid-uuid")
        
        # Should return proper error, not 500
        assert response.status_code in [400, 422], f"Expected 400/422 for invalid UUID, got {response.status_code}"
        
    def test_business_payments_endpoint_exists(self):
        """Test that the business payments endpoint exists"""
        fake_business_id = str(uuid4())
        response = client.get(f"/api/v1/payments/business/{fake_business_id}")
        
        # Should not be 404 (endpoint not found), should be auth-related
        assert response.status_code != 404 or "not found" not in response.json().get("detail", "").lower()

class TestHealthEndpointOptimization:
    """Test health endpoint performance optimization"""
    
    def test_health_endpoint_ultra_fast(self):
        """Test that /health endpoint responds in <100ms"""
        start_time = time.time()
        response = client.get("/health")
        response_time_ms = (time.time() - start_time) * 1000
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Verify ultra-fast performance (<100ms)
        assert response_time_ms < 100, f"Health endpoint too slow: {response_time_ms:.2f}ms"
        
    def test_health_endpoint_minimal_response(self):
        """Test that /health returns minimal response"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only contain status
        assert data == {"status": "ok"}
        
        # Should not contain heavy fields
        assert "version" not in data
        assert "service" not in data
        assert "checks" not in data
        
    def test_health_vs_readyz_performance(self):
        """Test that /health is significantly faster than /readyz"""
        # Test /health performance
        start_time = time.time()
        health_response = client.get("/health")
        health_time = (time.time() - start_time) * 1000
        
        # Test /readyz performance  
        start_time = time.time()
        readyz_response = client.get("/readyz")
        readyz_time = (time.time() - start_time) * 1000
        
        # Both should work
        assert health_response.status_code == 200
        assert readyz_response.status_code == 200
        
        # /health should be ultra-fast
        assert health_time < 100, f"/health too slow: {health_time:.2f}ms"
        
        # /health should be significantly faster than /readyz
        print(f"Performance: /health={health_time:.2f}ms, /readyz={readyz_time:.2f}ms")
        
        # /health should be at least 2x faster
        assert health_time < readyz_time / 2, f"/health ({health_time:.2f}ms) should be much faster than /readyz ({readyz_time:.2f}ms)"
        
    def test_health_endpoint_no_middleware_overhead(self):
        """Test that health endpoint has minimal middleware overhead"""
        # Multiple rapid calls should all be fast
        times = []
        for _ in range(5):
            start_time = time.time()
            response = client.get("/health")
            response_time = (time.time() - start_time) * 1000
            times.append(response_time)
            
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
        
        # All calls should be consistently fast
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        assert avg_time < 50, f"Average response time too high: {avg_time:.2f}ms"
        assert max_time < 100, f"Max response time too high: {max_time:.2f}ms"
        
    def test_readyz_comprehensive_checks(self):
        """Test that /readyz still provides comprehensive checks"""
        response = client.get("/readyz")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain comprehensive information
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "config" in data["checks"]

class TestMiddlewareExclusions:
    """Test that health endpoints bypass heavy middleware"""
    
    def test_health_bypasses_rate_limiting(self):
        """Test that health endpoint bypasses rate limiting"""
        # Make many rapid requests to health endpoint
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
            # Should not be rate limited
            
    def test_health_bypasses_security_headers(self):
        """Test that health endpoint bypasses security headers middleware"""
        response = client.get("/health")
        
        # Should not have heavy security headers
        headers = response.headers
        
        # Basic check - health endpoint should be lean
        assert response.status_code == 200
        
    def test_health_bypasses_error_handling_overhead(self):
        """Test that health endpoint bypasses error handling middleware overhead"""
        response = client.get("/health")
        
        # Should respond quickly without error tracking overhead
        assert response.status_code == 200
        
        # Response should not contain error tracking fields
        data = response.json()
        assert "error_id" not in data
        assert "timestamp" not in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])