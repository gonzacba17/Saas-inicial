@echo off
echo.
echo ================================================
echo       INICIANDO SERVIDOR BACKEND
echo       Cafeteria IA - FastAPI
echo ================================================
echo.

echo 🚀 Ejecutando script PowerShell del backend...
powershell -ExecutionPolicy Bypass -File "%~dp0start-backend.ps1"

echo.
echo 🛑 Servidor backend detenido
pause