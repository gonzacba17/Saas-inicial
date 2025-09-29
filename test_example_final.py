"""
test_example.py - Tests de ejemplo usando la configuración de SQLite temporal
Compatible con pytest-asyncio 0.23.4 y pytest 7.x
"""
import pytest
import asyncio
from uuid import uuid4

class TestUserAPI:
    """Tests para la API de usuarios"""
    
    def test_create_user_success(self, client, sample_user_data):
        """Test básico de creación de usuario"""
        response = client.post("/users/", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["username"] == sample_user_data["username"]
        assert data["is_active"] is True
        assert "id" in data
    
    def test_get_user_success(self, client, created_user):
        """Test de obtener usuario por ID"""
        user_id = created_user["id"]
        
        response = client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == created_user["email"]
        assert data["username"] == created_user["username"]
    
    def test_get_user_not_found(self, client):
        """Test de usuario no encontrado"""
        fake_id = str(uuid4())
        
        response = client.get(f"/users/{fake_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "User not found"
    
    def test_list_users_empty(self, client):
        """Test de listar usuarios cuando no hay ninguno"""
        response = client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_users_with_data(self, client, created_user):
        """Test de listar usuarios con datos"""
        response = client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == created_user["id"]
    
    def test_multiple_users_creation(self, client, sample_user_data):
        """Test de creación de múltiples usuarios"""
        users = []
        
        # Crear 3 usuarios diferentes
        for i in range(3):
            unique_id = str(uuid4())[:8]
            user_data = {
                "email": f"user_{i}_{unique_id}@example.com",
                "username": f"user_{i}_{unique_id}",
                "password": f"Password{i}123!"
            }
            
            response = client.post("/users/", json=user_data)
            assert response.status_code == 200
            users.append(response.json())
        
        # Verificar que todos fueron creados
        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Verificar que cada usuario existe
        for user in users:
            found = any(u["id"] == user["id"] for u in data)
            assert found

class TestBusinessAPI:
    """Tests para la API de negocios"""
    
    def test_create_business_success(self, client, sample_business_data):
        """Test de creación de negocio"""
        response = client.post("/businesses/", json=sample_business_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_business_data["name"]
        assert data["description"] == sample_business_data["description"]
        assert data["is_active"] is True
        assert "id" in data
    
    def test_create_business_minimal_data(self, client):
        """Test de creación de negocio con datos mínimos"""
        business_data = {"name": "Minimal Business"}
        
        response = client.post("/businesses/", json=business_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Minimal Business"
        assert data["description"] == ""
        assert data["is_active"] is True

class TestDatabaseIntegrity:
    """Tests para verificar integridad de la base de datos"""
    
    def test_database_isolation_between_tests(self, client, db_session):
        """Test que verifica aislamiento entre tests"""
        # Este test no debería ver datos de tests anteriores
        users = db_session.query(User).all()
        assert len(users) == 0
        
        businesses = db_session.query(Business).all()
        assert len(businesses) == 0
    
    def test_database_session_rollback(self, client, db_session, sample_user_data):
        """Test que verifica rollback de sesión"""
        from conftest import User
        
        # Crear usuario directamente en la sesión
        user = User(
            email=sample_user_data["email"],
            username=sample_user_data["username"],
            hashed_password="test_hash"
        )
        db_session.add(user)
        # NO hacer commit
        
        # Verificar que el usuario no está visible desde la API
        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_concurrent_operations_simulation(self, client):
        """Test que simula operaciones concurrentes"""
        import threading
        import time
        
        results = {"success": 0, "failed": 0}
        
        def create_user(index):
            try:
                # Pequeña pausa para simular concurrencia
                time.sleep(0.01)
                
                user_data = {
                    "email": f"concurrent_{index}_{uuid4()}@example.com",
                    "username": f"concurrent_{index}_{uuid4()}",
                    "password": f"Password{index}!"
                }
                
                response = client.post("/users/", json=user_data)
                if response.status_code == 200:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception:
                results["failed"] += 1
        
        # Crear 5 usuarios concurrentemente
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen todos
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert results["success"] >= 4  # Al menos 4 de 5 deberían tener éxito
        
        # Verificar que los usuarios están en la base de datos
        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == results["success"]

class TestAsyncEndpoints:
    """Tests específicos para endpoints async"""
    
    @pytest.mark.asyncio
    async def test_async_endpoint_compatibility(self, client):
        """Test que verifica compatibilidad con pytest-asyncio"""
        # Simular trabajo async
        await asyncio.sleep(0.001)
        
        # Usar TestClient normalmente (no es async)
        response = client.get("/users/")
        assert response.status_code == 200
    
    def test_multiple_async_calls(self, client, sample_user_data):
        """Test de múltiples llamadas a endpoints async"""
        # Crear usuario
        response1 = client.post("/users/", json=sample_user_data)
        assert response1.status_code == 200
        user_id = response1.json()["id"]
        
        # Obtener usuario
        response2 = client.get(f"/users/{user_id}")
        assert response2.status_code == 200
        
        # Listar usuarios
        response3 = client.get("/users/")
        assert response3.status_code == 200
        
        # Verificar consistencia
        user_data = response2.json()
        users_list = response3.json()
        assert any(u["id"] == user_id for u in users_list)
        assert user_data["email"] == sample_user_data["email"]

# Importar modelos para usar en tests
from conftest import User, Business