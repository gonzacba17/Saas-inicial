# ===============================================
# SCRIPT PARA RESOLVER PROBLEMAS DE WINDOWS
# Cafeteria IA - Correcciones específicas
# ===============================================

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "    SOLUCIONANDO PROBLEMAS DE WINDOWS" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# ===============================================
# 1. CONFIGURAR POLITICAS DE EJECUCION
# ===============================================

Write-Host "🔧 Configurando políticas de ejecución de PowerShell..." -ForegroundColor Yellow
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ Política de ejecución configurada" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  No se pudo cambiar la política (ejecuta como administrador si es necesario)" -ForegroundColor Yellow
}

# ===============================================
# 2. VERIFICAR/INSTALAR CHOCOLATEY (OPCIONAL)
# ===============================================

Write-Host "🍫 Verificando Chocolatey..." -ForegroundColor Yellow
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "✅ Chocolatey ya está instalado" -ForegroundColor Green
} else {
    Write-Host "📦 Chocolatey no encontrado (opcional para gestión de paquetes)" -ForegroundColor Yellow
    $installChoco = Read-Host "¿Instalar Chocolatey? (y/N)"
    if ($installChoco -eq 'y' -or $installChoco -eq 'Y') {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "✅ Chocolatey instalado" -ForegroundColor Green
    }
}

# ===============================================
# 3. VERIFICAR HERRAMIENTAS NECESARIAS
# ===============================================

Write-Host ""
Write-Host "🔍 Verificando herramientas necesarias..." -ForegroundColor Yellow

# Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
}

# Node.js
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js no encontrado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://nodejs.org/" -ForegroundColor Yellow
}

# Git
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitVersion = git --version
    Write-Host "✅ $gitVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Git no encontrado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://git-scm.com/" -ForegroundColor Yellow
}

# PostgreSQL
try {
    $pgVersion = psql --version 2>$null
    Write-Host "✅ PostgreSQL CLI disponible" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  PostgreSQL CLI no encontrado (normal si solo tienes el servidor)" -ForegroundColor Yellow
}

# ===============================================
# 4. CONFIGURAR VARIABLES DE ENTORNO
# ===============================================

Write-Host ""
Write-Host "🌐 Verificando variables de entorno..." -ForegroundColor Yellow

# Verificar PATH
$pathItems = $env:PATH -split ';'
$pythonInPath = $pathItems | Where-Object { $_ -like "*Python*" }
$nodeInPath = $pathItems | Where-Object { $_ -like "*nodejs*" -or $_ -like "*node*" }

if ($pythonInPath) {
    Write-Host "✅ Python en PATH" -ForegroundColor Green
} else {
    Write-Host "⚠️  Python no está en PATH" -ForegroundColor Yellow
}

if ($nodeInPath) {
    Write-Host "✅ Node.js en PATH" -ForegroundColor Green
} else {
    Write-Host "⚠️  Node.js no está en PATH" -ForegroundColor Yellow
}

# ===============================================
# 5. CONFIGURAR ARCHIVOS ESPECIFICOS DE WINDOWS
# ===============================================

Write-Host ""
Write-Host "📁 Configurando archivos específicos de Windows..." -ForegroundColor Yellow

# Crear .gitignore para Windows
$gitignoreContent = @"
# Windows specific files
Thumbs.db
ehthumbs.db
Desktop.ini
`$RECYCLE.BIN/
*.cab
*.msi
*.msix
*.msm
*.msp
*.lnk

# Python
__pycache__/
*.py[cod]
*`$py.class
venv/
.venv/
.env

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# Build outputs
dist/
build/
*.egg-info/
"@

if (Test-Path ".gitignore") {
    Write-Host "✅ .gitignore ya existe" -ForegroundColor Green
} else {
    Set-Content -Path ".gitignore" -Value $gitignoreContent
    Write-Host "✅ .gitignore creado" -ForegroundColor Green
}

# ===============================================
# 6. OPTIMIZACIONES DE RENDIMIENTO
# ===============================================

Write-Host ""
Write-Host "⚡ Aplicando optimizaciones de rendimiento..." -ForegroundColor Yellow

# Configurar npm para Windows
if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm config set fund false --global
    npm config set audit false --global
    Write-Host "✅ npm optimizado" -ForegroundColor Green
}

# Configurar pip para Windows
if (Get-Command pip -ErrorAction SilentlyContinue) {
    pip config set global.disable-pip-version-check true
    Write-Host "✅ pip optimizado" -ForegroundColor Green
}

# ===============================================
# 7. VERIFICAR PUERTOS
# ===============================================

Write-Host ""
Write-Host "🔌 Verificando puertos..." -ForegroundColor Yellow

$ports = @(5173, 8000)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠️  Puerto $port está en uso" -ForegroundColor Yellow
        Write-Host "   Proceso: $($connection.OwningProcess)" -ForegroundColor Gray
    } else {
        Write-Host "✅ Puerto $port disponible" -ForegroundColor Green
    }
}

# ===============================================
# RESUMEN
# ===============================================

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "    VERIFICACIONES COMPLETADAS" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "🎯 SIGUIENTE PASO:" -ForegroundColor Cyan
Write-Host "   Ejecuta: .\setup-complete.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 TIPS PARA WINDOWS:" -ForegroundColor Cyan
Write-Host "   • Ejecuta PowerShell como Administrador para mejor rendimiento" -ForegroundColor Gray
Write-Host "   • Añade exclusiones de antivirus para las carpetas del proyecto" -ForegroundColor Gray
Write-Host "   • Usa Windows Terminal para mejor experiencia" -ForegroundColor Gray
Write-Host ""