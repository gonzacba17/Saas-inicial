#!/usr/bin/env python3
"""
Deployment script for ModularBiz SaaS
Handles database migrations, environment setup, and production deployment.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"🔄 Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {command}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    if result.stdout:
        print(result.stdout)
    
    return result

def check_requirements():
    """Check if all required dependencies are installed."""
    print("🔍 Checking requirements...")
    
    try:
        import alembic
        print("✅ Alembic is available")
    except ImportError:
        print("❌ Alembic not found. Run: pip install alembic")
        sys.exit(1)
    
    try:
        import psycopg2
        print("✅ PostgreSQL driver is available")
    except ImportError:
        print("⚠️ PostgreSQL driver not found. For production, run: pip install psycopg2-binary")

def setup_environment(env: str):
    """Setup environment configuration."""
    print(f"🔧 Setting up {env} environment...")
    
    env_file = f".env.{env}" if env != "development" else ".env"
    example_file = f".env.{env}.example" if env == "production" else ".env.production.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(example_file):
            print(f"📋 Copying {example_file} to {env_file}")
            run_command(f"cp {example_file} {env_file}")
            print(f"⚠️ Please update {env_file} with your actual configuration values")
        else:
            print(f"❌ No example configuration found for {env} environment")
            return False
    
    print(f"✅ Environment file {env_file} is ready")
    return True

def run_migrations():
    """Run database migrations."""
    print("🗄️ Running database migrations...")
    
    # Check if alembic is initialized
    if not os.path.exists("alembic"):
        print("📦 Initializing Alembic...")
        run_command("alembic init alembic")
    
    # Generate initial migration if none exist
    versions_dir = Path("alembic/versions")
    if not any(versions_dir.glob("*.py")):
        print("📝 Creating initial migration...")
        run_command("alembic revision --autogenerate -m 'Initial migration'")
    
    # Run migrations
    print("⬆️ Applying migrations...")
    run_command("alembic upgrade head")
    
    print("✅ Database migrations completed")

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    run_command("pip install -r requirements.txt")
    print("✅ Dependencies installed")

def create_superuser():
    """Create a superuser account."""
    print("👤 Creating superuser account...")
    
    # This would typically be a separate script or management command
    print("ℹ️ Superuser creation should be done manually after deployment")
    print("   Use the /api/v1/auth/register endpoint with superuser privileges")

def test_deployment():
    """Test the deployment."""
    print("🧪 Testing deployment...")
    
    # Start the server in the background and test basic endpoints
    print("ℹ️ You can test the deployment by:")
    print("   1. Starting the server: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("   2. Checking health: curl http://localhost:8000/health")
    print("   3. Checking API docs: http://localhost:8000/docs")

def deploy(environment: str, skip_deps: bool = False, skip_migrations: bool = False):
    """Main deployment function."""
    print(f"🚀 Starting deployment for {environment} environment...")
    
    # Check requirements
    check_requirements()
    
    # Setup environment
    if not setup_environment(environment):
        return False
    
    # Install dependencies
    if not skip_deps:
        install_dependencies()
    
    # Run migrations
    if not skip_migrations:
        run_migrations()
    
    # Create superuser (optional)
    if environment == "production":
        create_superuser()
    
    # Test deployment
    test_deployment()
    
    print(f"✅ Deployment completed for {environment} environment!")
    print("\n📋 Next steps:")
    print("   1. Configure your web server (nginx, apache)")
    print("   2. Set up SSL certificates")
    print("   3. Configure monitoring and logging")
    print("   4. Set up backup procedures")
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Deploy ModularBiz SaaS")
    parser.add_argument(
        "environment",
        choices=["development", "staging", "production"],
        help="Deployment environment"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation"
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip database migrations"
    )
    
    args = parser.parse_args()
    
    success = deploy(
        environment=args.environment,
        skip_deps=args.skip_deps,
        skip_migrations=args.skip_migrations
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()