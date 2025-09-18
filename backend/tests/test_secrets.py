"""
Tests for secrets management functionality
"""

import pytest
import asyncio
import os
import json
import tempfile
from app.services_directory.secrets_service import (
    SecretsManager, EnvironmentSecretsBackend, FileSecretsBackend
)


class TestEnvironmentSecretsBackend:
    """Test environment variables backend"""
    
    def setup_method(self):
        self.backend = EnvironmentSecretsBackend()
        # Clean up any existing test secrets
        for key in list(os.environ.keys()):
            if key.startswith("SAAS_SECRET_TEST"):
                del os.environ[key]
    
    @pytest.mark.asyncio
    async def test_set_and_get_secret(self):
        """Test setting and getting a secret"""
        secret_name = "test_secret"
        secret_value = {"key1": "value1", "key2": "value2"}
        
        # Set secret
        success = await self.backend.set_secret(secret_name, secret_value)
        assert success is True
        
        # Get secret
        retrieved = await self.backend.get_secret(secret_name)
        assert retrieved == secret_value
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_secret(self):
        """Test getting a secret that doesn't exist"""
        retrieved = await self.backend.get_secret("nonexistent")
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_delete_secret(self):
        """Test deleting a secret"""
        secret_name = "test_delete"
        secret_value = {"test": "value"}
        
        # Set and verify
        await self.backend.set_secret(secret_name, secret_value)
        assert await self.backend.get_secret(secret_name) == secret_value
        
        # Delete and verify
        success = await self.backend.delete_secret(secret_name)
        assert success is True
        assert await self.backend.get_secret(secret_name) is None
    
    @pytest.mark.asyncio
    async def test_list_secrets(self):
        """Test listing secrets"""
        # Set multiple secrets
        await self.backend.set_secret("test_list1", {"a": "1"})
        await self.backend.set_secret("test_list2", {"b": "2"})
        
        # List secrets
        secrets = await self.backend.list_secrets()
        assert "test_list1" in secrets
        assert "test_list2" in secrets
    
    @pytest.mark.asyncio
    async def test_string_value_handling(self):
        """Test handling of string values (not JSON)"""
        secret_name = "test_string"
        
        # Set a plain string in environment
        os.environ[f"SAAS_SECRET_{secret_name.upper()}"] = "plain_string_value"
        
        # Get secret should return wrapped in dict
        retrieved = await self.backend.get_secret(secret_name)
        assert retrieved == {"value": "plain_string_value"}


class TestFileSecretsBackend:
    """Test file-based backend"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backend = FileSecretsBackend(self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_set_and_get_secret(self):
        """Test setting and getting a secret from file"""
        secret_name = "test_file_secret"
        secret_value = {"database": "localhost", "port": 5432}
        
        # Set secret
        success = await self.backend.set_secret(secret_name, secret_value)
        assert success is True
        
        # Verify file exists
        secret_path = os.path.join(self.temp_dir, f"{secret_name}.json")
        assert os.path.exists(secret_path)
        
        # Check file permissions
        stat_info = os.stat(secret_path)
        assert oct(stat_info.st_mode)[-3:] == "600"  # Owner read/write only
        
        # Get secret
        retrieved = await self.backend.get_secret(secret_name)
        assert retrieved == secret_value
    
    @pytest.mark.asyncio
    async def test_update_secret(self):
        """Test updating an existing secret"""
        secret_name = "test_update"
        original_value = {"version": 1}
        updated_value = {"version": 2, "new_key": "new_value"}
        
        # Set original
        await self.backend.set_secret(secret_name, original_value)
        assert await self.backend.get_secret(secret_name) == original_value
        
        # Update
        await self.backend.set_secret(secret_name, updated_value)
        assert await self.backend.get_secret(secret_name) == updated_value
    
    @pytest.mark.asyncio
    async def test_delete_secret(self):
        """Test deleting a secret file"""
        secret_name = "test_delete_file"
        secret_value = {"to_delete": True}
        
        # Set and verify
        await self.backend.set_secret(secret_name, secret_value)
        secret_path = os.path.join(self.temp_dir, f"{secret_name}.json")
        assert os.path.exists(secret_path)
        
        # Delete and verify
        success = await self.backend.delete_secret(secret_name)
        assert success is True
        assert not os.path.exists(secret_path)
        assert await self.backend.get_secret(secret_name) is None
    
    @pytest.mark.asyncio
    async def test_list_secrets(self):
        """Test listing secret files"""
        # Create multiple secrets
        await self.backend.set_secret("secret1", {"a": 1})
        await self.backend.set_secret("secret2", {"b": 2})
        await self.backend.set_secret("secret3", {"c": 3})
        
        # List secrets
        secrets = await self.backend.list_secrets()
        assert len(secrets) == 3
        assert "secret1" in secrets
        assert "secret2" in secrets
        assert "secret3" in secrets
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(self):
        """Test handling of invalid JSON files"""
        secret_name = "invalid_json"
        secret_path = os.path.join(self.temp_dir, f"{secret_name}.json")
        
        # Create invalid JSON file
        with open(secret_path, 'w') as f:
            f.write("invalid json content {")
        
        # Should return None for invalid JSON
        retrieved = await self.backend.get_secret(secret_name)
        assert retrieved is None


class TestSecretsManager:
    """Test the main SecretsManager class"""
    
    def setup_method(self):
        # Use environment backend for testing
        os.environ["SECRETS_BACKEND"] = "environment"
        self.manager = SecretsManager()
        
        # Clean up any existing test secrets
        for key in list(os.environ.keys()):
            if key.startswith("SAAS_SECRET_TEST"):
                del os.environ[key]
    
    @pytest.mark.asyncio
    async def test_get_secret_value(self):
        """Test getting a specific value from a secret"""
        secret_name = "test_value_access"
        secret_data = {"username": "admin", "password": "secret123", "port": 5432}
        
        await self.manager.set_secret(secret_name, secret_data)
        
        # Test getting specific values
        username = await self.manager.get_secret_value(secret_name, "username")
        assert username == "admin"
        
        password = await self.manager.get_secret_value(secret_name, "password")
        assert password == "secret123"
        
        port = await self.manager.get_secret_value(secret_name, "port")
        assert port == 5432
        
        # Test getting non-existent key with default
        missing = await self.manager.get_secret_value(secret_name, "missing", "default")
        assert missing == "default"
    
    @pytest.mark.asyncio
    async def test_rotate_secret(self):
        """Test secret rotation"""
        secret_name = "test_rotation"
        original_data = {"api_key": "old_key", "version": 1}
        new_data = {"api_key": "new_key", "version": 2}
        
        # Set original secret
        await self.manager.set_secret(secret_name, original_data)
        assert await self.manager.get_secret(secret_name) == original_data
        
        # Rotate secret
        success = await self.manager.rotate_secret(secret_name, new_data)
        assert success is True
        assert await self.manager.get_secret(secret_name) == new_data
    
    @pytest.mark.asyncio
    async def test_backup_and_restore(self):
        """Test backup and restore functionality"""
        # Create multiple secrets
        secrets_data = {
            "test_backup1": {"key1": "value1"},
            "test_backup2": {"key2": "value2"},
            "test_backup3": {"key3": "value3"}
        }
        
        for name, data in secrets_data.items():
            await self.manager.set_secret(name, data)
        
        # Create backup
        backup = await self.manager.backup_secrets()
        assert len(backup) >= 3  # At least our test secrets
        
        for name, data in secrets_data.items():
            assert name in backup
            assert backup[name] == data
        
        # Delete original secrets
        for name in secrets_data.keys():
            await self.manager.delete_secret(name)
        
        # Verify secrets are deleted
        for name in secrets_data.keys():
            assert await self.manager.get_secret(name) is None
        
        # Restore from backup
        success = await self.manager.restore_secrets(backup)
        assert success is True
        
        # Verify restoration
        for name, data in secrets_data.items():
            restored = await self.manager.get_secret(name)
            assert restored == data


class TestSecretUtilities:
    """Test utility functions"""
    
    def setup_method(self):
        os.environ["SECRETS_BACKEND"] = "environment"
        from app.services_directory.secrets_service import secrets_manager
        self.manager = secrets_manager
    
    @pytest.mark.asyncio
    async def test_utility_functions(self):
        """Test utility functions for common secrets"""
        from app.services_directory.secrets_service import (
            get_database_secret, get_api_keys, get_jwt_secrets
        )
        
        # Set up test secrets
        await self.manager.set_secret("database", {
            "host": "localhost",
            "port": "5432",
            "user": "testuser"
        })
        
        await self.manager.set_secret("api_keys", {
            "openai": "sk-test123",
            "mercadopago": "MP-test456"
        })
        
        await self.manager.set_secret("jwt", {
            "secret_key": "test-jwt-secret",
            "algorithm": "HS256"
        })
        
        # Test utility functions
        db_secret = await get_database_secret()
        assert db_secret["host"] == "localhost"
        assert db_secret["port"] == "5432"
        
        api_keys = await get_api_keys()
        assert api_keys["openai"] == "sk-test123"
        assert api_keys["mercadopago"] == "MP-test456"
        
        jwt_secret = await get_jwt_secrets()
        assert jwt_secret["secret_key"] == "test-jwt-secret"
        assert jwt_secret["algorithm"] == "HS256"


class TestSecureSecretContext:
    """Test secure secret context manager"""
    
    def setup_method(self):
        os.environ["SECRETS_BACKEND"] = "environment"
        from app.services_directory.secrets_service import secrets_manager
        self.manager = secrets_manager
    
    @pytest.mark.asyncio
    async def test_secure_context(self):
        """Test secure secret context manager"""
        from app.services_directory.secrets_service import SecureSecretContext
        
        secret_name = "test_secure_context"
        secret_data = {"sensitive": "data"}
        
        await self.manager.set_secret(secret_name, secret_data)
        
        # Test context manager
        async with SecureSecretContext(secret_name) as secret:
            assert secret is not None
            assert secret["sensitive"] == "data"
            
        # After context, secret reference should be cleared
        # (This is mainly for security, hard to test the memory clearing)


class TestRequiresSecretDecorator:
    """Test the requires_secret decorator"""
    
    def setup_method(self):
        os.environ["SECRETS_BACKEND"] = "environment"
        from app.services_directory.secrets_service import secrets_manager
        self.manager = secrets_manager
    
    @pytest.mark.asyncio
    async def test_requires_secret_decorator(self):
        """Test the requires_secret decorator"""
        from app.services_directory.secrets_service import requires_secret
        
        # Set up test secret
        await self.manager.set_secret("test_decorator", {
            "api_key": "secret123",
            "timeout": 30
        })
        
        @requires_secret("test_decorator", "api_key")
        async def function_with_secret(secret_value):
            return f"API Key: {secret_value}"
        
        @requires_secret("test_decorator")
        async def function_with_full_secret(secret):
            return f"Timeout: {secret['timeout']}"
        
        # Test with specific key
        result1 = await function_with_secret()
        assert result1 == "API Key: secret123"
        
        # Test with full secret
        result2 = await function_with_full_secret()
        assert result2 == "Timeout: 30"
        
        # Test with missing secret
        @requires_secret("nonexistent")
        async def function_with_missing_secret(secret):
            return secret
        
        with pytest.raises(ValueError, match="Secret nonexistent not found"):
            await function_with_missing_secret()


if __name__ == "__main__":
    pytest.main([__file__])