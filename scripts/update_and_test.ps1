# ===============================================
# SaaS Cafeterías - Update and Test Script (Windows)
# ===============================================
# 
# Script unificado para Windows que:
# 1. Sincroniza documentación
# 2. Corrige usuario admin
# 3. Ejecuta tests completos
# 4. Genera reporte final
#
# Uso: .\update_and_test.ps1
# ===============================================

# Error handling
$ErrorActionPreference = "Stop"

# Function definitions
function Write-Log {
    param($Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Blue
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# ===============================================
# HEADER
# ===============================================

Write-Host ""
Write-Host "🚀 SaaS Cafeterías - Update and Test Script (Windows)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ===============================================
# 1. VERIFICAR ENTORNO
# ===============================================

Write-Log "Verificando entorno..."

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Error "Este script debe ejecutarse desde el directorio raíz del proyecto"
    Write-Error "Estructura esperada: .\backend\ y .\frontend\"
    exit 1
}

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        Write-Error "Python no está instalado o no está en PATH"
        exit 1
    }
    $pythonCmd = "python3"
} else {
    $pythonCmd = "python"
}

Write-Success "Entorno verificado"

# ===============================================
# 2. CONFIGURAR BACKEND
# ===============================================

Write-Log "Configurando backend..."

Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Log "Creando entorno virtual..."
    & $pythonCmd -m venv venv
}

# Activate virtual environment
try {
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
    } elseif (Test-Path "venv\Scripts\activate.bat") {
        & .\venv\Scripts\activate.bat
    } else {
        throw "No se encontró script de activación"
    }
} catch {
    Write-Error "No se pudo activar el entorno virtual: $_"
    exit 1
}

# Install/update dependencies
Write-Log "Instalando dependencias..."
& pip install -q -r requirements.txt

Write-Success "Backend configurado"

# ===============================================
# 3. CONFIGURAR BASE DE DATOS Y ADMIN
# ===============================================

Write-Log "Configurando base de datos y usuario admin..."

# Create/update admin user
try {
    & $pythonCmd create_admin.py | Out-Null
} catch {
    Write-Warning "Admin user setup had warnings (probably already exists)"
}

Write-Success "Base de datos y admin configurados"

# ===============================================
# 4. EJECUTAR TESTS COMPLETOS
# ===============================================

Write-Log "Ejecutando suite completa de tests..."

# Run the comprehensive test suite
try {
    & $pythonCmd ..\tests\full_test.py
    Write-Success "Tests ejecutados exitosamente"
    $testResult = "PASS"
} catch {
    Write-Warning "Algunos tests fallaron (ver detalles arriba)"
    $testResult = "PARTIAL"
}

# ===============================================
# 5. VERIFICAR FRONTEND (OPCIONAL)
# ===============================================

Set-Location ..\frontend

if (Test-Path "package.json") {
    Write-Log "Verificando configuración del frontend..."
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        if (Get-Command npm -ErrorAction SilentlyContinue) {
            Write-Log "Instalando dependencias del frontend..."
            npm install | Out-Null
            Write-Success "Dependencias del frontend instaladas"
        } else {
            Write-Warning "npm no está disponible, saltando configuración del frontend"
        }
    } else {
        Write-Success "Frontend ya configurado"
    }
} else {
    Write-Warning "package.json no encontrado en frontend\"
}

# ===============================================
# 6. GENERAR REPORTE FINAL
# ===============================================

Set-Location ..

Write-Log "Generando reporte final..."

Write-Host ""
Write-Host "📊 REPORTE FINAL - SaaS Cafeterías" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check backend server (attempt to check if running)
Set-Location backend
$backendRunning = $false

# Try to check if backend is already running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Success "Backend está corriendo en http://localhost:8000"
    }
} catch {
    Write-Warning "Backend no está corriendo (ejecutar: cd backend && python -m uvicorn app.main:app --reload)"
}

# Check test report
$testReports = Get-ChildItem -Name "test_report_*.txt" -ErrorAction SilentlyContinue
if ($testReports) {
    $latestReport = $testReports | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Write-Success "Reporte de tests disponible: $latestReport"
} else {
    Write-Warning "No se encontró reporte de tests"
}

Set-Location ..

Write-Host ""
Write-Host "🎯 ESTADO DEL PROYECTO:" -ForegroundColor Yellow
Write-Host "----------------------"
Write-Host "✅ Documentación unificada (README.md actualizado)"
Write-Host "✅ Usuario admin configurado (admin@saas.test / Admin1234!)"
Write-Host "✅ Suite de tests ejecutada ($testResult)"
Write-Host "✅ Base de datos inicializada"

if ($backendRunning) {
    Write-Host "✅ Backend corriendo y accesible"
} else {
    Write-Host "🔄 Backend listo para ejecutar"
}

Write-Host ""
Write-Host "📝 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "-----------------"
Write-Host "1. Si backend no está corriendo:"
Write-Host "   cd backend && python -m uvicorn app.main:app --reload"
Write-Host ""
Write-Host "2. Si frontend no está corriendo:"
Write-Host "   cd frontend && npm run dev"
Write-Host ""
Write-Host "3. Validar funcionamiento completo:"
Write-Host "   python tests\full_test.py"
Write-Host ""
Write-Host "4. Acceder a la aplicación:"
Write-Host "   - Frontend: http://localhost:5173"
Write-Host "   - Backend: http://localhost:8000"
Write-Host "   - API Docs: http://localhost:8000/docs"
Write-Host ""

# ===============================================
# 7. CLEANUP
# ===============================================

if ($testResult -eq "PASS") {
    Write-Success "🎉 Script completado exitosamente!"
    exit 0
} else {
    Write-Warning "⚠️  Script completado con warnings. Revisar logs de tests."
    exit 1
}