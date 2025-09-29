#!/usr/bin/env python3
"""
Script para ejecutar tests sin colgamientos
Configura el entorno y ejecuta pytest con configuración optimizada
"""
import os
import sys
import subprocess

def setup_environment():
    """Configurar variables de entorno para tests"""
    os.environ["TESTING"] = "true"
    os.environ["USE_SQLITE"] = "true"
    os.environ["PYTHONPATH"] = os.getcwd()

def run_tests():
    """Ejecutar tests con configuración anti-colgamiento"""
    setup_environment()
    
    cmd = [
        sys.executable, "-m", "pytest",
        "test_fixed_example.py",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "--timeout=30",
        "--disable-warnings"
    ]
    
    print("🚀 Ejecutando tests sin colgamientos...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, timeout=120)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("❌ Tests se colgaron después de 2 minutos")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    if exit_code == 0:
        print("✅ Tests completados exitosamente")
    else:
        print("❌ Tests fallaron o se colgaron")
    sys.exit(exit_code)