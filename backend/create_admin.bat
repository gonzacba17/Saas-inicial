@echo off
echo.
echo ================================================
echo      CREANDO USUARIO ADMINISTRADOR
echo        Cafeteria IA - SaaS Project
echo ================================================
echo.

cd /d "%~dp0"

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
echo 🗃️  Verificando configuración de base de datos...
python -c "from app.core.config import settings; print(f'Conectando a: {settings.database_url}')"
if %ERRORLEVEL% neq 0 (
    echo ❌ Error en la configuración de la base de datos
    echo 💡 Verifica el archivo .env
    pause
    exit /b 1
)

echo.
echo 👤 Ejecutando script de creación de administrador...
python create_admin.py

echo.
echo ✅ Proceso completado
echo.
echo 🎯 Si todo salió bien, ya puedes hacer login con:
echo    Username: admin
echo    Password: TuPassword123
echo    URL: http://localhost:8000/api/v1/auth/login
echo.
pause