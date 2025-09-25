from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import api
from app.middleware.security import setup_security_middleware
from app.middleware.error_handler import setup_error_handlers
from app.db.db import create_tables

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    debug=settings.debug,
    description="🚀 Cafeteria IA - Sistema SaaS completo para gestión de cafeterías",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup error handling (debe ir primero)
setup_error_handlers(app, debug=settings.debug)

# Setup security middleware
setup_security_middleware(app)

# Include API routes
app.include_router(api.api_router, prefix=settings.api_v1_str)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Welcome to SaaS Cafeterías API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)