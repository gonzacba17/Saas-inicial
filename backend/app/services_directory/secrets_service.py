"""
Secrets Management Service
Provides secure handling of secrets with multiple backend support
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecretsBackend(ABC):
    """Abstract base class for secrets backends"""
    
    @abstractmethod
    async def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get a secret by name"""
        pass
    
    @abstractmethod
    async def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set a secret"""
        pass
    
    @abstractmethod
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret"""
        pass
    
    @abstractmethod
    async def list_secrets(self) -> list[str]:
        """List all secret names"""
        pass


class EnvironmentSecretsBackend(SecretsBackend):
    """Environment variables backend for secrets (default/fallback)"""
    
    def __init__(self):
        self.prefix = "SAAS_SECRET_"
        logger.info("Using Environment Variables for secrets management")
    
    async def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get secret from environment variables"""
        try:
            env_key = f"{self.prefix}{secret_name.upper()}"
            value = os.getenv(env_key)
            if value:
                # Try to parse as JSON, fallback to string
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return {"value": value}
            return None
        except Exception as e:
            logger.error(f"Error getting secret {secret_name}: {e}")
            return None
    
    async def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set secret in environment (for current session only)"""
        try:
            env_key = f"{self.prefix}{secret_name.upper()}"
            os.environ[env_key] = json.dumps(secret_value)
            logger.info(f"Secret {secret_name} set in environment")
            return True
        except Exception as e:
            logger.error(f"Error setting secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from environment"""
        try:
            env_key = f"{self.prefix}{secret_name.upper()}"
            if env_key in os.environ:
                del os.environ[env_key]
                logger.info(f"Secret {secret_name} deleted from environment")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting secret {secret_name}: {e}")
            return False
    
    async def list_secrets(self) -> list[str]:
        """List all secrets in environment"""
        try:
            secrets = []
            for key in os.environ:
                if key.startswith(self.prefix):
                    secret_name = key[len(self.prefix):].lower()
                    secrets.append(secret_name)
            return secrets
        except Exception as e:
            logger.error(f"Error listing secrets: {e}")
            return []


class FileSecretsBackend(SecretsBackend):
    """File-based secrets backend for development"""
    
    def __init__(self, secrets_dir: str = "secrets"):
        self.secrets_dir = secrets_dir
        os.makedirs(secrets_dir, exist_ok=True)
        logger.info(f"Using File-based secrets management in {secrets_dir}/")
    
    def _get_secret_path(self, secret_name: str) -> str:
        """Get file path for secret"""
        return os.path.join(self.secrets_dir, f"{secret_name}.json")
    
    async def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get secret from file"""
        try:
            secret_path = self._get_secret_path(secret_name)
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error getting secret {secret_name}: {e}")
            return None
    
    async def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set secret in file"""
        try:
            secret_path = self._get_secret_path(secret_name)
            with open(secret_path, 'w') as f:
                json.dump(secret_value, f, indent=2)
            # Set restrictive permissions
            os.chmod(secret_path, 0o600)
            logger.info(f"Secret {secret_name} saved to file")
            return True
        except Exception as e:
            logger.error(f"Error setting secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret file"""
        try:
            secret_path = self._get_secret_path(secret_name)
            if os.path.exists(secret_path):
                os.remove(secret_path)
                logger.info(f"Secret {secret_name} deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting secret {secret_name}: {e}")
            return False
    
    async def list_secrets(self) -> list[str]:
        """List all secret files"""
        try:
            secrets = []
            for filename in os.listdir(self.secrets_dir):
                if filename.endswith('.json'):
                    secret_name = filename[:-5]  # Remove .json extension
                    secrets.append(secret_name)
            return secrets
        except Exception as e:
            logger.error(f"Error listing secrets: {e}")
            return []


class HashiCorpVaultBackend(SecretsBackend):
    """HashiCorp Vault backend for secrets (production)"""
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "secret"):
        self.vault_url = vault_url.rstrip('/')
        self.vault_token = vault_token
        self.mount_point = mount_point
        self.headers = {
            "X-Vault-Token": vault_token,
            "Content-Type": "application/json"
        }
        logger.info(f"Using HashiCorp Vault at {vault_url}")
    
    async def _make_request(self, method: str, path: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to Vault"""
        try:
            import aiohttp
            url = f"{self.vault_url}/v1/{self.mount_point}/data/{path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        logger.error(f"Vault request failed: {response.status}")
                        return None
        except ImportError:
            logger.error("aiohttp not installed - cannot use Vault backend")
            return None
        except Exception as e:
            logger.error(f"Vault request error: {e}")
            return None
    
    async def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get secret from Vault"""
        try:
            response = await self._make_request("GET", secret_name)
            if response and "data" in response and "data" in response["data"]:
                return response["data"]["data"]
            return None
        except Exception as e:
            logger.error(f"Error getting secret {secret_name} from Vault: {e}")
            return None
    
    async def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set secret in Vault"""
        try:
            data = {"data": secret_value}
            response = await self._make_request("POST", secret_name, data)
            if response:
                logger.info(f"Secret {secret_name} saved to Vault")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting secret {secret_name} in Vault: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Vault"""
        try:
            response = await self._make_request("DELETE", secret_name)
            if response is not None:
                logger.info(f"Secret {secret_name} deleted from Vault")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting secret {secret_name} from Vault: {e}")
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in Vault"""
        try:
            url = f"{self.vault_url}/v1/{self.mount_point}/metadata"
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method="LIST",
                    url=url,
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("keys", [])
                    return []
        except Exception as e:
            logger.error(f"Error listing secrets from Vault: {e}")
            return []


class AWSSecretsManagerBackend(SecretsBackend):
    """AWS Secrets Manager backend for secrets"""
    
    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        self.region = region
        self.profile = profile
        logger.info(f"Using AWS Secrets Manager in region {region}")
    
    async def _get_client(self):
        """Get AWS Secrets Manager client"""
        try:
            import boto3
            session = boto3.Session(profile_name=self.profile) if self.profile else boto3.Session()
            return session.client('secretsmanager', region_name=self.region)
        except ImportError:
            logger.error("boto3 not installed - cannot use AWS Secrets Manager")
            return None
        except Exception as e:
            logger.error(f"Error creating AWS client: {e}")
            return None
    
    async def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get secret from AWS Secrets Manager"""
        try:
            client = await self._get_client()
            if not client:
                return None
            
            response = client.get_secret_value(SecretId=secret_name)
            secret_string = response.get('SecretString')
            if secret_string:
                return json.loads(secret_string)
            return None
        except client.exceptions.ResourceNotFoundException:
            return None
        except Exception as e:
            logger.error(f"Error getting secret {secret_name} from AWS: {e}")
            return None
    
    async def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set secret in AWS Secrets Manager"""
        try:
            client = await self._get_client()
            if not client:
                return False
            
            secret_string = json.dumps(secret_value)
            
            try:
                # Try to update existing secret
                client.update_secret(
                    SecretId=secret_name,
                    SecretString=secret_string
                )
            except client.exceptions.ResourceNotFoundException:
                # Create new secret
                client.create_secret(
                    Name=secret_name,
                    SecretString=secret_string
                )
            
            logger.info(f"Secret {secret_name} saved to AWS Secrets Manager")
            return True
        except Exception as e:
            logger.error(f"Error setting secret {secret_name} in AWS: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            client = await self._get_client()
            if not client:
                return False
            
            client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True
            )
            logger.info(f"Secret {secret_name} deleted from AWS Secrets Manager")
            return True
        except Exception as e:
            logger.error(f"Error deleting secret {secret_name} from AWS: {e}")
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in AWS Secrets Manager"""
        try:
            client = await self._get_client()
            if not client:
                return []
            
            response = client.list_secrets()
            return [secret['Name'] for secret in response.get('SecretList', [])]
        except Exception as e:
            logger.error(f"Error listing secrets from AWS: {e}")
            return []


class SecretsManager:
    """Main secrets manager with multiple backend support"""
    
    def __init__(self):
        self.backend = self._initialize_backend()
    
    def _initialize_backend(self) -> SecretsBackend:
        """Initialize the appropriate secrets backend"""
        secrets_backend = os.getenv("SECRETS_BACKEND", "environment").lower()
        
        if secrets_backend == "vault":
            vault_url = os.getenv("VAULT_URL")
            vault_token = os.getenv("VAULT_TOKEN")
            if vault_url and vault_token:
                return HashiCorpVaultBackend(vault_url, vault_token)
        
        elif secrets_backend == "aws":
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            aws_profile = os.getenv("AWS_PROFILE")
            return AWSSecretsManagerBackend(aws_region, aws_profile)
        
        elif secrets_backend == "file":
            secrets_dir = os.getenv("SECRETS_DIR", "secrets")
            return FileSecretsBackend(secrets_dir)
        
        # Default to environment variables
        return EnvironmentSecretsBackend()
    
    async def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get a secret"""
        return await self.backend.get_secret(secret_name)
    
    async def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set a secret"""
        return await self.backend.set_secret(secret_name, secret_value)
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret"""
        return await self.backend.delete_secret(secret_name)
    
    async def list_secrets(self) -> list[str]:
        """List all secrets"""
        return await self.backend.list_secrets()
    
    async def get_secret_value(self, secret_name: str, key: str, default: Any = None) -> Any:
        """Get a specific value from a secret"""
        secret = await self.get_secret(secret_name)
        if secret:
            return secret.get(key, default)
        return default
    
    async def rotate_secret(self, secret_name: str, new_value: Dict[str, Any]) -> bool:
        """Rotate a secret (set new value)"""
        return await self.set_secret(secret_name, new_value)
    
    async def backup_secrets(self) -> Dict[str, Dict[str, Any]]:
        """Backup all secrets (for migration)"""
        try:
            secrets = {}
            secret_names = await self.list_secrets()
            
            for name in secret_names:
                secret = await self.get_secret(name)
                if secret:
                    secrets[name] = secret
            
            logger.info(f"Backed up {len(secrets)} secrets")
            return secrets
        except Exception as e:
            logger.error(f"Error backing up secrets: {e}")
            return {}
    
    async def restore_secrets(self, secrets: Dict[str, Dict[str, Any]]) -> bool:
        """Restore secrets from backup"""
        try:
            success_count = 0
            for name, value in secrets.items():
                if await self.set_secret(name, value):
                    success_count += 1
            
            logger.info(f"Restored {success_count}/{len(secrets)} secrets")
            return success_count == len(secrets)
        except Exception as e:
            logger.error(f"Error restoring secrets: {e}")
            return False


# Global secrets manager instance
secrets_manager = SecretsManager()


# Utility functions for common secrets
async def get_database_secret() -> Optional[Dict[str, Any]]:
    """Get database connection secrets"""
    return await secrets_manager.get_secret("database")


async def get_api_keys() -> Optional[Dict[str, Any]]:
    """Get external API keys"""
    return await secrets_manager.get_secret("api_keys")


async def get_jwt_secrets() -> Optional[Dict[str, Any]]:
    """Get JWT signing secrets"""
    return await secrets_manager.get_secret("jwt")


async def get_encryption_keys() -> Optional[Dict[str, Any]]:
    """Get encryption keys"""
    return await secrets_manager.get_secret("encryption")


# Context manager for secure secret operations
class SecureSecretContext:
    """Context manager for secure secret operations"""
    
    def __init__(self, secret_name: str):
        self.secret_name = secret_name
        self.secret = None
    
    async def __aenter__(self):
        self.secret = await secrets_manager.get_secret(self.secret_name)
        return self.secret
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clear secret from memory
        if self.secret:
            for key in list(self.secret.keys()):
                self.secret[key] = None
            self.secret.clear()
        self.secret = None


# Decorator for functions that need secrets
def requires_secret(secret_name: str, key: str = None):
    """Decorator that injects secrets into function"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            secret = await secrets_manager.get_secret(secret_name)
            if not secret:
                raise ValueError(f"Secret {secret_name} not found")
            
            if key:
                value = secret.get(key)
                if value is None:
                    raise ValueError(f"Key {key} not found in secret {secret_name}")
                kwargs['secret_value'] = value
            else:
                kwargs['secret'] = secret
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Export main interface
__all__ = [
    'secrets_manager',
    'get_database_secret',
    'get_api_keys', 
    'get_jwt_secrets',
    'get_encryption_keys',
    'SecureSecretContext',
    'requires_secret'
]