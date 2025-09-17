from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    # Configuración del modelo para cargar variables de entorno
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignora variables extra en el .env
    )
    
    # ==============================================
    # INFORMACIÓN DEL PROYECTO
    # ==============================================
    project_name: str = "ModularBiz SaaS"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    environment: str = "development"
    debug: bool = True
    
    # ==============================================
    # CONFIGURACIÓN JWT
    # ==============================================
    secret_key: str = "modularbiz-saas-super-secret-key-2024-production-ready-minimum-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ==============================================
    # CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL
    # ==============================================
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "modularbiz_saas"
    
    @property
    def database_url(self) -> str:
        """Construye la URL de conexión a PostgreSQL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # ==============================================
    # CONFIGURACIÓN REDIS (OPCIONAL)
    # ==============================================
    redis_url: str = "redis://localhost:6379/0"
    
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


# Función de utilidad para verificar la configuración
def check_settings():
    """Verifica que todas las configuraciones críticas estén presentes"""
    print(f"✓ Proyecto: {settings.project_name}")
    print(f"✓ Entorno: {settings.environment}")
    print(f"✓ Base de datos: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"✓ API URL: {settings.api_v1_str}")
    print(f"✓ CORS habilitado para: {', '.join(settings.allowed_origins_list)}")
    return True


if __name__ == "__main__":
    check_settings()