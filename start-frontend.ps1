# ===============================================
# SCRIPT PARA INICIAR FRONTEND
# Cafeteria IA - React + Vite
# ===============================================

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "       INICIANDO SERVIDOR FRONTEND" -ForegroundColor Cyan
Write-Host "       Cafeteria IA - React + Vite" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

Set-Location "frontend"

# Verificar dependencias
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "❌ Error: Dependencias no instaladas" -ForegroundColor Red
    Write-Host "🔧 Ejecuta primero: .\setup-complete.ps1" -ForegroundColor Yellow
    exit 1
}

# Verificar archivos de configuración
Write-Host "🔍 Verificando configuración..." -ForegroundColor Yellow
$configFiles = @("vite.config.ts", "tailwind.config.js", "postcss.config.cjs")
foreach ($file in $configFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Error: $file no encontrado" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Archivos de configuración verificados" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Iniciando servidor de desarrollo Vite..." -ForegroundColor Green
Write-Host "📍 URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔄 Hot Module Replacement: Activo" -ForegroundColor Cyan
Write-Host "🎨 TailwindCSS: Configurado" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏹️  Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
npm run dev

Write-Host ""
Write-Host "🛑 Servidor detenido" -ForegroundColor Yellow