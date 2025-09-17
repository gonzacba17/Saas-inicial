"""
Archivo de configuración del entorno de Alembic para Cafeteria IA
Maneja las migraciones de base de datos PostgreSQL con SQLAlchemy
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# ==============================================
# CONFIGURACIÓN DE PATHS E IMPORTS
# ==============================================

# Añadir el directorio padre al path para importar la aplicación
current_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.dirname(current_path)
sys.path.append(backend_path)

# Importar configuración y modelos
from app.core.config import settings
from app.db.session import Base

# Importar TODOS los modelos para que Alembic los detecte
from app.db.models import User, Cafe, Product, Order, OrderItem, OrderStatus

# ==============================================
# CONFIGURACIÓN DE ALEMBIC
# ==============================================

# Objeto de configuración de Alembic
config = context.config

# Configurar logging desde el archivo .ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de los modelos para autogenerate
target_metadata = Base.metadata

# ==============================================
# FUNCIONES DE UTILIDAD
# ==============================================

def get_url():
    """
    Obtiene la URL de la base de datos desde la configuración
    Permite usar variables de entorno para diferentes entornos
    """
    return settings.database_url


def run_migrations_offline() -> None:
    """
    Ejecuta migraciones en modo 'offline'.
    
    Configura el contexto solo con una URL, sin crear un Engine.
    Las llamadas a context.execute() emiten strings al script de salida.
    Útil para generar scripts SQL sin conexión a la base.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detectar cambios de tipo
        compare_server_default=True,  # Detectar cambios en defaults
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecuta migraciones en modo 'online'.
    
    Crea un Engine y asocia una conexión con el contexto.
    Modo recomendado para desarrollo y producción.
    """
    # Configurar la conexión desde las variables de entorno
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    # Crear el engine con pool de conexiones
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detectar cambios de tipo
            compare_server_default=True,  # Detectar cambios en defaults
            render_as_batch=False,  # Para PostgreSQL no necesitamos batch
        )

        with context.begin_transaction():
            context.run_migrations()


# ==============================================
# EJECUCIÓN PRINCIPAL
# ==============================================

def main():
    """Función principal que determina el modo de ejecución"""
    try:
        if context.is_offline_mode():
            print("🔄 Ejecutando migraciones en modo OFFLINE...")
            run_migrations_offline()
        else:
            print("🔄 Ejecutando migraciones en modo ONLINE...")
            print(f"📊 Conectando a: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
            run_migrations_online()
        print("✅ Migraciones completadas exitosamente!")
    except Exception as e:
        print(f"❌ Error en las migraciones: {e}")
        raise


if __name__ == "__main__":
    main()
else:
    # Cuando se ejecuta desde alembic command
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()