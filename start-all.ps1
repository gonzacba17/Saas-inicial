# ===============================================
# SCRIPT PARA INICIAR BACKEND Y FRONTEND
# Cafeteria IA - Desarrollo Completo
# ===============================================

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "    INICIANDO APLICACIÓN COMPLETA" -ForegroundColor Cyan
Write-Host "    Backend: FastAPI + PostgreSQL" -ForegroundColor Cyan
Write-Host "    Frontend: React + Vite + TailwindCSS" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Verificar directorios
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Iniciando servidores en paralelo..." -ForegroundColor Green
Write-Host ""

# Función para ejecutar en background
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\start-backend.ps1"
}

$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\start-frontend.ps1"
}

Write-Host "🔧 Backend iniciando en background..." -ForegroundColor Yellow
Write-Host "🎨 Frontend iniciando en background..." -ForegroundColor Yellow
Write-Host ""

# Esperar un poco para que se inicien
Start-Sleep -Seconds 3

Write-Host "📍 URLs disponibles:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "🔑 Credenciales de admin:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor Yellow
Write-Host "   Password: TuPassword123" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏹️  Presiona cualquier tecla para detener ambos servidores..." -ForegroundColor Red

# Esperar input del usuario
$null = Read-Host

# Detener jobs
Write-Host ""
Write-Host "🛑 Deteniendo servidores..." -ForegroundColor Yellow
Stop-Job -Job $backendJob, $frontendJob
Remove-Job -Job $backendJob, $frontendJob

Write-Host "✅ Servidores detenidos" -ForegroundColor Green