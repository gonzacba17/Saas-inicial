@echo off
echo.
echo ================================================
echo       INICIANDO SERVIDOR FRONTEND
echo       Cafeteria IA - React + Vite
echo ================================================
echo.

echo 🎨 Ejecutando script PowerShell del frontend...
powershell -ExecutionPolicy Bypass -File "%~dp0start-frontend.ps1"

echo.
echo 🛑 Servidor frontend detenido
pause