@echo off
echo.
echo ================================================
echo       INICIANDO SERVIDOR FRONTEND
echo       Cafeteria IA - React Development Server
echo ================================================
echo.

cd /d "%~dp0\frontend"

echo 🔍 Verificando dependencias...
if not exist node_modules (
    echo ❌ Error: Dependencias no instaladas
    echo 🔧 Ejecuta primero: setup_frontend.bat
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando configuración...
if not exist vite.config.ts (
    echo ❌ Error: Archivo vite.config.ts no encontrado
    pause
    exit /b 1
)

echo.
echo 🎨 Verificando TailwindCSS...
if not exist tailwind.config.js (
    echo ❌ Error: Archivo tailwind.config.js no encontrado
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando servidor de desarrollo...
echo 📍 URL: http://localhost:5173
echo 🔄 Modo: Hot Module Replacement activado
echo 🎨 TailwindCSS: Activo
echo.
echo ⏹️  Presiona Ctrl+C para detener el servidor
echo.

npm run dev

echo.
echo 🛑 Servidor detenido
pause