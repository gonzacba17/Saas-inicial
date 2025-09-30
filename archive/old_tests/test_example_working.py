"""
TEST DE EJEMPLO - FUNCIONA CON LA NUEVA CONFIGURACIÓN
====================================================
"""
import pytest

def test_health_check(client):
    """Test básico que debe funcionar."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_user_registration(client, test_user_data):
    """Test de registro de usuario."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert "id" in data

def test_user_login(client, test_user_data):
    """Test de login completo."""
    # 1. Registrar usuario
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # 2. Login
    response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint(client, auth_headers):
    """Test endpoint protegido."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()

def test_business_creation(client, auth_headers):
    """Test creación de negocio."""
    business_data = {
        "name": "Test Business",
        "description": "A test business",
        "business_type": "restaurant"
    }
    
    response = client.post(
        "/api/v1/businesses", 
        json=business_data, 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Test Business"