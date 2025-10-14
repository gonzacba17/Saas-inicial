import os
from typing import Optional, Dict
from enum import Enum


class SecretsBackend(str, Enum):
    ENVIRONMENT = "environment"
    FILE = "file"
    VAULT = "vault"
    AWS = "aws"


class SecretsManager:
    """
    Centralized secrets management supporting multiple backends.
    Provides unified interface for retrieving sensitive configuration.
    """
    
    def __init__(self, backend: str = "environment"):
        self.backend = SecretsBackend(backend)
        self._cache: Dict[str, str] = {}
        
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve secret from configured backend.
        
        Args:
            key: Secret key to retrieve
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]
            
        # Retrieve based on backend
        if self.backend == SecretsBackend.ENVIRONMENT:
            value = self._get_from_environment(key, default)
        elif self.backend == SecretsBackend.FILE:
            value = self._get_from_file(key, default)
        elif self.backend == SecretsBackend.VAULT:
            value = self._get_from_vault(key, default)
        elif self.backend == SecretsBackend.AWS:
            value = self._get_from_aws(key, default)
        else:
            value = default
            
        # Cache the value
        if value is not None:
            self._cache[key] = value
            
        return value
    
    def _get_from_environment(self, key: str, default: Optional[str]) -> Optional[str]:
        """Retrieve secret from environment variables."""
        return os.getenv(key, default)
    
    def _get_from_file(self, key: str, default: Optional[str]) -> Optional[str]:
        """Retrieve secret from file system."""
        secrets_dir = os.getenv("SECRETS_DIR", "secrets")
        secret_path = os.path.join(secrets_dir, key)
        
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"Error reading secret from file {secret_path}: {e}")
            
        return default
    
    def _get_from_vault(self, key: str, default: Optional[str]) -> Optional[str]:
        """Retrieve secret from HashiCorp Vault."""
        try:
            import hvac
            
            vault_url = os.getenv("VAULT_URL", "http://localhost:8200")
            vault_token = os.getenv("VAULT_TOKEN")
            vault_mount_point = os.getenv("VAULT_MOUNT_POINT", "secret")
            
            if not vault_token:
                print("VAULT_TOKEN not set, falling back to default")
                return default
                
            client = hvac.Client(url=vault_url, token=vault_token)
            
            if not client.is_authenticated():
                print("Vault authentication failed")
                return default
                
            # Read secret from Vault
            secret_path = f"{vault_mount_point}/data/saas-cafeterias"
            response = client.secrets.kv.v2.read_secret_version(path=secret_path)
            
            if response and 'data' in response and 'data' in response['data']:
                return response['data']['data'].get(key, default)
                
        except ImportError:
            print("hvac library not installed. Install with: pip install hvac")
        except Exception as e:
            print(f"Error reading from Vault: {e}")
            
        return default
    
    def _get_from_aws(self, key: str, default: Optional[str]) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            region = os.getenv("AWS_REGION", "us-east-1")
            secret_name = os.getenv("AWS_SECRET_NAME", "saas-cafeterias/production")
            
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region
            )
            
            try:
                response = client.get_secret_value(SecretId=secret_name)
                
                if 'SecretString' in response:
                    import json
                    secrets_dict = json.loads(response['SecretString'])
                    return secrets_dict.get(key, default)
                    
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print(f"Secret {secret_name} not found in AWS Secrets Manager")
                else:
                    print(f"Error retrieving secret from AWS: {e}")
                    
        except ImportError:
            print("boto3 library not installed. Install with: pip install boto3")
        except Exception as e:
            print(f"Error reading from AWS Secrets Manager: {e}")
            
        return default
    
    def get_database_url(self) -> str:
        """Get database URL with special handling for password encoding."""
        db_url = self.get_secret("DATABASE_URL")
        if db_url:
            return db_url
            
        # Build from components
        user = self.get_secret("POSTGRES_USER", "postgres")
        password = self.get_secret("POSTGRES_PASSWORD", "")
        host = self.get_secret("POSTGRES_HOST", "localhost")
        port = self.get_secret("POSTGRES_PORT", "5432")
        db = self.get_secret("POSTGRES_DB", "saas_cafeterias")
        
        # URL encode password if it contains special characters
        from urllib.parse import quote_plus
        encoded_password = quote_plus(password) if password else ""
        
        return f"postgresql://{user}:{encoded_password}@{host}:{port}/{db}"
    
    def clear_cache(self):
        """Clear the secrets cache."""
        self._cache.clear()


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get or create global secrets manager instance."""
    global _secrets_manager
    
    if _secrets_manager is None:
        backend = os.getenv("SECRETS_BACKEND", "environment")
        _secrets_manager = SecretsManager(backend=backend)
        
    return _secrets_manager


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience function to get a secret."""
    manager = get_secrets_manager()
    return manager.get_secret(key, default)
