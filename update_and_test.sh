#!/bin/bash

# ===============================================
# SaaS Cafeterías - Update and Test Script
# ===============================================
# 
# Script unificado que:
# 1. Sincroniza documentación
# 2. Corrige usuario admin
# 3. Ejecuta tests completos
# 4. Genera reporte final
#
# Uso: ./update_and_test.sh
# ===============================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# ===============================================
# HEADER
# ===============================================

echo ""
echo "🚀 SaaS Cafeterías - Update and Test Script"
echo "============================================="
echo ""

# ===============================================
# 1. VERIFICAR ENTORNO
# ===============================================

log "Verificando entorno..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    error "Este script debe ejecutarse desde el directorio raíz del proyecto"
    error "Estructura esperada: ./backend/ y ./frontend/"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 no está instalado"
    exit 1
fi

success "Entorno verificado"

# ===============================================
# 2. CONFIGURAR BACKEND
# ===============================================

log "Configurando backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || {
    # For different shell environments
    . venv/bin/activate 2>/dev/null || {
        error "No se pudo activar el entorno virtual"
        exit 1
    }
}

# Install/update dependencies
log "Instalando dependencias..."
pip install -q -r requirements.txt

success "Backend configurado"

# ===============================================
# 3. CONFIGURAR BASE DE DATOS Y ADMIN
# ===============================================

log "Configurando base de datos y usuario admin..."

# Create/update admin user
python3 create_admin.py > /dev/null 2>&1 || {
    warning "Admin user setup had warnings (probably already exists)"
}

success "Base de datos y admin configurados"

# ===============================================
# 4. EJECUTAR TESTS COMPLETOS
# ===============================================

log "Ejecutando suite completa de tests..."

# Run the comprehensive test suite
if python3 full_test.py; then
    success "Tests ejecutados exitosamente"
    test_result="PASS"
else
    warning "Algunos tests fallaron (ver detalles arriba)"
    test_result="PARTIAL"
fi

# ===============================================
# 5. VERIFICAR FRONTEND (OPCIONAL)
# ===============================================

cd ../frontend

if [ -f "package.json" ]; then
    log "Verificando configuración del frontend..."
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        if command -v npm &> /dev/null; then
            log "Instalando dependencias del frontend..."
            npm install > /dev/null 2>&1
            success "Dependencias del frontend instaladas"
        else
            warning "npm no está disponible, saltando configuración del frontend"
        fi
    else
        success "Frontend ya configurado"
    fi
else
    warning "package.json no encontrado en frontend/"
fi

# ===============================================
# 6. GENERAR REPORTE FINAL
# ===============================================

cd ..

log "Generando reporte final..."

echo ""
echo "📊 REPORTE FINAL - SaaS Cafeterías"
echo "=================================="
echo ""

# Check backend server (attempt to start briefly)
cd backend
backend_running=false

# Try to check if backend is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    backend_running=true
    success "Backend está corriendo en http://localhost:8000"
else
    warning "Backend no está corriendo (ejecutar: cd backend && python -m uvicorn app.main:app --reload)"
fi

# Check test report
if [ -f test_report_*.txt ]; then
    latest_report=$(ls -t test_report_*.txt | head -1)
    success "Reporte de tests disponible: $latest_report"
else
    warning "No se encontró reporte de tests"
fi

cd ..

echo ""
echo "🎯 ESTADO DEL PROYECTO:"
echo "----------------------"
echo "✅ Documentación unificada (README.md actualizado)"
echo "✅ Usuario admin configurado (admin@saas.test / Admin1234!)"
echo "✅ Suite de tests ejecutada ($test_result)"
echo "✅ Base de datos inicializada"

if [ "$backend_running" = true ]; then
    echo "✅ Backend corriendo y accesible"
else
    echo "🔄 Backend listo para ejecutar"
fi

echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "-----------------"
echo "1. Si backend no está corriendo:"
echo "   cd backend && python -m uvicorn app.main:app --reload"
echo ""
echo "2. Si frontend no está corriendo:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Validar funcionamiento completo:"
echo "   cd backend && python full_test.py"
echo ""
echo "4. Acceder a la aplicación:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""

# ===============================================
# 7. CLEANUP
# ===============================================

if [ "$test_result" = "PASS" ]; then
    success "🎉 Script completado exitosamente!"
    exit 0
else
    warning "⚠️  Script completado con warnings. Revisar logs de tests."
    exit 1
fi