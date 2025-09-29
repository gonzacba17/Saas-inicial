"""
test_fixed_example.py - Tests sin colgamientos usando SQLite temporal
"""
import pytest
from uuid import uuid4

class TestUserAPIFixed:
    """Tests para la API de usuarios sin problemas de colgamiento"""
    
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
    
    def test_multiple_users_creation(self, client):
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

class TestDatabaseIsolation:
    """Tests para verificar aislamiento de base de datos"""
    
    def test_isolation_between_tests(self, client, db_session):
        """Test que verifica que cada test empieza limpio"""
        from conftest_fixed import User
        
        # Este test no debería ver datos de tests anteriores
        users = db_session.query(User).all()
        assert len(users) == 0
    
    def test_isolation_verification(self, client, db_session):
        """Segundo test para verificar aislamiento"""
        from conftest_fixed import User
        
        # Este test tampoco debería ver datos
        users = db_session.query(User).all()
        assert len(users) == 0
        
        # Crear un usuario
        user = User(
            email="isolation@test.com",
            username="isolation_user",
            hashed_password="test_hash"
        )
        db_session.add(user)
        db_session.commit()
        
        # Verificar que se creó
        users = db_session.query(User).all()
        assert len(users) == 1

class TestAsyncEndpoints:
    """Tests específicos para endpoints async"""
    
    def test_async_create_and_retrieve(self, client, sample_user_data):
        """Test completo de crear y recuperar usuario async"""
        # 1. Crear usuario
        create_response = client.post("/users/", json=sample_user_data)
        assert create_response.status_code == 200
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # 2. Obtener usuario individual
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        assert retrieved_user["email"] == sample_user_data["email"]
        assert retrieved_user["username"] == sample_user_data["username"]
        
        # 3. Listar todos los usuarios
        list_response = client.get("/users/")
        assert list_response.status_code == 200
        users_list = list_response.json()
        assert len(users_list) == 1
        assert users_list[0]["id"] == user_id
    
    def test_concurrent_user_creation(self, client):
        """Test de creación concurrente de usuarios"""
        import threading
        import time
        
        results = {"success": 0, "failed": 0}
        
        def create_user(index):
            try:
                unique_id = str(uuid4())[:8]
                user_data = {
                    "email": f"concurrent_{index}_{unique_id}@example.com",
                    "username": f"concurrent_{index}_{unique_id}",
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
        assert results["success"] >= 4  # Al menos 4 de 5 deberían funcionar
        
        # Verificar en base de datos
        response = client.get("/users/")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == results["success"]

class TestDatabaseConfiguration:
    """Tests para verificar configuración de base de datos"""
    
    def test_database_pragmas(self, engine):
        """Test que verifica que los pragmas SQLite están correctos"""
        with engine.connect() as conn:
            # Verificar WAL mode
            result = conn.execute("PRAGMA journal_mode").fetchone()
            assert result[0].upper() == "WAL"
            
            # Verificar foreign keys
            result = conn.execute("PRAGMA foreign_keys").fetchone()
            assert result[0] == 1
    
    def test_database_file_exists(self, engine):
        """Test que verifica que se usa archivo temporal (no :memory:)"""
        # El engine debería estar conectado a un archivo, no a :memory:
        url = str(engine.url)
        assert ":memory:" not in url
        assert ".db" in url

# Importar modelos necesarios
from conftest_fixed import User