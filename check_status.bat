@echo off
echo.
echo ================================================
echo         VERIFICAR ESTADO DEL PROYECTO
echo         Cafeteria IA - Status Check
echo ================================================
echo.

echo 🔍 VERIFICANDO PRERREQUISITOS...
echo.

echo 📍 Python:
python --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo    ❌ Python no encontrado
) else (
    echo    ✅ Python instalado
)

echo.
echo 📍 Node.js:
node --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo    ❌ Node.js no encontrado
) else (
    echo    ✅ Node.js instalado
)

echo.
echo 📍 PostgreSQL:
psql --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo    ⚠️  PostgreSQL CLI no encontrado (esto es normal si solo tienes el servidor)
) else (
    echo    ✅ PostgreSQL CLI disponible
)

echo.
echo 🔍 VERIFICANDO CONFIGURACIÓN DEL BACKEND...
echo.

cd /d "%~dp0\backend"

if exist venv (
    echo    ✅ Entorno virtual creado
) else (
    echo    ❌ Entorno virtual no creado
)

if exist .env (
    echo    ✅ Archivo .env encontrado
) else (
    echo    ❌ Archivo .env no encontrado
)

if exist alembic\versions (
    echo    ✅ Directorio de migraciones existe
) else (
    echo    ❌ Directorio de migraciones no existe
)

echo.
echo 🔍 VERIFICANDO CONFIGURACIÓN DEL FRONTEND...
echo.

cd /d "%~dp0\frontend"

if exist node_modules (
    echo    ✅ Dependencias de Node.js instaladas
) else (
    echo    ❌ Dependencias de Node.js no instaladas
)

if exist .env (
    echo    ✅ Archivo .env encontrado
) else (
    echo    ❌ Archivo .env no encontrado
)

if exist tailwind.config.js (
    echo    ✅ TailwindCSS configurado
) else (
    echo    ❌ TailwindCSS no configurado
)

if exist vite.config.ts (
    echo    ✅ Vite configurado
) else (
    echo    ❌ Vite no configurado
)

echo.
echo 🔍 VERIFICANDO SERVICIOS...
echo.

echo 📍 Verificando puerto 8000 (Backend):
netstat -an | findstr :8000 >nul
if %ERRORLEVEL% equ 0 (
    echo    ✅ Servidor backend corriendo en puerto 8000
) else (
    echo    ❌ Servidor backend no corriendo
)

echo.
echo 📍 Verificando puerto 5173 (Frontend):
netstat -an | findstr :5173 >nul
if %ERRORLEVEL% equ 0 (
    echo    ✅ Servidor frontend corriendo en puerto 5173
) else (
    echo    ❌ Servidor frontend no corriendo
)

echo.
echo ================================================
echo 📋 RESUMEN DE ESTADO COMPLETADO
echo ================================================
echo.
pause