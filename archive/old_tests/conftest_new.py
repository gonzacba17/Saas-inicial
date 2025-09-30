"""
conftest.py - Configuración completa para pytest con SQLite temporal y FastAPI
Compatible con pytest-asyncio 0.23.4 y pytest 7.x
"""
import os
import tempfile
import pytest
import asyncio
from pathlib import Path
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Float, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

# Configurar variables de entorno para tests
os.environ["TESTING"] = "true"
os.environ["USE_SQLITE"] = "true"

# Base para modelos
Base = declarative_base()

# Modelo de ejemplo
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# FastAPI app de ejemplo
app = FastAPI(title="Test API")

# Variable global para engine de test
_test_engine = None

def get_test_engine():
    """Crear engine de SQLite con archivo temporal para tests"""
    global _test_engine
    if _test_engine is not None:
        return _test_engine
    
    # Crear archivo temporal para SQLite
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_database.db"
    db_url = f"sqlite:///{db_path}"
    
    _test_engine = create_engine(
        db_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
            "isolation_level": None
        },
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # Configurar pragmas de SQLite para rendimiento y concurrencia
    @event.listens_for(_test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        # WAL mode para concurrencia
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        # Timeouts para evitar deadlocks
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()
    
    return _test_engine

def get_test_session():
    """Crear sesión de test"""
    engine = get_test_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = get_test_session()
    try:
        yield db
    finally:
        db.close()

# Endpoints de ejemplo
@app.post("/users/")
async def create_user(user_data: dict, db=Depends(get_db)):
    """Endpoint async de ejemplo para crear usuario"""
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=f"hashed_{user_data['password']}"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active
    }

@app.get("/users/{user_id}")
async def get_user(user_id: str, db=Depends(get_db)):
    """Endpoint async para obtener usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active
    }

@app.get("/users/")
async def list_users(db=Depends(get_db)):
    """Endpoint async para listar usuarios"""
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active
        }
        for user in users
    ]

@app.post("/businesses/")
async def create_business(business_data: dict, db=Depends(get_db)):
    """Endpoint async para crear negocio"""
    business = Business(
        name=business_data["name"],
        description=business_data.get("description", "")
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return {
        "id": business.id,
        "name": business.name,
        "description": business.description,
        "is_active": business.is_active
    }

# ============================================================================
# FIXTURES DE PYTEST
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Fixture de event loop para toda la sesión"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Configurar base de datos de test una vez por sesión"""
    engine = get_test_engine()
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Limpiar al final de la sesión
    try:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
    except Exception:
        pass

@pytest.fixture(scope="function")
def db_session():
    """Fixture de sesión de base de datos con scope de función"""
    engine = get_test_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        
        # Limpiar todas las tablas después de cada test
        try:
            with engine.begin() as conn:
                for table in reversed(Base.metadata.sorted_tables):
                    conn.execute(table.delete())
        except Exception:
            pass

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture de TestClient con override de dependencia"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Limpiar overrides anteriores y establecer el nuevo
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """Datos de usuario de ejemplo"""
    unique_id = str(uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "TestPassword123!"
    }

@pytest.fixture
def sample_business_data():
    """Datos de negocio de ejemplo"""
    unique_id = str(uuid4())[:8]
    return {
        "name": f"Test Business {unique_id}",
        "description": f"Test business description {unique_id}"
    }

@pytest.fixture
def created_user(client, sample_user_data):
    """Fixture que crea un usuario y retorna los datos"""
    response = client.post("/users/", json=sample_user_data)
    assert response.status_code == 200
    return response.json()

# ============================================================================
# UTILIDADES DE LIMPIEZA
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_between_tests():
    """Limpieza automática entre tests"""
    yield
    
    # Forzar garbage collection para limpiar conexiones
    import gc
    gc.collect()

def reset_test_database():
    """Función para resetear completamente la base de datos de test"""
    global _test_engine
    if _test_engine is not None:
        try:
            Base.metadata.drop_all(bind=_test_engine)
            Base.metadata.create_all(bind=_test_engine)
        except Exception:
            pass