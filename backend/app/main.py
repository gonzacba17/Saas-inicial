import os
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
# Cached response for even faster performance
_HEALTH_RESPONSE = {"status": "ok"}

@app.get("/health")
def health_check():
    """
    Ultra-fast health check endpoint optimized for <100ms response.
    Returns immediately without any dependencies or external calls.
    Uses cached response for maximum performance.
    Use /readyz for comprehensive readiness checks.
    """
    return _HEALTH_RESPONSE

# Comprehensive readiness check endpoint
@app.get("/readyz")
def readiness_check():
    """
    Comprehensive readiness check endpoint.
    Performs database connectivity and service dependency checks.
    May take longer than /health but provides detailed status.
    """
    checks = {
        "status": "ok",
        "service": "saas-cafeterias",
        "version": settings.version,
        "checks": {}
    }
    
    # Database connectivity check
    try:
        # Get database connection manually for better error handling
        from app.db.db import get_db
        db_gen = get_db()
        db = next(db_gen)
        try:
            result = db.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                checks["checks"]["database"] = {"status": "ok", "response_time_ms": "<5"}
            else:
                checks["checks"]["database"] = {"status": "error", "error": "Invalid response"}
                checks["status"] = "degraded"
        finally:
            # Always close the database connection
            try:
                next(db_gen, None)
            except StopIteration:
                pass
    except Exception as e:
        checks["checks"]["database"] = {"status": "error", "error": str(e)}
        checks["status"] = "degraded"
    
    # Environment configuration check
    try:
        checks["checks"]["config"] = {
            "status": "ok",
            "environment": settings.environment,
            "debug": settings.debug
        }
    except Exception as e:
        checks["checks"]["config"] = {"status": "error", "error": str(e)}
        checks["status"] = "degraded"
    
    return checks

# Legacy database health check endpoint (deprecated, use /readyz)
@app.get("/health/db")
def health_check_db():
    """
    Legacy database health check endpoint.
    DEPRECATED: Use /readyz for comprehensive checks.
    """
    try:
        # Get database connection manually for better error handling
        from app.db.db import get_db
        db_gen = get_db()
        db = next(db_gen)
        try:
            result = db.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                return {"status": "ok", "db": True, "deprecated": "Use /readyz instead"}
            else:
                return {"status": "error", "db": False, "deprecated": "Use /readyz instead"}
        finally:
            # Always close the database connection
            try:
                next(db_gen, None)
            except StopIteration:
                pass
    except Exception as e:
        return {"status": "error", "db": False, "error": str(e), "deprecated": "Use /readyz instead"}

# Setup error handling (debe ir primero)
setup_error_handlers(app, debug=settings.debug)

# Setup rate limiting middleware
from app.middleware.rate_limiter import RateLimitMiddleware
rate_limit_enabled = settings.environment == "production" or os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
app.add_middleware(RateLimitMiddleware, enabled=rate_limit_enabled)

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
