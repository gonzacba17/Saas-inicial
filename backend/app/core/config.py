from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import os
from pathlib import Path

# Ensure .env file is loaded explicitly
try:
    from dotenv import load_dotenv
    # Load .env from multiple possible locations
    env_paths = [
        Path(".env"),
        Path("../.env"),
        Path("../../.env"),
        Path(__file__).parent.parent.parent / ".env"
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path, encoding='utf-8')
            print(f"Loaded environment file: {env_path.absolute()}")
            break
    else:
        print("No .env file found in expected locations")
        
except ImportError:
    print("python-dotenv not installed, relying on system environment variables")
except Exception as e:
    print(f"Error loading .env file: {e}")


class Settings(BaseSettings):
    # Configuración del modelo para cargar variables de entorno
    model_config = SettingsConfigDict(
        env_file=[".env.local", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignora variables extra en el .env
    )

    # ==============================================
    # INFORMACIÓN DEL PROYECTO
    # ==============================================
    project_name: str = "SaaS Cafeterías"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    environment: str = "development"
    debug: bool = True

    # ==============================================
    # CONFIGURACIÓN JWT
    # ==============================================
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator('secret_key')
    def validate_secret_key(cls, v, info):
        """Validar que SECRET_KEY sea segura en producción"""
        env = info.data.get('environment', 'development')
        
        if env == 'production':
            forbidden_patterns = [
                'development-secret-key',
                'change-in-production',
                'change-this-in-production',
                'your-secret-key',
                'example',
                'test',
                'change-me'
            ]
            
            if any(pattern in v.lower() for pattern in forbidden_patterns):
                raise ValueError(
                    '\n🚨 FATAL ERROR: Development SECRET_KEY detected in production!\n\n'
                    'Generate a secure key with:\n'
                    '  python -c "import secrets; print(secrets.token_urlsafe(64))"\n\n'
                    'Then update your .env file with ENVIRONMENT=production\n'
                )
            
            if len(v) < 64:
                raise ValueError(
                    f'SECRET_KEY too short: {len(v)} chars (minimum: 64 in production)\n'
                    'Generate a new one with:\n'
                    '  python -c "import secrets; print(secrets.token_urlsafe(64))"'
                )
        
        return v

    # ==============================================
    # CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL
    # ==============================================
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT") or "5432")
    postgres_db: str = os.getenv("POSTGRES_DB", "saas_db")

    # ==============================================
    # CONFIGURACIÓN DE BASE DE DATOS SQLITE (DESARROLLO)
    # ==============================================
    sqlite_file: str = os.getenv("SQLITE_FILE", "saas_cafeterias_local.db")

    # Direct DATABASE_URL support
    database_url: Optional[str] = None
    
    @property
    def db_url(self) -> str:
        """Construye la URL de conexión a la base de datos con manejo de encoding UTF-8"""
        # Use DATABASE_URL if provided in environment
        if self.database_url:
            # Ensure the provided DATABASE_URL has proper encoding
            return self._ensure_utf8_encoding(self.database_url)
        
        # Verificar si PostgreSQL está disponible, sino usar SQLite
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            return f"sqlite:///./{self.sqlite_file}"
        else:
            # Configuración para PostgreSQL con encoding UTF-8 completo
            return self._build_postgres_url()
    
    def _ensure_utf8_encoding(self, url: str) -> str:
        """Ensure database URL has proper UTF-8 encoding parameters."""
        if url.startswith('postgresql'):
            # Add UTF-8 encoding parameters if not present
            if 'client_encoding=utf8' not in url:
                separator = '&' if '?' in url else '?'
                url += f"{separator}client_encoding=utf8"
        return url
    
    def _build_postgres_url(self) -> str:
        """Build PostgreSQL URL with proper encoding and error handling."""
        from urllib.parse import quote_plus
        import logging
        
        try:
            # URL encode all components to handle special characters
            encoded_user = quote_plus(str(self.postgres_user))
            encoded_password = quote_plus(str(self.postgres_password))
            encoded_host = quote_plus(str(self.postgres_host))
            encoded_db = quote_plus(str(self.postgres_db))
            
            # Build URL with UTF-8 encoding parameters
            base_url = f"postgresql://{encoded_user}:{encoded_password}@{encoded_host}:{self.postgres_port}/{encoded_db}"
            
            # Add UTF-8 specific parameters (PostgreSQL specific)
            url = f"{base_url}?client_encoding=utf8"
            
            return url
            
        except Exception as e:
            logging.error(f"Error building PostgreSQL URL: {str(e)}")
            logging.error("Check that all database credentials are properly set and don't contain invalid characters")
            
            # Fallback to basic URL without encoding if there's an issue
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # ==============================================
    # CONFIGURACIÓN REDIS
    # ==============================================
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_url: str = "redis://localhost:6379/0"

    # Redis Cache Configuration
    cache_default_ttl: int = 300  # 5 minutes
    cache_long_ttl: int = 3600   # 1 hour
    cache_short_ttl: int = 60    # 1 minute

    # ==============================================
    # SECRETS MANAGEMENT
    # ==============================================
    secrets_backend: str = "environment"  # environment, file, vault, aws
    secrets_dir: str = "secrets"

    # HashiCorp Vault
    vault_url: Optional[str] = None
    vault_token: Optional[str] = None
    vault_mount_point: str = "secret"

    # AWS Secrets Manager
    aws_region: str = "us-east-1"
    aws_profile: Optional[str] = None

    # ==============================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ==============================================
    rate_limit_calls: int = 100
    rate_limit_period: int = 3600  # 1 hour
    enable_https_redirect: bool = False
    trusted_proxies: str = "127.0.0.1,::1"
    
    # ==============================================
    # CONFIGURACIÓN DE TESTING
    # ==============================================
    testing: bool = os.getenv("TESTING", "false").lower() == "true"

    # ==============================================
    # APIs EXTERNAS (OPCIONAL)
    # ==============================================
    openai_api_key: Optional[str] = None
    mercadopago_key: Optional[str] = None

    # ==============================================
    # CONFIGURACIÓN CORS
    # ==============================================
    allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convierte la cadena de orígenes separados por comas a una lista"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # ==============================================
    # CONFIGURACIÓN DE LOGGING
    # ==============================================
    log_level: str = "INFO"

    # ==============================================
    # CONFIGURACIÓN DE ARCHIVOS
    # ==============================================
    max_file_size_mb: int = 10
    upload_folder: str = "uploads"


# Instancia global de configuración
settings = Settings()

def check_settings():
    print(f"✓ Proyecto: {settings.project_name}")
    print(f"✓ Entorno: {settings.environment}")
    print(f"✓ Base de datos: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"✓ API URL: {settings.api_v1_str}")
    print(f"✓ CORS habilitado para: {', '.join(settings.allowed_origins_list)}")
    return True


if __name__ == "__main__":
    check_settings()