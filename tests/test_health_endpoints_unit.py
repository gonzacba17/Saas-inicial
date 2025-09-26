#!/usr/bin/env python3
"""
Health endpoints unit tests using FastAPI TestClient
"""
import pytest
import time
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint_performance():
    """Test that /health endpoint responds in <100ms"""
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
    
    # /health should be faster than /readyz (unless DB is super fast)
    print(f"Performance: /health={health_time:.2f}ms, /readyz={readyz_time:.2f}ms")

def test_health_endpoint_content():
    """Test health endpoint returns expected content structure"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert data["status"] == "ok"
    assert data["service"] == "saas-cafeterias"
    assert "version" in data
    
    # Ensure no heavy computations
    assert len(data) <= 5  # Keep response minimal

def test_readyz_endpoint_detailed_checks():
    """Test readyz endpoint provides detailed status checks"""
    response = client.get("/readyz")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check overall structure
    assert data["service"] == "saas-cafeterias"
    assert data["status"] in ["ok", "degraded"]
    
    # Check database check details
    db_check = data["checks"]["database"]
    if db_check["status"] == "ok":
        assert "response_time_ms" in db_check
    else:
        assert "error" in db_check
    
    # Check config check
    config_check = data["checks"]["config"]
    assert config_check["status"] == "ok"
    assert "environment" in config_check
    assert "debug" in config_check

if __name__ == "__main__":
    pytest.main([__file__, "-v"])