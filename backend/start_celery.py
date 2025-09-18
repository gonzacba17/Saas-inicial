#!/usr/bin/env python3
"""
Celery worker startup script for SaaS Inicial.
This script starts Celery workers for background task processing.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def start_celery_worker():
    """Start Celery worker with appropriate configuration."""
    try:
        # Check if Redis is available
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        print(f"🔗 Using Redis URL: {redis_url}")
        
        # Celery worker command
        cmd = [
            "celery",
            "-A", "app.services.celery_app:celery_app",
            "worker",
            "--loglevel=info",
            "--concurrency=2",
            "--queues=default,ai_queue,notifications,reports,payments"
        ]
        
        print("🚀 Starting Celery worker...")
        print(f"📄 Command: {' '.join(cmd)}")
        
        # Start the worker
        subprocess.run(cmd, cwd=backend_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Celery worker stopped by user")
    except Exception as e:
        print(f"❌ Error starting Celery worker: {e}")
        sys.exit(1)

def start_celery_beat():
    """Start Celery beat scheduler for periodic tasks."""
    try:
        cmd = [
            "celery",
            "-A", "app.services.celery_app:celery_app",
            "beat",
            "--loglevel=info"
        ]
        
        print("⏰ Starting Celery beat scheduler...")
        print(f"📄 Command: {' '.join(cmd)}")
        
        subprocess.run(cmd, cwd=backend_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Celery beat stopped by user")
    except Exception as e:
        print(f"❌ Error starting Celery beat: {e}")
        sys.exit(1)

def start_flower():
    """Start Flower web interface for monitoring."""
    try:
        cmd = [
            "celery",
            "-A", "app.services.celery_app:celery_app",
            "flower",
            "--port=5555"
        ]
        
        print("🌸 Starting Flower monitoring interface...")
        print(f"📄 Command: {' '.join(cmd)}")
        print("🌐 Web interface will be available at: http://localhost:5555")
        
        subprocess.run(cmd, cwd=backend_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Flower stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flower: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
🔧 Celery Management Script

Usage:
    python start_celery.py worker   # Start Celery worker
    python start_celery.py beat     # Start Celery beat scheduler
    python start_celery.py flower   # Start Flower monitoring
    
Environment Variables:
    REDIS_URL=redis://localhost:6379/0
    
Examples:
    # Start worker in development
    python start_celery.py worker
    
    # Start beat scheduler
    python start_celery.py beat
    
    # Monitor with Flower
    python start_celery.py flower
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "worker":
        start_celery_worker()
    elif command == "beat":
        start_celery_beat()
    elif command == "flower":
        start_flower()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: worker, beat, flower")
        sys.exit(1)