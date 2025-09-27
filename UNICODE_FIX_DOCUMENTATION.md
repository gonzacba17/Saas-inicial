# PostgreSQL Unicode Connection Error Fix

This document describes the complete solution for fixing the `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 85: invalid continuation byte` error in the FastAPI test suite.

## Problem Description

The error occurred when:
- Database credentials contained special characters (e.g., ñ, á, @, #)
- Environment variables weren't properly URL-encoded
- Windows system locale settings interfered with UTF-8 encoding
- SQLAlchemy connection wasn't configured for UTF-8

## Complete Solution Implemented

### 1. Database Configuration Fix (`backend/app/db/db.py`)

**Key Changes:**
- Added lazy database engine creation to avoid connection issues during import
- Implemented proper UTF-8 encoding for PostgreSQL connections
- Added connection retry logic and detailed error handling
- Configured connection pooling with UTF-8 client encoding

**Important Features:**
```python
# PostgreSQL specific configuration with UTF-8
connect_args={
    "client_encoding": "utf8",
    "options": "-c client_encoding=utf8"
}
```

### 2. Enhanced Configuration (`backend/app/core/config.py`)

**Key Improvements:**
- Automatic URL encoding of all database credentials
- UTF-8 parameter injection for PostgreSQL URLs
- Comprehensive error handling for encoding issues
- Support for both individual credentials and DATABASE_URL

**URL Encoding Examples:**
- `contraseña` → `contrase%C3%B1a`
- `pass@word` → `pass%40word`
- `user#123` → `user%23123`

### 3. Test Configuration Updates (`tests/conftest.py`)

**Features Added:**
- Support for PostgreSQL integration tests with proper UTF-8 encoding
- Automatic fallback to SQLite for development
- Environment variable controls for test database selection
- Proper cleanup and connection management

**Usage:**
```bash
# Use PostgreSQL for tests
export USE_POSTGRES_TESTS=true

# Use SQLite for tests (default)
export USE_POSTGRES_TESTS=false
```

### 4. Environment Variable Examples (`.env.example`)

**Updated with:**
- Clear documentation for special character handling
- URL encoding examples and best practices
- Test database configuration options
- Multiple methods for setting database credentials

### 5. pytest Configuration (`pytest.ini`)

**UTF-8 Settings:**
- Documented required environment variables for Windows
- Configured console output for proper UTF-8 display
- Added encoding-related test markers

### 6. Windows-Specific Support

**Created Tools:**
- `scripts/setup_windows_utf8.bat` - Automated Windows UTF-8 setup
- `scripts/test_database_connection.py` - Comprehensive connection testing

## How to Use

### For Development

1. **Set up environment variables:**
   ```bash
   # For special characters in passwords
   export POSTGRES_PASSWORD="contraseña"
   # Or use URL-encoded version
   export DATABASE_URL="postgresql://user:contrase%C3%B1a@localhost:5432/db"
   ```

2. **Run the connection test:**
   ```bash
   python scripts/test_database_connection.py
   ```

3. **For Windows users:**
   ```cmd
   # Run as Administrator
   scripts\setup_windows_utf8.bat
   ```

### For Testing

1. **SQLite tests (default):**
   ```bash
   pytest
   ```

2. **PostgreSQL integration tests:**
   ```bash
   export USE_POSTGRES_TESTS=true
   export POSTGRES_TEST_USER=postgres
   export POSTGRES_TEST_PASSWORD=postgres
   pytest
   ```

### For Production

1. **Set DATABASE_URL with proper encoding:**
   ```bash
   DATABASE_URL=postgresql://user:encoded_password@host:5432/db?client_encoding=utf8
   ```

2. **Or use individual variables (auto-encoded):**
   ```bash
   POSTGRES_USER=myuser
   POSTGRES_PASSWORD=contraseña
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=mydb
   ```

## Troubleshooting

### Common Issues and Solutions

1. **"codec can't decode" error:**
   - Check for special characters in POSTGRES_PASSWORD
   - Use URL encoding: `ñ` → `%C3%B1`, `@` → `%40`
   - Run `python scripts/test_database_connection.py` for diagnosis

2. **"invalid connection option 'charset'" error:**
   - Fixed: Removed unsupported `charset` parameter
   - Using only `client_encoding=utf8` for PostgreSQL

3. **Connection refused:**
   - Ensure PostgreSQL is running
   - Check host, port, and credentials
   - Verify firewall settings

4. **Import errors during testing:**
   - Fixed: Implemented lazy database engine creation
   - Engine only connects when actually used, not during import

### Verification Commands

```bash
# Test environment setup
python scripts/test_database_connection.py

# Test with SQLite
export USE_SQLITE=true
pytest tests/test_database.py

# Test with PostgreSQL (if available)
export USE_POSTGRES_TESTS=true
pytest tests/test_database.py

# Test specific encoding scenarios
python -c "
from urllib.parse import quote_plus
print('contraseña ->', quote_plus('contraseña'))
print('pass@word ->', quote_plus('pass@word'))
"
```

## Files Modified

1. `backend/app/db/db.py` - Database engine and connection handling
2. `backend/app/core/config.py` - Configuration and URL building
3. `tests/conftest.py` - Test database setup
4. `.env.example` - Environment variable examples
5. `pytest.ini` - Test configuration
6. `scripts/setup_windows_utf8.bat` - Windows setup script
7. `scripts/test_database_connection.py` - Connection testing utility

## Testing Results

✅ **Environment Setup**: UTF-8 encoding properly configured  
✅ **URL Encoding**: Special characters correctly encoded  
✅ **Database Connection**: Engine creation works with proper encoding  
✅ **Special Characters**: Unicode strings handled correctly  
✅ **Cross-Platform**: Works on both Linux and Windows  

The Unicode connection error has been completely resolved. The application now properly handles:
- Special characters in database credentials
- UTF-8 encoding in connection strings
- Cross-platform compatibility
- Both development and production environments
- Comprehensive testing with proper encoding

## Security Notes

- Passwords are automatically URL-encoded to prevent injection
- Connection parameters are validated and sanitized
- Error messages don't expose sensitive credential information
- Test databases use isolated credentials