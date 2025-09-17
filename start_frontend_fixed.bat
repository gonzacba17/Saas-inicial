@echo off
echo.
echo ================================================
echo       INICIANDO FRONTEND CAFETERIA IA
echo       React + Vite + TailwindCSS (CORREGIDO)
echo ================================================
echo.

cd /d "%~dp0\frontend"

echo 🔍 Verificando archivos de configuración...
if not exist postcss.config.cjs (
    echo ❌ Error: postcss.config.cjs no encontrado
    pause
    exit /b 1
)

if not exist tailwind.config.js (
    echo ❌ Error: tailwind.config.js no encontrado
    pause
    exit /b 1
)

if not exist vite.config.ts (
    echo ❌ Error: vite.config.ts no encontrado
    pause
    exit /b 1
)

echo ✅ Archivos de configuración encontrados

echo.
echo 🔍 Verificando dependencias...
if not exist node_modules (
    echo ❌ Error: node_modules no encontrado
    echo 🔧 Ejecuta primero los comandos de instalación en PowerShell
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas

echo.
echo 🚀 Iniciando servidor de desarrollo Vite...
echo 📍 URL: http://localhost:5173
echo 🎨 TailwindCSS: Configurado con PostCSS
echo 🔄 Hot Module Replacement: Activo
echo.
echo ⏹️  Presiona Ctrl+C para detener el servidor
echo.

npm run dev

echo.
echo 🛑 Servidor detenido
pause