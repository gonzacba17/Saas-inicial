from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.api.v1 import api
from app.middleware.security import setup_security_middleware
from app.middleware.error_handler import setup_error_handlers
from app.db.db import create_tables, get_db

# Create lifespan event handler  
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    debug=settings.debug,
    description="🚀 Cafeteria IA - Sistema SaaS completo para gestión de cafeterías",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ultra-fast health check endpoint (defined before middleware for maximum speed)
@app.get("/health")
def health_check():
    """
    Ultra-fast health check endpoint.
    Returns immediately without database or external service checks.
    Use /health/db for database connectivity verification.
    """
    return {"status": "ok"}

# Database health check endpoint (defined before middleware)
@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """
    Database health check endpoint.
    Performs a simple database connectivity test.
    """
    try:
        # Simple database connectivity test
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            return {"status": "ok", "db": True}
        else:
            return {"status": "error", "db": False}
    except Exception as e:
        return {"status": "error", "db": False, "error": str(e)}

# Setup error handling (debe ir primero)
setup_error_handlers(app, debug=settings.debug)

# Setup security middleware
setup_security_middleware(app)

# Include API routes
app.include_router(api.api_router, prefix=settings.api_v1_str)


@app.get("/")
def read_root():
    return {"message": "Welcome to SaaS Cafeterías API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)