@echo off
echo.
echo ================================================
echo    CONFIGURACIÓN INICIAL DEL FRONTEND
echo    Cafeteria IA - React + Vite + TailwindCSS
echo ================================================
echo.

cd /d "%~dp0\frontend"

echo 🔍 Verificando Node.js...
node --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Node.js no está instalado o no está en el PATH
    echo 📝 Instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando npm...
npm --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: npm no está disponible
    pause
    exit /b 1
)

echo.
echo 🧹 Limpiando instalaciones previas...
if exist node_modules (
    echo 🗑️  Eliminando node_modules...
    rmdir /s /q node_modules
)
if exist package-lock.json (
    echo 🗑️  Eliminando package-lock.json...
    del package-lock.json
)

echo.
echo 📦 Actualizando npm a la última versión...
npm install -g npm@latest

echo.
echo 📚 Instalando dependencias del frontend...
npm install

echo.
echo 🎨 Verificando configuración de TailwindCSS...
if not exist "src\index.css" (
    echo ❌ Error: archivo src\index.css no encontrado
    pause
    exit /b 1
)

echo.
echo 🔧 Verificando configuración de Vite...
npx vite --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Vite no se instaló correctamente
    pause
    exit /b 1
)

echo.
echo 🛠️  Construyendo assets para verificar configuración...
npm run build
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Falló la construcción del proyecto
    echo 🔍 Revisa la configuración de Vite y TailwindCSS
    pause
    exit /b 1
)

echo.
echo ✅ ¡Frontend configurado exitosamente!
echo.
echo 📋 RESUMEN:
echo    • Node.js y npm verificados
echo    • Dependencias instaladas
echo    • TailwindCSS configurado
echo    • Vite configurado
echo    • Build de prueba exitoso
echo.
echo 🎯 SIGUIENTE PASO:
echo    Para iniciar el servidor de desarrollo ejecuta: start_frontend.bat
echo    O manualmente: npm run dev
echo.
pause