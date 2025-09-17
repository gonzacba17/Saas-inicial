# ===============================================
# SCRIPT PARA INICIAR BACKEND
# Cafeteria IA - FastAPI Server
# ===============================================

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "       INICIANDO SERVIDOR BACKEND" -ForegroundColor Cyan
Write-Host "       Cafeteria IA - FastAPI" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

Set-Location "backend"

# Verificar entorno virtual
Write-Host "🔍 Verificando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Error: Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "🔧 Ejecuta primero: .\setup-complete.ps1" -ForegroundColor Yellow
    exit 1
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar configuración
Write-Host "🗃️  Verificando configuración..." -ForegroundColor Yellow
try {
    python -c "from app.core.config import check_settings; check_settings()"
    Write-Host "✅ Configuración verificada" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error en la configuración" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Iniciando servidor FastAPI..." -ForegroundColor Green
Write-Host "📍 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔄 Modo: Hot reload activado" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏹️  Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Write-Host ""
Write-Host "🛑 Servidor detenido" -ForegroundColor Yellow