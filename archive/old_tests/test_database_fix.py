#!/usr/bin/env python3
"""
Test script to verify the PostgreSQL Unicode connection fix.
This script tests the specific configuration with your credentials.
"""
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment_loading():
    """Test that environment variables are loaded correctly."""
    logger.info("=== Testing Environment Variable Loading ===")
    
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file, encoding='utf-8')
            logger.info(f"✅ Loaded .env file: {env_file.absolute()}")
        else:
            logger.warning("❌ .env file not found")
            return False
    except ImportError:
        logger.error("❌ python-dotenv not installed")
        return False
    
    # Check your specific credentials
    expected_values = {
        'POSTGRES_USER': 'postgresql',
        'POSTGRES_PASSWORD': 'mapuchito17',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'testdb'
    }
    
    all_good = True
    for key, expected in expected_values.items():
        actual = os.getenv(key)
        if actual == expected:
            logger.info(f"✅ {key}: {actual}")
        else:
            logger.error(f"❌ {key}: expected '{expected}', got '{actual}'")
            all_good = False
    
    return all_good

def test_url_encoding():
    """Test URL encoding of database credentials."""
    logger.info("=== Testing URL Encoding ===")
    
    try:
        import urllib.parse
        
        # Test encoding your specific password
        password = "mapuchito17"
        encoded = urllib.parse.quote_plus(password)
        logger.info(f"✅ Password encoding: '{password}' -> '{encoded}'")
        
        # Test other characters that could cause issues
        test_cases = [
            ("postgresql", "postgresql"),
            ("mapuchito17", "mapuchito17"),
            ("localhost", "localhost"),
            ("testdb", "testdb"),
            ("test@password", "test%40password"),
            ("test#password", "test%23password"),
            ("contraseña", "contrase%C3%B1a")
        ]
        
        for original, expected_encoded in test_cases:
            actual_encoded = urllib.parse.quote_plus(original)
            if actual_encoded == expected_encoded:
                logger.info(f"✅ Encoding '{original}' -> '{actual_encoded}'")
            else:
                logger.warning(f"⚠️  Encoding '{original}': expected '{expected_encoded}', got '{actual_encoded}'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ URL encoding test failed: {e}")
        return False

def test_database_connection():
    """Test the actual database connection."""
    logger.info("=== Testing Database Connection ===")
    
    # Add backend to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    
    try:
        # Import our fixed database module
        from app.db.db import create_database_engine
        
        logger.info("✅ Successfully imported database module")
        
        # Test engine creation
        logger.info("Creating database engine...")
        engine = create_database_engine()
        logger.info("✅ Database engine created successfully")
        
        # Test connection
        logger.info("Testing database connection...")
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, 'Hello UTF-8: ñáéíóú' as message"))
            row = result.fetchone()
            logger.info(f"✅ Connection test successful: {row.test}, {row.message}")
        
        # Test with special characters
        logger.info("Testing UTF-8 character handling...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'Café español con niños' as test_utf8"))
            row = result.fetchone()
            logger.info(f"✅ UTF-8 test successful: {row.test_utf8}")
        
        engine.dispose()
        logger.info("✅ Database connection test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        
        # Provide specific guidance
        error_str = str(e).lower()
        if "connection refused" in error_str:
            logger.error("💡 PostgreSQL server might not be running")
            logger.error("   Try: net start postgresql (Windows) or sudo service postgresql start (Linux)")
        elif "authentication failed" in error_str:
            logger.error("💡 Authentication failed - check username/password")
        elif "database" in error_str and "does not exist" in error_str:
            logger.error("💡 Database 'testdb' does not exist")
            logger.error("   Create it with: createdb testdb")
        elif "codec can't decode" in error_str or "invalid continuation byte" in error_str:
            logger.error("💡 Unicode encoding error - this should be fixed now!")
        
        return False

def test_sqlite_fallback():
    """Test SQLite fallback functionality."""
    logger.info("=== Testing SQLite Fallback ===")
    
    # Set SQLite mode
    os.environ['USE_SQLITE'] = 'true'
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
        from app.db.db import create_database_engine
        
        logger.info("Testing SQLite fallback...")
        engine = create_database_engine()
        
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            logger.info(f"✅ SQLite fallback successful: {row.test}")
        
        engine.dispose()
        # Reset PostgreSQL mode
        os.environ['USE_SQLITE'] = 'false'
        return True
        
    except Exception as e:
        logger.error(f"❌ SQLite fallback failed: {e}")
        os.environ['USE_SQLITE'] = 'false'
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting PostgreSQL Unicode Connection Fix Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Environment Loading", test_environment_loading),
        ("URL Encoding", test_url_encoding),
        ("SQLite Fallback", test_sqlite_fallback),
        ("PostgreSQL Connection", test_database_connection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} Test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Your PostgreSQL Unicode connection issue is fixed!")
        logger.info("\n💡 Next steps:")
        logger.info("   1. Make sure PostgreSQL is running")
        logger.info("   2. Create the 'testdb' database if needed: createdb testdb")
        logger.info("   3. Run your tests: pytest")
    else:
        logger.error("\n❌ Some tests failed. Check the errors above.")
        if not results.get("Environment Loading", False):
            logger.error("   🔧 Fix: Check your .env file exists and has correct values")
        if not results.get("PostgreSQL Connection", False):
            logger.error("   🔧 Fix: Start PostgreSQL and ensure database exists")
            logger.error("   🔧 Alternative: Use SQLite for testing: export USE_SQLITE=true")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)