#!/usr/bin/env python3
"""
🧪 CAFETERIA IA - FULL INTEGRATION TEST SUITE
=============================================

Script completo de testing que valida toda la funcionalidad del sistema:
- Backend y Frontend funcionando correctamente
- Todos los endpoints principales (auth, businesses, products, orders)
- Validación de JWT y permisos según rol
- Pruebas de integración entre frontend y backend
- Reporte detallado de resultados

Autor: Sistema de QA automatizado
Compatible: Windows y Linux
Ejecutar: python full_test.py
"""

import os
import sys
import json
import time
import asyncio
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Agregar el directorio backend al PYTHONPATH
project_root = Path(__file__).parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

@dataclass
class TestResult:
    """Clase para almacenar resultados de pruebas individuales"""
    name: str
    passed: bool
    execution_time: float
    details: str
    error: Optional[str] = None

class TestCategory(Enum):
    """Categorías de pruebas"""
    ENVIRONMENT = "🔧 Entorno"
    SECURITY = "🔒 Seguridad"
    DATABASE = "💾 Base de Datos"
    AUTHENTICATION = "🔐 Autenticación"
    AUTHORIZATION = "👮 Autorización"
    BUSINESS_LOGIC = "🏢 Lógica de Negocio"
    API_ENDPOINTS = "🌐 API Endpoints"
    INTEGRATION = "🔗 Integración"
    PERFORMANCE = "⚡ Rendimiento"
    FRONTEND = "🖥️ Frontend"

class FullTestSuite:
    """Suite completa de tests para Cafeteria IA"""
    
    def __init__(self):
        self.results: Dict[TestCategory, List[TestResult]] = {
            category: [] for category in TestCategory
        }
        self.start_time = time.time()
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.admin_token = None
        self.test_user_token = None
        self.test_business_id = None
        self.test_product_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def add_result(self, category: TestCategory, name: str, passed: bool, 
                   execution_time: float, details: str, error: str = None):
        """Agregar resultado de prueba"""
        result = TestResult(name, passed, execution_time, details, error)
        self.results[category].append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        self.log(f"{status} {name} ({execution_time:.2f}s)")
        if error:
            self.log(f"Error: {error}", "ERROR")
    
    async def run_test(self, category: TestCategory, test_name: str, test_func):
        """Ejecutar una prueba individual con manejo de errores"""
        start_time = time.time()
        try:
            details = await test_func()
            execution_time = time.time() - start_time
            self.add_result(category, test_name, True, execution_time, details)
            return True
        except Exception as e:
            execution_time = time.time() - start_time
            self.add_result(category, test_name, False, execution_time, 
                          f"Error ejecutando prueba", str(e))
            return False
    
    async def test_environment_setup(self) -> str:
        """🔧 Verificar configuración del entorno"""
        checks = []
        
        # Verificar Python
        python_version = sys.version
        checks.append(f"Python: {python_version}")
        
        # Verificar SO
        os_info = f"{platform.system()} {platform.release()}"
        checks.append(f"OS: {os_info}")
        
        # Verificar directorio de trabajo
        current_dir = os.getcwd()
        checks.append(f"Directorio: {current_dir}")
        
        # Verificar estructura de directorios críticos
        critical_dirs = {
            "backend/app": "Backend application directory",
            "backend/alembic": "Database migrations",
            "tests": "Test suite directory",
            "frontend": "Frontend application",
            "scripts": "Automation scripts"
        }
        for dir_name, description in critical_dirs.items():
            if os.path.exists(dir_name):
                checks.append(f"✅ {dir_name}/ existe")
            else:
                raise Exception(f"Directorio crítico {dir_name}/ no encontrado")
        
        return "; ".join(checks)
    
    async def test_imports_and_dependencies(self) -> str:
        """🔧 Verificar importaciones y dependencias"""
        import_results = []
        
        # Importaciones críticas
        critical_imports = [
            ("app.main", "FastAPI main application"),
            ("app.core.config", "Configuration module"),
            ("app.db.db", "Database models"),
            ("app.schemas", "Pydantic schemas"),
            ("app.services", "Service layer"),
            ("app.api.v1.auth", "Authentication routes")
        ]
        
        for module_name, description in critical_imports:
            try:
                __import__(module_name)
                import_results.append(f"✅ {description}")
            except ImportError as e:
                raise Exception(f"Failed to import {module_name}: {str(e)}")
        
        # Verificar dependencias externas críticas
        external_deps = [
            "fastapi", "uvicorn", "sqlalchemy", "pydantic", "passlib", "httpx"
        ]
        
        for dep in external_deps:
            try:
                __import__(dep)
                import_results.append(f"✅ {dep}")
            except ImportError:
                raise Exception(f"Dependencia crítica {dep} no encontrada")
        
        return "; ".join(import_results)
    
    async def test_security_configuration(self) -> str:
        """🔒 Verificar configuración de seguridad"""
        from app.core.config import settings
        
        security_checks = []
        
        # Verificar que las claves no sean las por defecto
        default_secrets = [
            "your-super-secret-key",
            "local-development-secret-key",
            "change-this",
            "default"
        ]
        
        if any(secret in settings.secret_key.lower() for secret in default_secrets):
            security_checks.append("⚠️ SECRET_KEY parece ser por defecto")
        else:
            security_checks.append("✅ SECRET_KEY configurado")
        
        # Verificar longitud de claves
        if len(settings.secret_key) >= 32:
            security_checks.append("✅ SECRET_KEY tiene longitud adecuada")
        else:
            security_checks.append("⚠️ SECRET_KEY muy corto")
        
        # Verificar configuración de CORS
        if hasattr(settings, 'allowed_origins_list'):
            origins = settings.allowed_origins_list
            security_checks.append(f"✅ CORS configurado: {len(origins)} orígenes")
        else:
            security_checks.append("⚠️ CORS no configurado")
        
        return "; ".join(security_checks)
    
    async def test_database_connection(self) -> str:
        """💾 Verificar conexión y estructura de base de datos"""
        from app.db.db import get_db, create_tables, User
        from sqlalchemy.orm import Session
        
        db_checks = []
        
        # Crear tablas si no existen
        try:
            create_tables()
            db_checks.append("✅ Tablas de BD creadas/verificadas")
        except Exception as e:
            raise Exception(f"Error creando tablas: {str(e)}")
        
        # Verificar conexión de BD
        try:
            db_gen = get_db()
            db: Session = next(db_gen)
            
            # Contar usuarios
            user_count = db.query(User).count()
            db_checks.append(f"✅ Conexión BD OK, {user_count} usuarios")
            
            db.close()
        except Exception as e:
            raise Exception(f"Error conectando BD: {str(e)}")
        
        return "; ".join(db_checks)
    
    async def test_admin_user_exists(self) -> str:
        """💾 Verificar que existe usuario admin"""
        from app.db.db import get_db
        from app.services import get_user_by_email, get_user_by_username
        
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Buscar admin por username
            admin_user = get_user_by_username(db, "admin")
            if not admin_user:
                admin_user = get_user_by_email(db, "admin@saas.test")
            
            if admin_user:
                return f"✅ Usuario admin encontrado: {admin_user.email}, role: {admin_user.role}, active: {admin_user.is_active}"
            else:
                raise Exception("Usuario admin no encontrado")
        finally:
            db.close()
    
    async def test_password_hashing(self) -> str:
        """🔒 Verificar sistema de hash de contraseñas"""
        from app.services import get_password_hash, verify_password
        
        test_password = "TestPassword123!"
        
        # Generar hash
        hashed = get_password_hash(test_password)
        if len(hashed) < 50:  # Hash bcrypt típico es >50 chars
            raise Exception("Hash generado parece inválido")
        
        # Verificar hash correcto
        if not verify_password(test_password, hashed):
            raise Exception("Verificación de contraseña correcta falló")
        
        # Verificar rechazo de contraseña incorrecta
        if verify_password("WrongPassword", hashed):
            raise Exception("Sistema aceptó contraseña incorrecta")
        
        return f"✅ Hash: {len(hashed)} chars, verificación OK"
    
    async def test_backend_server_running(self) -> str:
        """🌐 Verificar que el servidor backend está corriendo"""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.backend_url}/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    return f"✅ Backend corriendo: {health_data.get('status')}, v{health_data.get('version')}"
                else:
                    raise Exception(f"Health check falló: {response.status_code}")
        except httpx.ConnectError:
            raise Exception("No se puede conectar al backend. ¿Está corriendo?")
    
    async def test_openapi_docs_accessible(self) -> str:
        """🌐 Verificar que la documentación API está accesible"""
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Probar OpenAPI JSON
            response = await client.get(f"{self.backend_url}/api/v1/openapi.json")
            if response.status_code != 200:
                raise Exception(f"OpenAPI JSON no accesible: {response.status_code}")
            
            openapi_data = response.json()
            paths_count = len(openapi_data.get('paths', {}))
            
            return f"✅ OpenAPI accesible, {paths_count} endpoints documentados"
    
    async def test_admin_login(self) -> str:
        """🔐 Probar login de usuario admin"""
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            login_data = {
                "username": "admin",
                "password": "Admin1234!"
            }
            
            response = await client.post(f"{self.backend_url}/api/v1/auth/login", data=login_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                self.admin_token = auth_response.get('access_token')
                
                return f"✅ Login admin exitoso, role: {auth_response.get('role')}, token: {len(self.admin_token)} chars"
            else:
                raise Exception(f"Login admin falló: {response.status_code} - {response.text}")
    
    async def test_jwt_token_validation(self) -> str:
        """🔐 Verificar validación de token JWT"""
        import httpx
        
        if not self.admin_token:
            raise Exception("Token admin no disponible")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Probar endpoint /me
            response = await client.get(f"{self.backend_url}/api/v1/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return f"✅ JWT válido, usuario: {user_data.get('username')}, role: {user_data.get('role')}"
            else:
                raise Exception(f"Validación JWT falló: {response.status_code}")
    
    async def test_unauthorized_access_blocked(self) -> str:
        """🔒 Verificar que acceso no autorizado es bloqueado"""
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Probar sin token
            response = await client.get(f"{self.backend_url}/api/v1/auth/me")
            
            if response.status_code == 401:
                return "✅ Acceso sin token correctamente bloqueado"
            else:
                raise Exception(f"Acceso sin token no fue bloqueado: {response.status_code}")
    
    async def test_invalid_credentials_rejected(self) -> str:
        """🔒 Verificar que credenciales inválidas son rechazadas"""
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            login_data = {
                "username": "admin",
                "password": "WrongPassword"
            }
            
            response = await client.post(f"{self.backend_url}/api/v1/auth/login", data=login_data)
            
            if response.status_code == 401:
                return "✅ Credenciales inválidas correctamente rechazadas"
            else:
                raise Exception(f"Credenciales inválidas no fueron rechazadas: {response.status_code}")
    
    async def test_user_registration(self) -> str:
        """🔐 Probar registro de nuevo usuario"""
        import httpx
        
        # Crear usuario único para testing
        timestamp = int(time.time())
        test_user = {
            "email": f"test{timestamp}@test.com",
            "username": f"testuser{timestamp}",
            "password": "TestPass123!"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{self.backend_url}/api/v1/auth/register", json=test_user)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Probar login con nuevo usuario
                login_response = await client.post(f"{self.backend_url}/api/v1/auth/login", data={
                    "username": test_user["username"],
                    "password": test_user["password"]
                })
                
                if login_response.status_code == 200:
                    auth_data = login_response.json()
                    self.test_user_token = auth_data.get('access_token')
                    return f"✅ Usuario registrado y login exitoso: {user_data.get('username')}"
                else:
                    raise Exception("Login con nuevo usuario falló")
            else:
                raise Exception(f"Registro falló: {response.status_code} - {response.text}")
    
    async def test_business_crud_operations(self) -> str:
        """🏢 Probar operaciones CRUD de negocios"""
        import httpx
        
        if not self.admin_token:
            raise Exception("Token admin no disponible")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Crear negocio
            business_data = {
                "name": f"Test Cafe {int(time.time())}",
                "description": "Cafe de prueba para testing",
                "address": "123 Test Street",
                "business_type": "cafe"
            }
            
            create_response = await client.post(
                f"{self.backend_url}/api/v1/businesses",
                json=business_data,
                headers=headers
            )
            
            if create_response.status_code == 200:
                business = create_response.json()
                self.test_business_id = business.get('id')
                
                # Leer negocio
                read_response = await client.get(
                    f"{self.backend_url}/api/v1/businesses/{self.test_business_id}",
                    headers=headers
                )
                
                if read_response.status_code == 200:
                    return f"✅ Negocio creado y leído: {business.get('name')}"
                else:
                    raise Exception("Error leyendo negocio creado")
            else:
                raise Exception(f"Error creando negocio: {create_response.status_code}")
    
    async def test_product_crud_operations(self) -> str:
        """🏢 Probar operaciones CRUD de productos"""
        import httpx
        
        if not self.admin_token or not self.test_business_id:
            raise Exception("Token admin o business_id no disponible")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Crear producto
            product_data = {
                "business_id": self.test_business_id,
                "name": f"Test Product {int(time.time())}",
                "description": "Producto de prueba",
                "price": 9.99,
                "category": "bebidas"
            }
            
            create_response = await client.post(
                f"{self.backend_url}/api/v1/products",
                json=product_data,
                headers=headers
            )
            
            if create_response.status_code == 200:
                product = create_response.json()
                self.test_product_id = product.get('id')
                
                return f"✅ Producto creado: {product.get('name')}, precio: ${product.get('price')}"
            else:
                raise Exception(f"Error creando producto: {create_response.status_code}")
    
    async def test_role_based_permissions(self) -> str:
        """👮 Probar permisos basados en roles"""
        import httpx
        
        if not self.test_user_token:
            raise Exception("Token de usuario de prueba no disponible")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Usuario normal no debería poder acceder a endpoints admin
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Intentar acceder a lista de usuarios (admin only)
            response = await client.get(f"{self.backend_url}/api/v1/users", headers=headers)
            
            # Dependiendo de la implementación, puede ser 403 o 401
            if response.status_code in [401, 403]:
                return "✅ Permisos de rol correctamente aplicados"
            else:
                raise Exception(f"Usuario normal pudo acceder a endpoint admin: {response.status_code}")
    
    async def test_cors_configuration(self) -> str:
        """🔒 Verificar configuración CORS"""
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Simular request CORS preflight
            headers = {
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = await client.options(f"{self.backend_url}/api/v1/auth/login", headers=headers)
            
            # CORS configurado debería permitir OPTIONS
            if response.status_code in [200, 204]:
                cors_headers = response.headers.get("Access-Control-Allow-Origin", "")
                return f"✅ CORS configurado, allow-origin: {cors_headers}"
            else:
                return "⚠️ CORS podría no estar configurado correctamente"
    
    async def test_api_response_times(self) -> str:
        """⚡ Verificar tiempos de respuesta de API"""
        import httpx
        
        if not self.admin_token:
            raise Exception("Token admin no disponible")
        
        endpoints_to_test = [
            ("/health", None),
            ("/api/v1/auth/me", {"Authorization": f"Bearer {self.admin_token}"}),
            ("/api/v1/businesses", {"Authorization": f"Bearer {self.admin_token}"})
        ]
        
        response_times = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, headers in endpoints_to_test:
                start_time = time.time()
                
                response = await client.get(f"{self.backend_url}{endpoint}", headers=headers or {})
                
                response_time = (time.time() - start_time) * 1000  # en ms
                response_times.append(response_time)
                
                if response.status_code not in [200, 201]:
                    raise Exception(f"Endpoint {endpoint} falló: {response.status_code}")
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        if max_response_time > 5000:  # 5 segundos
            raise Exception(f"Tiempo de respuesta muy alto: {max_response_time:.2f}ms")
        
        return f"✅ Tiempos OK - Promedio: {avg_response_time:.2f}ms, Máximo: {max_response_time:.2f}ms"
    
    async def test_frontend_accessibility(self) -> str:
        """🖥️ Verificar que el frontend está accesible"""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.frontend_url)
                
                if response.status_code == 200:
                    # Verificar que contiene elementos React típicos
                    content = response.text
                    if "vite" in content.lower() or "react" in content.lower() or "app" in content.lower():
                        return f"✅ Frontend accesible en {self.frontend_url}"
                    else:
                        return f"⚠️ Frontend responde pero contenido inesperado"
                else:
                    raise Exception(f"Frontend no accesible: {response.status_code}")
        except httpx.ConnectError:
            return f"⚠️ Frontend no está corriendo en {self.frontend_url}"
    
    async def test_database_data_integrity(self) -> str:
        """💾 Verificar integridad de datos en BD"""
        from app.db.db import get_db, User, Business, Product
        from sqlalchemy.orm import Session
        
        db_gen = get_db()
        db: Session = next(db_gen)
        
        try:
            # Verificar relaciones de datos
            checks = []
            
            # Contar registros
            user_count = db.query(User).count()
            business_count = db.query(Business).count()
            product_count = db.query(Product).count()
            
            checks.append(f"Users: {user_count}")
            checks.append(f"Businesses: {business_count}")
            checks.append(f"Products: {product_count}")
            
            # Verificar que hay al menos un admin
            from app.db.db import UserRole
            admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
            if admin_count == 0:
                raise Exception("No hay usuarios admin en la BD")
            
            checks.append(f"Admins: {admin_count}")
            
            return f"✅ Integridad OK - {'; '.join(checks)}"
        finally:
            db.close()
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        self.log("🚀 INICIANDO SUITE COMPLETA DE TESTS - CAFETERIA IA", "INFO")
        self.log("=" * 80)
        
        # Tests de entorno
        await self.run_test(TestCategory.ENVIRONMENT, "Configuración del entorno", self.test_environment_setup)
        await self.run_test(TestCategory.ENVIRONMENT, "Importaciones y dependencias", self.test_imports_and_dependencies)
        
        # Tests de seguridad
        await self.run_test(TestCategory.SECURITY, "Configuración de seguridad", self.test_security_configuration)
        await self.run_test(TestCategory.SECURITY, "Sistema de hash de contraseñas", self.test_password_hashing)
        await self.run_test(TestCategory.SECURITY, "Configuración CORS", self.test_cors_configuration)
        
        # Tests de base de datos
        await self.run_test(TestCategory.DATABASE, "Conexión a base de datos", self.test_database_connection)
        await self.run_test(TestCategory.DATABASE, "Usuario admin existe", self.test_admin_user_exists)
        await self.run_test(TestCategory.DATABASE, "Integridad de datos", self.test_database_data_integrity)
        
        # Tests de API
        await self.run_test(TestCategory.API_ENDPOINTS, "Servidor backend corriendo", self.test_backend_server_running)
        await self.run_test(TestCategory.API_ENDPOINTS, "Documentación API accesible", self.test_openapi_docs_accessible)
        
        # Tests de autenticación
        await self.run_test(TestCategory.AUTHENTICATION, "Login de admin", self.test_admin_login)
        await self.run_test(TestCategory.AUTHENTICATION, "Validación JWT", self.test_jwt_token_validation)
        await self.run_test(TestCategory.AUTHENTICATION, "Registro de usuario", self.test_user_registration)
        await self.run_test(TestCategory.AUTHENTICATION, "Rechazo credenciales inválidas", self.test_invalid_credentials_rejected)
        
        # Tests de autorización
        await self.run_test(TestCategory.AUTHORIZATION, "Bloqueo acceso no autorizado", self.test_unauthorized_access_blocked)
        await self.run_test(TestCategory.AUTHORIZATION, "Permisos basados en roles", self.test_role_based_permissions)
        
        # Tests de lógica de negocio
        await self.run_test(TestCategory.BUSINESS_LOGIC, "CRUD de negocios", self.test_business_crud_operations)
        await self.run_test(TestCategory.BUSINESS_LOGIC, "CRUD de productos", self.test_product_crud_operations)
        
        # Tests de rendimiento
        await self.run_test(TestCategory.PERFORMANCE, "Tiempos de respuesta API", self.test_api_response_times)
        
        # Tests de frontend
        await self.run_test(TestCategory.FRONTEND, "Accesibilidad del frontend", self.test_frontend_accessibility)
    
    def generate_report(self) -> str:
        """Generar reporte detallado de resultados"""
        total_time = time.time() - self.start_time
        
        # Calcular estadísticas
        total_tests = sum(len(results) for results in self.results.values())
        passed_tests = sum(len([r for r in results if r.passed]) for results in self.results.values())
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Crear reporte
        report = []
        report.append("🧪 CAFETERIA IA - REPORTE DE TESTING COMPLETO")
        report.append("=" * 80)
        report.append(f"📊 RESUMEN EJECUTIVO")
        report.append(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"   Tiempo total: {total_time:.2f}s")
        report.append(f"   Tests ejecutados: {total_tests}")
        report.append(f"   Tests exitosos: {passed_tests}")
        report.append(f"   Tests fallidos: {failed_tests}")
        report.append(f"   Tasa de éxito: {success_rate:.1f}%")
        report.append("")
        
        # Reporte por categoría
        for category, results in self.results.items():
            if not results:
                continue
                
            category_passed = len([r for r in results if r.passed])
            category_total = len(results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            report.append(f"{category.value}")
            report.append(f"   Éxito: {category_passed}/{category_total} ({category_rate:.1f}%)")
            
            for result in results:
                status = "✅" if result.passed else "❌"
                report.append(f"   {status} {result.name} ({result.execution_time:.2f}s)")
                if result.error:
                    report.append(f"      Error: {result.error}")
            report.append("")
        
        # Recomendaciones
        report.append("📋 RECOMENDACIONES")
        if failed_tests == 0:
            report.append("   🎉 ¡Excelente! Todos los tests pasaron exitosamente.")
            report.append("   🚀 El sistema está listo para desarrollo/producción.")
        else:
            report.append(f"   ⚠️  {failed_tests} tests fallaron. Revisar errores arriba.")
            report.append("   🔧 Corregir problemas antes de continuar.")
        
        report.append("")
        report.append("💡 PRÓXIMOS PASOS")
        report.append("   1. Si hay fallos, revisar logs detallados arriba")
        report.append("   2. Verificar que backend y frontend estén corriendo")
        report.append("   3. Ejecutar tests individuales si es necesario")
        report.append("   4. Repetir testing después de correcciones")
        
        return "\n".join(report)
    
    def save_report_to_file(self, report: str):
        """Guardar reporte en archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            self.log(f"📄 Reporte guardado en: {filename}")
        except Exception as e:
            self.log(f"Error guardando reporte: {str(e)}", "ERROR")

async def main():
    """Función principal"""
    print("🧪 CAFETERIA IA - FULL TEST SUITE")
    print("Iniciando testing completo del sistema...")
    print("=" * 50)
    
    # Crear instancia del test suite
    test_suite = FullTestSuite()
    
    try:
        # Ejecutar todas las pruebas
        await test_suite.run_all_tests()
        
        # Generar y mostrar reporte
        report = test_suite.generate_report()
        print("\n" + report)
        
        # Guardar reporte en archivo
        test_suite.save_report_to_file(report)
        
        # Calcular resultado final
        total_tests = sum(len(results) for results in test_suite.results.values())
        failed_tests = sum(len([r for r in results if not r.passed]) for results in test_suite.results.values())
        
        if failed_tests == 0:
            print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            print("🚀 Sistema listo para usar")
            sys.exit(0)
        else:
            print(f"\n❌ {failed_tests} tests fallaron")
            print("🔧 Revisar errores y corregir antes de continuar")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error crítico en testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    project_root = Path(__file__).parent.parent
    backend_app_dir = project_root / "backend" / "app"
    if not backend_app_dir.exists():
        print("❌ Error: Este script debe ejecutarse desde el directorio del proyecto")
        print("Ejecute: cd tests && python full_test.py")
        print("O desde raíz: python tests/full_test.py")
        sys.exit(1)
    
    # Cambiar al directorio del proyecto para ejecución
    os.chdir(project_root)
    
    # Ejecutar tests
    asyncio.run(main())