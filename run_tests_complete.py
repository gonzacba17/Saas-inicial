#!/usr/bin/env python3
"""
Script completo para ejecutar tests del proyecto SaaS Cafeterías
================================================================

Este script proporciona diferentes modos de ejecución:
- Tests unitarios (rápidos, con TestClient)
- Tests de integración (con Docker)
- Tests completos con coverage
- Tests específicos por categoría

Uso:
    python run_tests_complete.py [modo] [opciones]
    
Modos:
    unit        - Solo tests unitarios (rápido)
    integration - Tests de integración con Docker
    all         - Todos los tests
    smoke       - Tests de humo (básicos)
    auth        - Solo tests de autenticación
    api         - Solo tests de API
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

def setup_environment():
    """Configurar variables de entorno para tests."""
    env = os.environ.copy()
    
    # Variables básicas para tests
    env.update({
        "TESTING": "true",
        "USE_SQLITE": "true",
        "PYTHONPATH": str(Path(__file__).parent / "backend"),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
    })
    
    # En Windows, configurar encoding
    if sys.platform.startswith('win'):
        env.update({
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8"
        })
    
    return env

def run_command(cmd, env=None, cwd=None, timeout=300):
    """Ejecutar comando con manejo de errores."""
    if env is None:
        env = setup_environment()
    
    if cwd is None:
        cwd = Path(__file__).parent
        
    print(f"🔧 Ejecutando: {' '.join(cmd)}")
    print(f"📁 Directorio: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            print("📋 STDOUT:")
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print("❌ STDERR:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Comando expiró después de {timeout}s")
        return False, "", "Timeout"
    except Exception as e:
        print(f"💥 Error ejecutando comando: {e}")
        return False, "", str(e)

def check_dependencies():
    """Verificar que las dependencias necesarias estén instaladas."""
    print("🔍 Verificando dependencias...")
    
    # Verificar Python
    if sys.version_info < (3, 9):
        print("❌ Se requiere Python 3.9+")
        return False
    
    # Verificar pytest
    success, _, _ = run_command(["python", "-m", "pytest", "--version"])
    if not success:
        print("❌ pytest no está instalado. Instala con: pip install pytest")
        return False
    
    print("✅ Dependencias verificadas")
    return True

def run_unit_tests(args):
    """Ejecutar tests unitarios usando TestClient."""
    print("\n🚀 EJECUTANDO TESTS UNITARIOS")
    print("=" * 50)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", "unit or not (integration or e2e)",
        "--cov=backend/app",
        "--cov-report=term-missing",
        "--maxfail=5"
    ]
    
    if args.fast:
        cmd.extend(["--maxfail=1", "-x"])
    
    if args.verbose:
        cmd.append("-vv")
    
    success, stdout, stderr = run_command(cmd, timeout=180)
    
    if success:
        print("✅ Tests unitarios completados exitosamente")
    else:
        print("❌ Tests unitarios fallaron")
        
    return success

def run_integration_tests(args):
    """Ejecutar tests de integración con Docker."""
    print("\n🐳 EJECUTANDO TESTS DE INTEGRACIÓN CON DOCKER")
    print("=" * 50)
    
    # Verificar Docker
    docker_success, _, _ = run_command(["docker", "--version"])
    if not docker_success:
        print("❌ Docker no está disponible. Los tests de integración necesitan Docker.")
        return False
    
    # Limpiar contenedores previos
    print("🧹 Limpiando contenedores previos...")
    run_command(["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"])
    
    try:
        # Iniciar servicios de test
        print("🚀 Iniciando servicios de test...")
        success, _, _ = run_command([
            "docker-compose", "-f", "docker-compose.test.yml",
            "up", "-d", "test-db", "test-redis", "test-backend"
        ], timeout=180)
        
        if not success:
            print("❌ Error iniciando servicios de test")
            return False
        
        # Esperar a que los servicios estén listos
        print("⏳ Esperando servicios...")
        time.sleep(15)
        
        # Ejecutar tests de integración
        print("🧪 Ejecutando tests de integración...")
        success, _, _ = run_command([
            "docker-compose", "-f", "docker-compose.test.yml",
            "run", "--rm", "test-runner"
        ], timeout=300)
        
        if success:
            print("✅ Tests de integración completados exitosamente")
        else:
            print("❌ Tests de integración fallaron")
            
        return success
        
    finally:
        # Limpiar siempre
        print("🧹 Limpiando servicios de test...")
        run_command(["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"])

def run_specific_tests(marker, description):
    """Ejecutar tests con un marker específico."""
    print(f"\n🎯 EJECUTANDO {description.upper()}")
    print("=" * 50)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", marker,
        "--maxfail=3"
    ]
    
    success, stdout, stderr = run_command(cmd, timeout=120)
    
    if success:
        print(f"✅ {description} completados exitosamente")
    else:
        print(f"❌ {description} fallaron")
        
    return success

def run_smoke_tests():
    """Ejecutar tests de humo - básicos y críticos."""
    return run_specific_tests("smoke or critical", "Tests de humo")

def run_auth_tests():
    """Ejecutar solo tests de autenticación."""
    return run_specific_tests("auth", "Tests de autenticación")

def run_api_tests():
    """Ejecutar solo tests de API."""
    return run_specific_tests("api", "Tests de API")

def run_all_tests(args):
    """Ejecutar todos los tests en secuencia."""
    print("\n🎯 EJECUTANDO SUITE COMPLETA DE TESTS")
    print("=" * 50)
    
    results = []
    
    # 1. Tests unitarios
    print("\n📍 FASE 1: Tests Unitarios")
    results.append(("Unitarios", run_unit_tests(args)))
    
    # 2. Tests de integración (si Docker está disponible)
    if not args.skip_integration:
        print("\n📍 FASE 2: Tests de Integración")
        results.append(("Integración", run_integration_tests(args)))
    
    # Resumen
    print("\n📊 RESUMEN DE RESULTADOS")
    print("=" * 50)
    
    success_count = 0
    for test_type, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{test_type:20} {status}")
        if success:
            success_count += 1
    
    total_tests = len(results)
    print(f"\nResultado: {success_count}/{total_tests} suites pasaron")
    
    return success_count == total_tests

def create_test_report():
    """Crear reporte de tests si existe coverage."""
    coverage_file = Path("htmlcov/index.html")
    if coverage_file.exists():
        print(f"\n📊 Reporte de coverage disponible en: {coverage_file.absolute()}")
    
    results_file = Path("test-results.xml")
    if results_file.exists():
        print(f"📋 Resultados JUnit en: {results_file.absolute()}")

def main():
    parser = argparse.ArgumentParser(
        description="Script de testing para SaaS Cafeterías",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run_tests_complete.py unit                 # Solo tests unitarios
  python run_tests_complete.py integration          # Solo integración
  python run_tests_complete.py all                  # Todos los tests
  python run_tests_complete.py smoke                # Tests básicos
  python run_tests_complete.py auth                 # Solo autenticación
  python run_tests_complete.py unit --fast          # Unitarios rápidos
  python run_tests_complete.py all --skip-integration  # Sin Docker
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["unit", "integration", "all", "smoke", "auth", "api"],
        help="Tipo de tests a ejecutar"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Ejecutar en modo rápido (fallar al primer error)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Output más detallado"
    )
    
    parser.add_argument(
        "--skip-integration",
        action="store_true",
        help="Saltar tests de integración en modo 'all'"
    )
    
    args = parser.parse_args()
    
    print("🧪 SAAS CAFETERÍAS - SUITE DE TESTING")
    print("=" * 50)
    print(f"Modo: {args.mode}")
    print(f"Python: {sys.version}")
    print(f"Directorio: {Path.cwd()}")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Ejecutar tests según el modo
    success = False
    
    if args.mode == "unit":
        success = run_unit_tests(args)
    elif args.mode == "integration":
        success = run_integration_tests(args)
    elif args.mode == "all":
        success = run_all_tests(args)
    elif args.mode == "smoke":
        success = run_smoke_tests()
    elif args.mode == "auth":
        success = run_auth_tests()
    elif args.mode == "api":
        success = run_api_tests()
    
    # Crear reportes
    create_test_report()
    
    # Resultado final
    if success:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        sys.exit(0)
    else:
        print("\n💥 ALGUNOS TESTS FALLARON")
        sys.exit(1)

if __name__ == "__main__":
    main()