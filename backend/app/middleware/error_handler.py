"""
Middleware robusto para manejo de errores en Cafeteria IA
Proporciona logging detallado y respuestas de error consistentes
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Optional

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para manejo centralizado de errores con:
    - Logging detallado de errores
    - IDs únicos de error para tracking
    - Respuestas consistentes
    - Ocultación de detalles internos en producción
    """

    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next):
        """Procesar request con manejo de errores"""
        # Skip error handling overhead for ultra-fast health endpoints
        if request.url.path in ["/health", "/readyz"]:
            return await call_next(request)
            
        error_id = str(uuid.uuid4())[:8]
        
        try:
            # Procesar request
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # HTTPException ya manejada por FastAPI, solo log si es error servidor
            if e.status_code >= 500:
                logger.error(
                    f"HTTP Error {error_id}: {e.status_code} - {e.detail} "
                    f"[{request.method} {request.url}]"
                )
            raise e
            
        except Exception as e:
            # Error no manejado - log completo y respuesta segura
            logger.error(
                f"Unhandled Error {error_id}: {str(e)} "
                f"[{request.method} {request.url}] "
                f"Traceback: {traceback.format_exc()}"
            )
            
            # Respuesta según entorno
            if self.debug:
                error_detail = {
                    "error_id": error_id,
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url),
                    "method": request.method
                }
            else:
                error_detail = {
                    "error_id": error_id,
                    "message": "Internal server error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "detail": error_detail
                }
            )

class ValidationErrorHandler:
    """
    Manejador especializado para errores de validación
    Proporciona mensajes claros y útiles para el frontend
    """
    
    @staticmethod
    def format_validation_error(exc_info) -> dict:
        """Formatear errores de validación Pydantic"""
        errors = []
        
        for error in exc_info.get('errors', []):
            # Handle both dict and string errors
            if isinstance(error, dict):
                field_path = ' -> '.join(str(loc) for loc in error.get('loc', []))
                errors.append({
                    "field": field_path,
                    "message": error.get('msg', 'Validation error'),
                    "type": error.get('type', 'validation_error'),
                    "input": error.get('input')
                })
            else:
                # Handle string errors
                errors.append({
                    "field": "unknown",
                    "message": str(error),
                    "type": "validation_error",
                    "input": None
                })
        
        return {
            "error": "validation_error",
            "message": "Invalid input data",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat()
        }

class DatabaseErrorHandler:
    """
    Manejador especializado para errores de base de datos
    Convierte errores técnicos en mensajes user-friendly
    """
    
    @staticmethod
    def handle_database_error(error: Exception) -> dict:
        """Manejar errores comunes de base de datos"""
        error_msg = str(error).lower()
        
        # Errores de integridad (duplicados, etc.)
        if "unique constraint" in error_msg or "duplicate" in error_msg:
            return {
                "error": "duplicate_entry",
                "message": "A record with this information already exists",
                "type": "integrity_error"
            }
        
        # Errores de foreign key
        elif "foreign key constraint" in error_msg:
            return {
                "error": "invalid_reference",
                "message": "Referenced record does not exist",
                "type": "foreign_key_error"
            }
        
        # Error de conexión
        elif "connection" in error_msg or "timeout" in error_msg:
            return {
                "error": "database_unavailable",
                "message": "Database is temporarily unavailable",
                "type": "connection_error"
            }
        
        # Error genérico de BD
        else:
            return {
                "error": "database_error",
                "message": "Database operation failed",
                "type": "database_error"
            }

class SecurityErrorHandler:
    """
    Manejador especializado para errores de seguridad
    Previene la exposición de información sensible
    """
    
    @staticmethod
    def handle_auth_error(error_type: str) -> dict:
        """Manejar errores de autenticación/autorización"""
        
        error_responses = {
            "invalid_credentials": {
                "error": "authentication_failed",
                "message": "Invalid username or password",
                "code": "INVALID_CREDENTIALS"
            },
            "token_expired": {
                "error": "token_expired",
                "message": "Authentication token has expired",
                "code": "TOKEN_EXPIRED"
            },
            "invalid_token": {
                "error": "invalid_token",
                "message": "Invalid authentication token",
                "code": "INVALID_TOKEN"
            },
            "insufficient_permissions": {
                "error": "access_denied",
                "message": "Insufficient permissions for this operation",
                "code": "ACCESS_DENIED"
            },
            "account_disabled": {
                "error": "account_disabled",
                "message": "Account is disabled",
                "code": "ACCOUNT_DISABLED"
            }
        }
        
        return error_responses.get(error_type, {
            "error": "security_error",
            "message": "Security validation failed",
            "code": "SECURITY_ERROR"
        })

def setup_error_handlers(app, debug: bool = False):
    """
    Configurar todos los manejadores de error en la aplicación FastAPI
    """
    
    # Agregar middleware de manejo de errores
    app.add_middleware(ErrorHandlingMiddleware, debug=debug)
    
    # Manejador para errores de validación
    @app.exception_handler(422)
    async def validation_exception_handler(request: Request, exc):
        """Manejar errores de validación Pydantic"""
        logger.warning(f"Validation error on {request.url}: {exc.detail}")
        
        return JSONResponse(
            status_code=422,
            content=ValidationErrorHandler.format_validation_error({
                'errors': exc.detail if hasattr(exc, 'detail') else []
            })
        )
    
    # Manejador para errores 404
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Manejar recursos no encontrados"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": "The requested resource was not found",
                "path": str(request.url.path),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Manejador para errores 401 (no autenticado)
    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc):
        """Manejar errores de autenticación"""
        return JSONResponse(
            status_code=401,
            content=SecurityErrorHandler.handle_auth_error("invalid_credentials")
        )
    
    # Manejador para errores 403 (no autorizado)
    @app.exception_handler(403)
    async def forbidden_handler(request: Request, exc):
        """Manejar errores de autorización"""
        return JSONResponse(
            status_code=403,
            content=SecurityErrorHandler.handle_auth_error("insufficient_permissions")
        )
    
    logger.info("Error handlers configured successfully")

# Utilidades para manejo de errores en endpoints
class ErrorResponseBuilder:
    """
    Builder para crear respuestas de error consistentes
    """
    
    @staticmethod
    def business_error(message: str, code: str = "BUSINESS_ERROR") -> HTTPException:
        """Crear error de lógica de negocio"""
        return HTTPException(
            status_code=400,
            detail={
                "error": "business_logic_error",
                "message": message,
                "code": code,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def not_found_error(resource: str, identifier: str = None) -> HTTPException:
        """Crear error de recurso no encontrado"""
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
            
        return HTTPException(
            status_code=404,
            detail={
                "error": "not_found",
                "message": message,
                "resource": resource,
                "identifier": identifier,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def authorization_error(action: str, resource: str = None) -> HTTPException:
        """Crear error de autorización"""
        message = f"Not authorized to {action}"
        if resource:
            message += f" {resource}"
            
        return HTTPException(
            status_code=403,
            detail=SecurityErrorHandler.handle_auth_error("insufficient_permissions")
        )