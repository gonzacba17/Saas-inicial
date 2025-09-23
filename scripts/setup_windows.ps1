# SaaS Cafeterías - Windows PowerShell Setup Script
# Ejecutar como administrador o con permisos de desarrollador

Write-Host "Setting up SaaS Cafeterías for Local Development (Windows)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Check Python 3.11+
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[1-9]" -or $pythonVersion -match "Python 3\.[2-9][0-9]") {
        Write-Host "Python version: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "Python 3.11+ required. Current: $pythonVersion" -ForegroundColor Red
        Write-Host "Please install Python 3.11+ from https://python.org" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ and add to PATH" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Setting up Backend..." -ForegroundColor Blue
Set-Location backend

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env.local if it doesn't exist
if (!(Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    @"
# SaaS Cafeterías - Local Development Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database (SQLite for local development)
DATABASE_URL=sqlite:///./saas_cafeterias_local.db

# Security
SECRET_KEY=local-development-secret-key
JWT_SECRET_KEY=local-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=SaaS Cafeterías
VERSION=1.0.0

# Redis (optional for local dev)
REDIS_URL=redis://localhost:6379/0
REDIS_PORT=6379
REDIS_HOST=localhost

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173

# Optional external APIs
MERCADOPAGO_ACCESS_TOKEN=TEST-your-sandbox-token-here
MERCADOPAGO_SANDBOX=true
OPENAI_API_KEY=sk-your-openai-key-here

# Development settings
SQL_ECHO=false
AUTO_RELOAD=true
"@ | Out-File -FilePath ".env.local" -Encoding UTF8
}

# Initialize database and create admin user
Write-Host "Initializing database and creating admin user..." -ForegroundColor Yellow
python create_admin.py

Write-Host "Backend setup completed!" -ForegroundColor Green

# Frontend setup
Write-Host ""
Write-Host "Setting up Frontend..." -ForegroundColor Blue
Set-Location ../frontend

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

# Create .env for frontend if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating frontend .env file..." -ForegroundColor Yellow
    @"
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

Write-Host "Frontend setup completed!" -ForegroundColor Green

# Final instructions
Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the development environment:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Backend (Terminal 1 - PowerShell):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Frontend (Terminal 2):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Gray
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Admin User (for testing):" -ForegroundColor Cyan
Write-Host "   Email: admin@saas.test" -ForegroundColor White
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: Admin1234!" -ForegroundColor White
Write-Host ""
Write-Host "Troubleshooting Tips:" -ForegroundColor Yellow
Write-Host "   - If API docs don't load, check backend logs for errors" -ForegroundColor Gray
Write-Host "   - If login fails with 401, verify CORS and backend is running" -ForegroundColor Gray
Write-Host "   - If import errors occur, ensure PYTHONPATH includes backend directory" -ForegroundColor Gray
Write-Host "   - Use 'admin' as username, not email for login" -ForegroundColor Gray

# Return to root directory
Set-Location ..
