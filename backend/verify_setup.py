#!/usr/bin/env python3
"""
Script para verificar que la configuración del backend esté correcta.
Verifica todas las dependencias y configuraciones antes de ejecutar la aplicación.
"""
import os
import sys
import sqlite3
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_env_file():
    """Verificar que el archivo .env existe y es legible"""
    env_path = Path("../.env")
    
    print("🔍 Verificando archivo .env...")
    if not env_path.exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("✅ Archivo .env leído correctamente")
            if "USE_SQLITE=true" in content:
                print("✅ Configuración SQLite activada")
            else:
                print("⚠️  SQLite no está activado")
        return True
    except UnicodeDecodeError as e:
        print(f"❌ Error de codificación en .env: {e}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo .env: {e}")
        return False

def check_config():
    """Verificar que la configuración se carga correctamente"""
    print("\n🔍 Verificando configuración...")
    try:
        from app.core.config import settings
        print(f"✅ Configuración cargada correctamente")
        print(f"   📁 Proyecto: {settings.project_name}")
        print(f"   🌍 Entorno: {settings.environment}")
        print(f"   🗃️  Base de datos: SQLite - {settings.sqlite_file}")
        print(f"   🔐 Debug: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

def check_database():
    """Verificar que la base de datos SQLite se puede crear/conectar"""
    print("\n🔍 Verificando base de datos SQLite...")
    try:
        from app.core.config import settings
        db_path = Path(settings.sqlite_file)
        
        # Intentar conectar a SQLite
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        print(f"✅ Conexión SQLite exitosa: {db_path.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error con SQLite: {e}")
        return False

def check_redis():
    """Verificar Redis (opcional)"""
    print("\n🔍 Verificando Redis (opcional)...")
    try:
        import redis
        from app.core.config import settings
        
        r = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis conectado")
        return True
    except Exception as e:
        print(f"⚠️  Redis no disponible (continuando con cache en memoria): {e}")
        return True  # No es crítico

def check_mercadopago():
    """Verificar MercadoPago (opcional)"""
    print("\n🔍 Verificando MercadoPago (opcional)...")
    try:
        from app.core.config import settings
        if settings.mercadopago_key:
            print("✅ Token MercadoPago configurado")
        else:
            print("⚠️  MercadoPago token no configurado (funcionalidad de pagos deshabilitada)")
        return True
    except Exception as e:
        print(f"⚠️  MercadoPago no disponible: {e}")
        return True  # No es crítico

def check_imports():
    """Verificar que las importaciones principales funcionan"""
    print("\n🔍 Verificando importaciones principales...")
    try:
        from app.main import app
        print("✅ Aplicación FastAPI importada correctamente")
        
        from app.db.db import create_tables
        print("✅ Funciones de base de datos importadas")
        
        from app.services import get_password_hash
        print("✅ Servicios de autenticación importados")
        
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def main():
    """Ejecutar todas las verificaciones"""
    print("🚀 SaaS Cafeterías - Verificación de Configuración")
    print("=" * 60)
    
    checks = [
        check_env_file,
        check_config,
        check_database,
        check_redis,
        check_mercadopago,
        check_imports
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ¡Todas las verificaciones pasaron exitosamente!")
        print("\n📝 Comandos para ejecutar:")
        print("1. Crear usuario admin:")
        print("   cd backend && python create_admin.py")
        print("\n2. Iniciar servidor:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
        print("\n3. Acceder a la documentación:")
        print("   http://localhost:8000/docs")
        return True
    else:
        print("❌ Algunas verificaciones fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)