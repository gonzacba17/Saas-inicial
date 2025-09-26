#!/usr/bin/env python3
"""
Health endpoints tests - validating optimized /health and comprehensive /readyz
"""
import pytest
import time
import httpx
from fastapi.testclient import TestClient

def test_health_endpoint_performance():
    """Test that /health endpoint responds in <100ms"""
    with httpx.Client(base_url="http://localhost:8000", timeout=5.0) as client:
        start_time = time.time()
        response = client.get("/health")
        response_time_ms = (time.time() - start_time) * 1000
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data
        
        # Verify performance (<100ms)
        assert response_time_ms < 100, f"Health endpoint too slow: {response_time_ms:.2f}ms"

def test_health_endpoint_no_dependencies():
    """Test that /health endpoint doesn't depend on database or external services"""
    with httpx.Client(base_url="http://localhost:8000", timeout=5.0) as client:
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not contain database status
        assert "db" not in data
        assert "database" not in data
        assert "checks" not in data
        
        # Should be simple and fast
        assert data["status"] == "ok"
        assert data["service"] == "saas-cafeterias"

def test_readyz_endpoint_comprehensive():
    """Test that /readyz endpoint provides comprehensive checks"""
    with httpx.Client(base_url="http://localhost:8000", timeout=10.0) as client:
        response = client.get("/readyz")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain comprehensive checks
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "checks" in data
        
        # Should have database check
        assert "database" in data["checks"]
        assert "config" in data["checks"]
        
        # Database check should have status
        db_check = data["checks"]["database"]
        assert "status" in db_check
        assert db_check["status"] in ["ok", "error"]

def test_legacy_health_db_endpoint():
    """Test that legacy /health/db endpoint still works but shows deprecation"""
    with httpx.Client(base_url="http://localhost:8000", timeout=5.0) as client:
        response = client.get("/health/db")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain deprecation notice
        assert "deprecated" in data
        assert "Use /readyz instead" in data["deprecated"]
        
        # Should still provide basic db status
        assert "status" in data
        assert "db" in data

def test_health_endpoints_comparison():
    """Test performance comparison between /health and /readyz"""
    with httpx.Client(base_url="http://localhost:8000", timeout=10.0) as client:
        
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
        
        # /health should be significantly faster
        assert health_time < 100, f"/health too slow: {health_time:.2f}ms"
        
        # /readyz can be slower but should be reasonable
        assert readyz_time < 1000, f"/readyz too slow: {readyz_time:.2f}ms"
        
        # /health should be faster than /readyz
        assert health_time < readyz_time, f"/health ({health_time:.2f}ms) should be faster than /readyz ({readyz_time:.2f}ms)"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])