#!/usr/bin/env python
"""
Script para ejecutar tests con coverage y servir reporte HTML
Optimizado para Windows
"""
import subprocess
import sys
import os
import time
import http.server
import socketserver
import webbrowser
from pathlib import Path
from threading import Timer


def run_tests_with_coverage():
    """Ejecutar tests con coverage"""
    print("=" * 80)
    print("🔍 Ejecutando tests con coverage...")
    print("=" * 80)
    
    backend_dir = Path(__file__).parent.resolve()
    htmlcov_dir = backend_dir / "htmlcov"
    
    if htmlcov_dir.exists():
        print(f"🗑️  Limpiando directorio anterior: {htmlcov_dir}")
        import shutil
        shutil.rmtree(htmlcov_dir, ignore_errors=True)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=app/api/v1",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=html",
        "--tb=short",
        "-v"
    ]
    
    print(f"\n📦 Módulos a testear: app/api/v1/")
    print(f"📁 Directorio de tests: tests/")
    print(f"💻 Comando: {' '.join(cmd)}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(backend_dir),
            env=os.environ.copy()
        )
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 80)
        print(f"✅ Tests completados en {elapsed_time:.2f} segundos")
        print("=" * 80)
        
        return result.returncode, htmlcov_dir
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: No se encontró pytest. Instala dependencias con: pip install -r requirements-test.txt")
        return 1, None
    except Exception as e:
        print(f"\n❌ Error durante ejecución: {str(e)}")
        return 1, None


def serve_coverage_report(htmlcov_dir):
    """Servir reporte HTML en servidor local"""
    if not htmlcov_dir or not htmlcov_dir.exists():
        print(f"\n❌ No se encontró el directorio htmlcov en: {htmlcov_dir}")
        print("   El reporte HTML no fue generado.")
        return
    
    index_file = htmlcov_dir / "index.html"
    if not index_file.exists():
        print(f"\n❌ No se encontró index.html en: {index_file}")
        return
    
    print("\n" + "=" * 80)
    print("📊 Generando reporte HTML...")
    print("=" * 80)
    
    PORT = 8001
    
    os.chdir(str(htmlcov_dir))
    
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"\n✅ Servidor disponible en: {url}")
            print(f"📂 Sirviendo: {htmlcov_dir}")
            print(f"\n💡 Presiona Ctrl+C para detener el servidor\n")
            
            def open_browser():
                webbrowser.open(url)
            
            Timer(1.5, open_browser).start()
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 10048:
            print(f"\n⚠️  Puerto {PORT} en uso. Intenta cerrar otras aplicaciones o usa otro puerto.")
        else:
            print(f"\n❌ Error al iniciar servidor: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido")


if __name__ == "__main__":
    try:
        returncode, htmlcov_dir = run_tests_with_coverage()
        
        if returncode == 0:
            serve_coverage_report(htmlcov_dir)
        else:
            print(f"\n⚠️  Tests fallaron con código: {returncode}")
            print("   No se iniciará el servidor HTTP.")
            
        sys.exit(returncode)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación interrumpida por el usuario")
        sys.exit(130)
