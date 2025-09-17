@echo off
echo.
echo ================================================
echo    EJECUTANDO CONFIGURACION COMPLETA
echo    (Wrapper para PowerShell)
echo ================================================
echo.

echo 🔧 Ejecutando script PowerShell de configuracion...
powershell -ExecutionPolicy Bypass -File "%~dp0setup-complete.ps1"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Error en la configuracion
    pause
    exit /b 1
)

echo.
echo ✅ Configuracion completada exitosamente
echo.
echo 🎯 Para iniciar los servidores:
echo    Backend:  start-backend.bat
echo    Frontend: start-frontend.bat
echo    Ambos:    start-all.bat
echo.
pause