#!/usr/bin/env python3
"""
Script de inicio para desarrollo local en Windows.
Verifica la configuración y inicia el servidor FastAPI.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Iniciar el servidor de desarrollo con verificaciones"""
    print("🚀 SaaS Cafeterías - Servidor de Desarrollo")
    print("=" * 50)
    
    # Verificar configuración
    print("🔍 Verificando configuración...")
    
    try:
        from app.core.config import settings
        print(f"✅ Entorno: {settings.environment}")
        
        # Show database configuration
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            print(f"✅ Base de datos: SQLite - {settings.sqlite_file}")
        else:
            print(f"✅ Base de datos: PostgreSQL - {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
        
        print(f"✅ Puerto: 8000")
        print(f"✅ Debug: {settings.debug}")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        sys.exit(1)
    
    print("\n📋 Información de inicio:")
    print("• Servidor: http://localhost:8000")
    print("• Documentación API: http://localhost:8000/docs")
    print("• Admin: admin@example.com / Admin1234!")
    print("• Base de datos: SQLite (local)")
    print("• Redis: Memoria (fallback)")
    print("• MercadoPago: Deshabilitado (desarrollo)")
    
    print("\n🟡 Iniciando servidor FastAPI con reload automático...")
    print("   Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    # Cambiar al directorio backend
    os.chdir(backend_dir)
    
    # Iniciar servidor
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n🔴 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()