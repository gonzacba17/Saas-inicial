#!/bin/bash

# Deployment script for SaaS Cafeterías
# Supports development, staging, and production environments

set -e

# Configuration
ENVIRONMENT=${1:-development}
PROJECT_NAME="saas-cafeterias"
COMPOSE_FILE="docker-compose.yml"
OVERRIDE_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
    print_success "docker-compose is available"
}

# Function to create environment file
create_env_file() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_warning ".env file not found. Creating from .env.example"
            cp .env.example .env
            print_warning "Please edit .env file with your configuration before running again"
            exit 1
        else
            print_error ".env.example file not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Function to validate environment
validate_environment() {
    case $ENVIRONMENT in
        development|dev)
            ENVIRONMENT="development"
            OVERRIDE_FILE="docker-compose.override.yml"
            ;;
        production|prod)
            ENVIRONMENT="production"
            OVERRIDE_FILE="docker-compose.prod.yml"
            ;;
        staging)
            ENVIRONMENT="staging"
            OVERRIDE_FILE="docker-compose.staging.yml"
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            print_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
    
    print_success "Environment set to: $ENVIRONMENT"
}

# Function to build images
build_images() {
    print_status "Building Docker images for $ENVIRONMENT..."
    
    if [ -f "$OVERRIDE_FILE" ]; then
        docker-compose -f $COMPOSE_FILE -f $OVERRIDE_FILE build --no-cache
    else
        docker-compose -f $COMPOSE_FILE build --no-cache
    fi
    
    print_success "Images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting services for $ENVIRONMENT..."
    
    if [ -f "$OVERRIDE_FILE" ]; then
        docker-compose -f $COMPOSE_FILE -f $OVERRIDE_FILE up -d
    else
        docker-compose -f $COMPOSE_FILE up -d
    fi
    
    print_success "Services started successfully"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    docker-compose exec backend alembic upgrade head
    
    if [ $? -eq 0 ]; then
        print_success "Migrations completed successfully"
    else
        print_error "Migrations failed"
        exit 1
    fi
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Check backend health
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is healthy"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend health check failed"
            exit 1
        fi
        sleep 2
    done
    
    # Check frontend health (only in development)
    if [ "$ENVIRONMENT" = "development" ]; then
        for i in {1..30}; do
            if curl -f http://localhost:3000 > /dev/null 2>&1; then
                print_success "Frontend is healthy"
                break
            fi
            if [ $i -eq 30 ]; then
                print_error "Frontend health check failed"
                exit 1
            fi
            sleep 2
        done
    fi
}

# Function to show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    print_status "\nService URLs:"
    case $ENVIRONMENT in
        development)
            echo "Frontend: http://localhost:3000"
            echo "Backend API: http://localhost:8000"
            echo "API Docs: http://localhost:8000/docs"
            echo "Flower (Celery): http://localhost:5555"
            ;;
        production|staging)
            echo "Application: http://localhost"
            echo "API Docs: http://localhost/docs"
            echo "Flower (Celery): http://localhost:5555"
            ;;
    esac
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    docker-compose down
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to backup before deployment
backup_before_deploy() {
    if [ "$ENVIRONMENT" = "production" ]; then
        print_status "Creating backup before deployment..."
        docker-compose exec backup /backup.sh
        print_success "Backup completed"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [environment] [command]"
    echo ""
    echo "Environments:"
    echo "  development (default) - Local development with hot reload"
    echo "  staging              - Staging environment"
    echo "  production           - Production environment"
    echo ""
    echo "Commands:"
    echo "  deploy    - Full deployment (default)"
    echo "  build     - Build images only"
    echo "  start     - Start services only"
    echo "  stop      - Stop services"
    echo "  restart   - Restart services"
    echo "  logs      - Show logs"
    echo "  status    - Show service status"
    echo "  cleanup   - Stop services and cleanup"
    echo "  backup    - Create database backup"
    echo ""
    echo "Examples:"
    echo "  $0 development        # Deploy in development mode"
    echo "  $0 production deploy  # Deploy in production mode"
    echo "  $0 development logs   # Show development logs"
}

# Main deployment function
deploy() {
    print_status "Starting deployment for $ENVIRONMENT environment..."
    
    check_docker
    check_docker_compose
    create_env_file
    validate_environment
    
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_before_deploy
    fi
    
    build_images
    start_services
    run_migrations
    check_health
    show_status
    
    print_success "Deployment completed successfully!"
}

# Parse command line arguments
COMMAND=${2:-deploy}

case $COMMAND in
    deploy)
        deploy
        ;;
    build)
        check_docker
        validate_environment
        build_images
        ;;
    start)
        check_docker
        validate_environment
        start_services
        ;;
    stop)
        docker-compose down
        print_success "Services stopped"
        ;;
    restart)
        docker-compose restart
        print_success "Services restarted"
        ;;
    logs)
        docker-compose logs -f
        ;;
    status)
        validate_environment
        show_status
        ;;
    cleanup)
        cleanup
        ;;
    backup)
        docker-compose exec backup /backup.sh
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac