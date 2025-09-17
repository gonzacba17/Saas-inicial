@echo off
echo.
echo ================================================
echo       RESETEAR PROYECTO COMPLETO
echo       ⚠️  ESTO ELIMINARÁ TODO Y EMPEZARÁ DE CERO
echo ================================================
echo.

set /p confirm="¿Estás seguro de que quieres resetear todo? (S/N): "
if /i not "%confirm%"=="S" (
    echo ❌ Operación cancelada
    pause
    exit /b 0
)

echo.
echo 🗑️  Eliminando entorno virtual del backend...
cd /d "%~dp0\backend"
if exist venv (
    rmdir /s /q venv
    echo ✅ Entorno virtual eliminado
)

echo.
echo 🗑️  Eliminando node_modules del frontend...
cd /d "%~dp0\frontend"
if exist node_modules (
    rmdir /s /q node_modules
    echo ✅ node_modules eliminado
)
if exist package-lock.json (
    del package-lock.json
    echo ✅ package-lock.json eliminado
)

echo.
echo 🗑️  Eliminando archivos de migración...
cd /d "%~dp0\backend"
if exist alembic\versions (
    for %%f in (alembic\versions\*.py) do (
        if not "%%~nf"=="__init__" (
            del "%%f"
        )
    )
    echo ✅ Migraciones eliminadas
)

echo.
echo ✅ ¡Proyecto reseteado completamente!
echo.
echo 🎯 PRÓXIMOS PASOS:
echo    1. Ejecuta: setup_backend.bat
echo    2. Ejecuta: setup_frontend.bat
echo    3. Verifica que PostgreSQL esté corriendo
echo    4. Inicia los servidores con start_backend.bat y start_frontend.bat
echo.
pause