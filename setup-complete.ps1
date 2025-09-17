# ===============================================
# SCRIPT COMPLETO DE CONFIGURACIÓN
# Cafeteria IA - SaaS Project
# Windows PowerShell Setup
# ===============================================

param(
    [switch]$SkipFrontend,
    [switch]$OnlyMigrations,
    [switch]$OnlyAdmin,
    [switch]$Help
)

# Colores para output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorOutput "USO DEL SCRIPT:" $InfoColor
    Write-ColorOutput ".\setup-complete.ps1                 # Configuración completa" $InfoColor
    Write-ColorOutput ".\setup-complete.ps1 -OnlyMigrations # Solo ejecutar migraciones" $InfoColor
    Write-ColorOutput ".\setup-complete.ps1 -OnlyAdmin      # Solo crear usuario admin" $InfoColor
    Write-ColorOutput ".\setup-complete.ps1 -SkipFrontend   # Omitir configuración frontend" $InfoColor
    Write-ColorOutput ".\setup-complete.ps1 -Help           # Mostrar esta ayuda" $InfoColor
    exit 0
}

if ($Help) {
    Show-Help
}

Write-ColorOutput "=" * 80 $InfoColor
Write-ColorOutput "    CONFIGURACIÓN COMPLETA - CAFETERIA IA" $InfoColor
Write-ColorOutput "    Backend: FastAPI + PostgreSQL + Alembic" $InfoColor
Write-ColorOutput "    Frontend: React + Vite + TailwindCSS" $InfoColor
Write-ColorOutput "=" * 80 $InfoColor
Write-ColorOutput ""

# Verificar que estamos en el directorio correcto
$currentPath = Get-Location
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-ColorOutput "❌ Error: Ejecuta este script desde el directorio raíz del proyecto" $ErrorColor
    Write-ColorOutput "   Debe contener las carpetas 'backend' y 'frontend'" $ErrorColor
    exit 1
}

# ===============================================
# PASO 1: CONFIGURAR BACKEND
# ===============================================

if (-not $OnlyAdmin) {
    Write-ColorOutput "🔧 PASO 1: CONFIGURANDO BACKEND" $InfoColor
    Write-ColorOutput "================================" $InfoColor

    Set-Location "backend"

    # Verificar Python
    Write-ColorOutput "🐍 Verificando Python..." $InfoColor
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "✅ $pythonVersion" $SuccessColor
    }
    catch {
        Write-ColorOutput "❌ Python no encontrado. Instala Python 3.8+ desde python.org" $ErrorColor
        exit 1
    }

    # Crear/verificar entorno virtual
    Write-ColorOutput "📦 Configurando entorno virtual..." $InfoColor
    if (Test-Path "venv") {
        Write-ColorOutput "⚠️  Entorno virtual existe. Eliminando..." $WarningColor
        Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
    }

    python -m venv venv
    Write-ColorOutput "✅ Entorno virtual creado" $SuccessColor

    # Activar entorno virtual
    Write-ColorOutput "🔧 Activando entorno virtual..." $InfoColor
    $venvActivate = ".\venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) {
        & $venvActivate
        Write-ColorOutput "✅ Entorno virtual activado" $SuccessColor
    } else {
        Write-ColorOutput "❌ Error activando entorno virtual" $ErrorColor
        exit 1
    }

    # Actualizar pip
    Write-ColorOutput "📦 Actualizando pip..." $InfoColor
    python -m pip install --upgrade pip --quiet

    # Instalar dependencias
    Write-ColorOutput "📚 Instalando dependencias..." $InfoColor
    pip install -r requirements.txt --quiet
    Write-ColorOutput "✅ Dependencias instaladas" $SuccessColor

    # Verificar configuración
    Write-ColorOutput "🔍 Verificando configuración..." $InfoColor
    try {
        python -c "from app.core.config import settings; print(f'DB: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')"
        Write-ColorOutput "✅ Configuración verificada" $SuccessColor
    }
    catch {
        Write-ColorOutput "❌ Error en configuración. Verifica el archivo .env" $ErrorColor
        exit 1
    }

    Set-Location ".."
}

# ===============================================
# PASO 2: EJECUTAR MIGRACIONES
# ===============================================

if (-not $OnlyAdmin) {
    Write-ColorOutput ""
    Write-ColorOutput "🗂️  PASO 2: EJECUTANDO MIGRACIONES" $InfoColor
    Write-ColorOutput "===================================" $InfoColor

    Set-Location "backend"

    # Activar entorno virtual
    $venvActivate = ".\venv\Scripts\Activate.ps1"
    & $venvActivate

    # Verificar/crear directorio de versiones
    if (-not (Test-Path "alembic\versions")) {
        Write-ColorOutput "📁 Creando directorio de versiones..." $InfoColor
        New-Item -ItemType Directory -Path "alembic\versions" -Force
        New-Item -ItemType File -Path "alembic\versions\__init__.py" -Force
    }

    # Generar migración inicial
    Write-ColorOutput "📝 Generando migración inicial..." $InfoColor
    try {
        alembic revision --autogenerate -m "Initial migration - Create all tables"
        Write-ColorOutput "✅ Migración generada" $SuccessColor
    }
    catch {
        Write-ColorOutput "❌ Error generando migración: $_" $ErrorColor
        Write-ColorOutput "🔍 Verificando estado de Alembic..." $InfoColor
        alembic current
        Write-ColorOutput "🔍 Historial de migraciones:" $InfoColor
        alembic history
    }

    # Ejecutar migraciones
    Write-ColorOutput "🚀 Aplicando migraciones..." $InfoColor
    try {
        alembic upgrade head
        Write-ColorOutput "✅ Migraciones aplicadas exitosamente" $SuccessColor
    }
    catch {
        Write-ColorOutput "❌ Error aplicando migraciones: $_" $ErrorColor
        Write-ColorOutput "💡 Intentando inicializar Alembic..." $WarningColor
        try {
            alembic stamp head
            alembic revision --autogenerate -m "Initial migration"
            alembic upgrade head
            Write-ColorOutput "✅ Migraciones reparadas y aplicadas" $SuccessColor
        }
        catch {
            Write-ColorOutput "❌ Error crítico con migraciones. Verifica PostgreSQL" $ErrorColor
            exit 1
        }
    }

    Set-Location ".."
}

# ===============================================
# PASO 3: CREAR USUARIO ADMINISTRADOR
# ===============================================

Write-ColorOutput ""
Write-ColorOutput "👤 PASO 3: CREANDO USUARIO ADMINISTRADOR" $InfoColor
Write-ColorOutput "=========================================" $InfoColor

Set-Location "backend"

# Activar entorno virtual
$venvActivate = ".\venv\Scripts\Activate.ps1"
& $venvActivate

# Ejecutar script de creación de admin
Write-ColorOutput "🔐 Creando usuario administrador..." $InfoColor
try {
    python create_admin.py
    Write-ColorOutput "✅ Usuario administrador creado" $SuccessColor
}
catch {
    Write-ColorOutput "❌ Error creando administrador: $_" $ErrorColor
    Write-ColorOutput "🔍 Verificando tabla users..." $InfoColor
    python -c "
from app.db.session import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    result = db.execute(text('SELECT COUNT(*) FROM users'))
    count = result.scalar()
    print(f'✅ Tabla users existe con {count} registros')
except Exception as e:
    print(f'❌ Error con tabla users: {e}')
finally:
    db.close()
"
}

Set-Location ".."

# ===============================================
# PASO 4: CONFIGURAR FRONTEND
# ===============================================

if (-not $SkipFrontend -and -not $OnlyMigrations -and -not $OnlyAdmin) {
    Write-ColorOutput ""
    Write-ColorOutput "🎨 PASO 4: CONFIGURANDO FRONTEND" $InfoColor
    Write-ColorOutput "=================================" $InfoColor

    Set-Location "frontend"

    # Verificar Node.js
    Write-ColorOutput "📦 Verificando Node.js..." $InfoColor
    try {
        $nodeVersion = node --version
        Write-ColorOutput "✅ Node.js $nodeVersion" $SuccessColor
    }
    catch {
        Write-ColorOutput "❌ Node.js no encontrado. Instala desde nodejs.org" $ErrorColor
        exit 1
    }

    # Limpiar instalaciones previas
    Write-ColorOutput "🧹 Limpiando instalaciones previas..." $InfoColor
    if (Test-Path "node_modules") {
        Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    }
    if (Test-Path "package-lock.json") {
        Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
    }

    # Instalar dependencias
    Write-ColorOutput "📚 Instalando dependencias del frontend..." $InfoColor
    npm install
    Write-ColorOutput "✅ Dependencias del frontend instaladas" $SuccessColor

    # Verificar configuración
    Write-ColorOutput "🔍 Verificando configuración de Vite..." $InfoColor
    if (Test-Path "vite.config.ts") {
        Write-ColorOutput "✅ Vite configurado" $SuccessColor
    }
    if (Test-Path "tailwind.config.js") {
        Write-ColorOutput "✅ TailwindCSS configurado" $SuccessColor
    }
    if (Test-Path "postcss.config.cjs") {
        Write-ColorOutput "✅ PostCSS configurado" $SuccessColor
    }

    Set-Location ".."
}

# ===============================================
# PASO 5: VERIFICACIÓN FINAL
# ===============================================

Write-ColorOutput ""
Write-ColorOutput "🔍 PASO 5: VERIFICACIÓN FINAL" $InfoColor
Write-ColorOutput "==============================" $InfoColor

# Verificar login del admin
Write-ColorOutput "🔐 Verificando login de administrador..." $InfoColor
Set-Location "backend"
$venvActivate = ".\venv\Scripts\Activate.ps1"
& $venvActivate

try {
    python -c "
from app.services.auth import authenticate_user
from app.db.session import SessionLocal
db = SessionLocal()
user = authenticate_user(db, 'admin', 'TuPassword123')
if user:
    print('✅ Login de admin verificado correctamente')
    print(f'   Email: {user.email}')
    print(f'   Username: {user.username}')
    print(f'   Superusuario: {user.is_superuser}')
else:
    print('❌ Error: No se pudo verificar login de admin')
db.close()
"
    Write-ColorOutput "✅ Verificación de login exitosa" $SuccessColor
}
catch {
    Write-ColorOutput "❌ Error verificando login: $_" $ErrorColor
}

Set-Location ".."

# ===============================================
# RESUMEN FINAL
# ===============================================

Write-ColorOutput ""
Write-ColorOutput "=" * 80 $SuccessColor
Write-ColorOutput "    🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE" $SuccessColor
Write-ColorOutput "=" * 80 $SuccessColor
Write-ColorOutput ""
Write-ColorOutput "📋 RESUMEN:" $InfoColor
Write-ColorOutput "   ✅ Backend configurado (FastAPI + PostgreSQL)" $SuccessColor
Write-ColorOutput "   ✅ Migraciones ejecutadas" $SuccessColor
Write-ColorOutput "   ✅ Usuario administrador creado" $SuccessColor
if (-not $SkipFrontend) {
    Write-ColorOutput "   ✅ Frontend configurado (React + Vite + TailwindCSS)" $SuccessColor
}
Write-ColorOutput ""
Write-ColorOutput "🔑 CREDENCIALES DE ADMINISTRADOR:" $InfoColor
Write-ColorOutput "   Username: admin" $WarningColor
Write-ColorOutput "   Password: TuPassword123" $WarningColor
Write-ColorOutput ""
Write-ColorOutput "🚀 PARA INICIAR LOS SERVIDORES:" $InfoColor
Write-ColorOutput "   Backend:  .\start-backend.ps1" $InfoColor
Write-ColorOutput "   Frontend: .\start-frontend.ps1" $InfoColor
Write-ColorOutput "   Ambos:    .\start-all.ps1" $InfoColor
Write-ColorOutput ""
Write-ColorOutput "🌐 URLs:" $InfoColor
Write-ColorOutput "   Frontend: http://localhost:5173" $InfoColor
Write-ColorOutput "   Backend:  http://localhost:8000" $InfoColor
Write-ColorOutput "   API Docs: http://localhost:8000/docs" $InfoColor
Write-ColorOutput ""
Write-ColorOutput "✅ ¡Todo listo para usar!" $SuccessColor
Write-ColorOutput "=" * 80 $SuccessColor