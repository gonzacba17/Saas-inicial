#!/bin/bash

# SaaS Cafeterías - Local Development Setup Script
# This script sets up the entire environment for local development

echo "🚀 Setting up SaaS Cafeterías for Local Development"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.11+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 20+ and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Backend Setup
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local not found. Please create it manually from .env.example"
    echo "   Basic .env.local should contain:"
    echo "   DATABASE_URL=sqlite:///./saas_cafeterias_local.db"
    echo "   SECRET_KEY=local-development-secret-key"
    echo "   DEBUG=true"
fi

# Initialize database and create admin user
echo "Initializing database and creating admin user..."
python3 create_admin.py

echo "✅ Backend setup completed!"

# Frontend Setup
echo ""
echo "🔧 Setting up Frontend..."
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF
fi

echo "✅ Frontend setup completed!"

# Final instructions
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 To start the development environment:"
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Admin User (for testing):"
echo "   Email: admin@saas.test"
echo "   Password: Admin1234!"
echo ""
echo "⚠️  Note: This setup uses SQLite for simplicity. For production,"
echo "   configure PostgreSQL and Redis for better performance."