@echo off
echo.
echo ================================================
echo       INICIANDO SERVIDOR BACKEND
echo       Cafeteria IA - FastAPI Server
echo ================================================
echo.

cd /d "%~dp0\backend"

echo 🔍 Verificando entorno virtual...
if not exist venv\Scripts\activate.bat (
    echo ❌ Error: Entorno virtual no encontrado
    echo 🔧 Ejecuta primero: setup_backend.bat
    pause
    exit /b 1
)

echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo 🗃️  Verificando configuración...
python -c "from app.core.config import check_settings; check_settings()"
if %ERRORLEVEL% neq 0 (
    echo ❌ Error en la configuración
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando servidor FastAPI...
echo 📍 URL: http://localhost:8000
echo 📚 Docs: http://localhost:8000/docs
echo 🔄 Modo: Hot reload activado
echo.
echo ⏹️  Presiona Ctrl+C para detener el servidor
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo 🛑 Servidor detenido
pause