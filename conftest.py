"""
conftest.py - Configuración de tests sin colgamientos
Usa SQLite temporal (no :memory:) con WAL mode y pooling optimizado
"""
import os
import tempfile
import pytest
from pathlib import Path
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

# Configurar variables antes de cualquier import
os.environ["TESTING"] = "true"
os.environ["USE_SQLITE"] = "true"

# Base para modelos
Base = declarative_base()

# Modelo de ejemplo simple
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Variables globales para engine y archivo temporal
_test_engine = None
_temp_db_file = None

def create_test_engine():
    """Crear engine de SQLite con archivo temporal y configuración anti-bloqueo"""
    global _test_engine, _temp_db_file
    
    if _test_engine is not None:
        return _test_engine
    
    # Crear archivo temporal para SQLite
    temp_fd, _temp_db_file = tempfile.mkstemp(suffix='.db', prefix='test_')
    os.close(temp_fd)  # Cerrar el descriptor, solo necesitamos el path
    
    db_url = f"sqlite:///{_temp_db_file}"
    
    # Engine con configuración anti-bloqueo
    _test_engine = create_engine(
        db_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 20,
            "isolation_level": None  # Autocommit mode
        },
        poolclass=StaticPool,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
    
    # Configurar pragmas SQLite para WAL mode y foreign keys
    @event.listens_for(_test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        # WAL mode para concurrencia
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        # Foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        # Timeouts anti-deadlock
        cursor.execute("PRAGMA busy_timeout=20000")
        cursor.close()
    
    return _test_engine

def cleanup_test_engine():
    """Limpiar engine y archivo temporal"""
    global _test_engine, _temp_db_file
    
    if _test_engine is not None:
        _test_engine.dispose()
        _test_engine = None
    
    if _temp_db_file and os.path.exists(_temp_db_file):
        try:
            os.unlink(_temp_db_file)
        except (OSError, PermissionError):
            pass
        _temp_db_file = None

# FastAPI app de ejemplo
app = FastAPI(title="Test API")

# Dependency para obtener sesión de DB
def get_db():
    """Dependency original - será override en tests"""
    pass

# Endpoints de ejemplo
@app.post("/users/")
async def create_user(user_data: dict, db=Depends(get_db)):
    """Endpoint async para crear usuario"""
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

# ============================================================================
# FIXTURES DE PYTEST
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Configurar base de datos de test una vez por sesión"""
    # Crear engine y tablas
    engine = create_test_engine()
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup al final de la sesión
    cleanup_test_engine()

@pytest.fixture(scope="session")
def engine(setup_test_database):
    """Fixture de engine para toda la sesión"""
    return setup_test_database

@pytest.fixture(scope="session")
def SessionLocal(engine):
    """Fixture de SessionLocal para toda la sesión"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session(SessionLocal, engine):
    """Fixture de sesión de base de datos con scope de función"""
    session = SessionLocal()
    
    # Usar transacción que se puede rollback
    connection = engine.connect()
    transaction = connection.begin()
    session.bind = connection
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        
        # Limpiar todas las tablas como backup
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
        """Override que retorna la sesión de test"""
        try:
            yield db_session
        finally:
            pass
    
    # Configurar override
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Limpiar overrides
        app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """Datos de usuario de ejemplo únicos"""
    unique_id = str(uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "TestPassword123!"
    }

@pytest.fixture
def created_user(client, sample_user_data):
    """Fixture que crea un usuario y retorna los datos"""
    response = client.post("/users/", json=sample_user_data)
    assert response.status_code == 200
    return response.json()

# ============================================================================
# UTILIDADES Y LIMPIEZA
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_between_tests():
    """Limpieza automática entre tests"""
    yield
    
    # Forzar garbage collection
    import gc
    gc.collect()

def clear_all_tables(engine):
    """Utility para limpiar todas las tablas"""
    try:
        with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(table.delete())
    except Exception:
        pass