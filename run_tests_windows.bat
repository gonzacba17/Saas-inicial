@echo off
echo 🧪 EJECUTOR DE TESTS - WINDOWS 11 ANTI-TIMEOUT
echo =============================================

REM Configurar encoding UTF-8 y variables
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set TESTING=true
set USE_SQLITE=true

echo 🔧 Configurando entorno...
echo PYTHONIOENCODING=%PYTHONIOENCODING%
echo PYTHONUTF8=%PYTHONUTF8%
echo TESTING=%TESTING%

REM Verificar Python
echo 🐍 Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instala Python 3.11+
    pause
    exit /b 1
)

REM Instalar dependencias básicas
echo 📦 Instalando dependencias básicas...
pip install pytest pytest-timeout pytest-cov fastapi[all] sqlalchemy python-multipart

REM Test rápido de verificación
echo 🚀 Test rápido de verificación...
python -c "
import sys
sys.path.insert(0, 'backend')
try:
    from app.main import app
    print('✅ App importada correctamente')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if %errorlevel% neq 0 (
    echo ❌ Error en configuración inicial
    pause
    exit /b 1
)

REM Ejecutar test de ejemplo
echo 🧪 Ejecutando test de ejemplo...
python -m pytest test_auth_working.py -v --tb=short --timeout=30

if %errorlevel% equ 0 (
    echo ✅ Test de ejemplo PASÓ
) else (
    echo ❌ Test de ejemplo FALLÓ
    echo.
    echo 🔍 Diagnostico:
    echo - Verifica que el directorio backend/ existe
    echo - Verifica que app/main.py está en backend/
    echo - Ejecuta: cd backend ^&^& python -c "from app.main import app; print('OK')"
    pause
    exit /b 1
)

REM Ejecutar todos los tests si el ejemplo pasó
echo.
echo 🎯 Ejecutando TODOS los tests...
python -m pytest tests/ -v --tb=short --timeout=30 --maxfail=3

if %errorlevel% equ 0 (
    echo.
    echo 🎉 ¡TODOS LOS TESTS PASARON!
    echo 📊 Revisa el reporte de coverage en htmlcov/index.html
) else (
    echo.
    echo ⚠️  Algunos tests fallaron
    echo 📋 Revisa los errores arriba
)

echo.
echo 🏁 Ejecución completada
pause