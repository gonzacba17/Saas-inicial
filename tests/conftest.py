"""
Configuración de tests para pytest
"""
import os
import sys
import pytest
from pathlib import Path

# Set environment variables for testing
os.environ['USE_SQLITE'] = 'true'
os.environ['PYTHONPATH'] = 'backend'

# Add backend to Python path
project_root = Path(__file__).parent.parent
backend_path = project_root / 'backend'
sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database before running tests."""
    import subprocess
    
    # Create test database
    script_path = project_root / 'backend' / 'create_test_db.py'
    subprocess.run([sys.executable, str(script_path)], cwd=str(project_root))
    
    yield
    
    # Cleanup after tests
    db_path = project_root / 'saas_cafeterias.db'
    if db_path.exists():
        pass  # Keep for debugging, remove in production