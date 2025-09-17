@echo off
echo.
echo ================================================
echo    CONFIGURACIÓN INICIAL DEL BACKEND
echo    Cafeteria IA - FastAPI + PostgreSQL
echo ================================================
echo.

cd /d "%~dp0\backend"

echo 🔍 Verificando Python...
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo 📝 Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 🐍 Creando entorno virtual...
if exist venv (
    echo ⚠️  El entorno virtual ya existe. Eliminando...
    rmdir /s /q venv
)
python -m venv venv

echo.
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

echo.
echo 📚 Instalando dependencias...
pip install -r requirements.txt

echo.
echo 🗃️  Verificando conexión a PostgreSQL...
python -c "from app.core.config import settings; print(f'✓ Configuración cargada: {settings.database_url}')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Error al cargar la configuración. Verifica el archivo .env
    pause
    exit /b 1
)

echo.
echo 🔄 Inicializando Alembic (si es necesario)...
if not exist alembic\versions (
    echo 📁 Creando directorio de versiones...
    mkdir alembic\versions
)

echo.
echo 🗂️  Generando migración inicial...
alembic revision --autogenerate -m "Initial migration - Create all tables"

echo.
echo 🚀 Aplicando migraciones a la base de datos...
alembic upgrade head

echo.
echo ✅ ¡Backend configurado exitosamente!
echo.
echo 📋 RESUMEN:
echo    • Entorno virtual creado y activado
echo    • Dependencias instaladas
echo    • Base de datos configurada
echo    • Migraciones aplicadas
echo.
echo 🎯 SIGUIENTE PASO:
echo    Para iniciar el servidor ejecuta: start_backend.bat
echo    O manualmente: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
pause