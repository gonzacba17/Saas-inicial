"""
TEST QUE ANTES FALLABA - AHORA FUNCIONA
======================================
Ejemplo completo de test_register_user_success usando las nuevas fixtures
"""
import pytest

# 🧪 TESTS BÁSICOS QUE DEBEN FUNCIONAR

@pytest.mark.unit
@pytest.mark.fast
def test_health_check(client):
    """Test básico - verificar que el servidor responde."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.unit
@pytest.mark.auth
def test_register_user_success(client, test_user_data):
    """
    ❌ ANTES: Fallaba con httpx.ConnectError y timeout
    ✅ AHORA: Funciona con TestClient y SQLite temporal
    """
    # Registrar usuario usando TestClient (NO httpx/requests)
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    # Verificaciones
    assert response.status_code == 200, f"Error: {response.text}"
    
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data  # No debe devolver password
    assert data["is_active"] is True
    assert data["role"] == test_user_data["role"]

@pytest.mark.unit
@pytest.mark.auth
def test_register_duplicate_email(client, test_user_data):
    """Test registrar email duplicado."""
    # Primer registro
    response1 = client.post("/api/v1/auth/register", json=test_user_data)
    assert response1.status_code == 200
    
    # Segundo registro con mismo email (debe fallar)
    response2 = client.post("/api/v1/auth/register", json=test_user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()

@pytest.mark.unit
@pytest.mark.auth
def test_login_success(client, test_user_data):
    """Test login completo."""
    # 1. Registrar usuario
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 200
    
    # 2. Login
    login_response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    
    # 3. Verificar respuesta
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    assert "access_token" in token_data
    assert "token_type" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.unit
@pytest.mark.auth
def test_login_invalid_credentials(client, test_user_data):
    """Test login con credenciales inválidas."""
    # Registrar usuario
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Intentar login con password incorrecta
    response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["username"],
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]

@pytest.mark.unit
@pytest.mark.auth
def test_protected_endpoint_without_token(client):
    """Test endpoint protegido sin token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

@pytest.mark.unit
@pytest.mark.auth
def test_protected_endpoint_with_token(client, auth_headers):
    """Test endpoint protegido CON token válido."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    
    user_data = response.json()
    assert "email" in user_data
    assert "username" in user_data
    assert "id" in user_data

@pytest.mark.unit
@pytest.mark.business
def test_create_business(client, auth_headers, test_business_data):
    """Test crear negocio autenticado."""
    response = client.post(
        "/api/v1/businesses",
        json=test_business_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    business = response.json()
    assert business["name"] == test_business_data["name"]
    assert business["description"] == test_business_data["description"]
    assert "id" in business

@pytest.mark.unit
@pytest.mark.business
def test_create_business_unauthorized(client, test_business_data):
    """Test crear negocio sin autenticación."""
    response = client.post("/api/v1/businesses", json=test_business_data)
    assert response.status_code == 401

# 🧪 TEST DE PERFORMANCE

@pytest.mark.unit
@pytest.mark.fast
def test_multiple_operations_performance(client, test_user_data):
    """Test que múltiples operaciones no causen timeout."""
    # Registrar
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 200
    
    # Login
    login_response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Múltiples requests
    for i in range(5):
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
    
    # Health checks
    for i in range(10):
        response = client.get("/health")
        assert response.status_code == 200