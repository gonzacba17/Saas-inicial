# Crear el script desde cero
cat > scripts/deploy_production.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}🚀 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

print_status "Starting production deployment..."

# Check prerequisites
print_status "Checking prerequisites..."
docker --version || exit 1
docker-compose --version || exit 1
[ -f ".env.production" ] || { print_error ".env.production not found"; exit 1; }
[ -f "docker-compose.production.yml" ] || { print_error "docker-compose.production.yml not found"; exit 1; }
print_success "Prerequisites OK"

# Create backup
print_status "Creating backup directory..."
mkdir -p backups
print_success "Backup directory ready"

# Build images
print_status "Building Docker images..."
docker-compose -f docker-compose.production.yml build
print_success "Images built"

# Start services
print_status "Starting services..."
docker-compose -f docker-compose.production.yml up -d
print_success "Services started"

# Wait for services
print_status "Waiting for services (30s)..."
sleep 30

# Health check
print_status "Running health check..."
for i in {1..30}; do
    if curl -f http://localhost/health 2>/dev/null; then
        print_success "Health check passed"
        break
    fi
    echo -n "."
    sleep 2
done

print_success "DEPLOYMENT SUCCESSFUL!"
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║     🎉 DEPLOYMENT SUCCESSFUL 🎉                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
EOFSCRIPT

# Hacer ejecutable
chmod +x scripts/deploy_production.sh

# Ejecutar
bash scripts/deploy_production.sh