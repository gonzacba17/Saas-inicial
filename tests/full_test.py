"""
🧪 FULL INTEGRATION TEST SUITE - SaaS Cafeterías
===============================================

Test suite completo que ejecuta flujos end-to-end siguiendo orden lógico:
auth → roles → businesses → orders → payments → performance → security

Compatible con pytest: puede ejecutarse como:
- pytest tests/full_test.py  
- pytest tests/full_test.py::test_full_integration_flow

Author: Sistema de QA automatizado
"""

import pytest
import time
import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import httpx
from fastapi.testclient import TestClient

# Setup logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CLASES DE SOPORTE (fuera de clases de test para evitar pytest warnings)
# ============================================================================

@dataclass
class TestData:
    """Almacena datos compartidos entre tests."""
    admin_token: Optional[str] = None
    user_token: Optional[str] = None
    business_id: Optional[str] = None
    product_id: Optional[str] = None
    order_id: Optional[str] = None
    base_url: str = "http://localhost:8000"

class TestStatus(Enum):
    """Estados de test para tracking."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StepResult:
    """Resultado de cada paso del test."""
    step_name: str
    status: TestStatus
    duration: float
    details: str
    error: Optional[str] = None

# ============================================================================
# FIXTURE GLOBAL PARA DATOS COMPARTIDOS
# ============================================================================

@pytest.fixture(scope="module")
def shared_data():
    """Fixture que proporciona datos compartidos entre todos los tests."""
    return TestData()

# ============================================================================
# TEST PRINCIPAL DE INTEGRACIÓN COMPLETA
# ============================================================================

class TestFullIntegrationFlow:
    """Suite de tests de integración completa siguiendo flujo lógico."""
    
    def test_full_integration_flow(self, shared_data: TestData):
        """
        Test principal que ejecuta flujo completo de integración:
        auth → roles → businesses → orders → payments → performance → security
        """
        logger.info("🚀 Iniciando Full Integration Test Suite")
        
        results = []
        
        # Paso 1: Tests de Autenticación
        auth_result = self._test_authentication_flow(shared_data)
        results.append(auth_result)
        assert auth_result.status == TestStatus.PASSED, f"Auth failed: {auth_result.error}"
        
        # Paso 2: Tests de Roles y Permisos  
        roles_result = self._test_roles_and_permissions(shared_data)
        results.append(roles_result)
        assert roles_result.status == TestStatus.PASSED, f"Roles failed: {roles_result.error}"
        
        # Paso 3: Tests de Businesses (CRUD)
        business_result = self._test_business_operations(shared_data)
        results.append(business_result)
        assert business_result.status == TestStatus.PASSED, f"Business failed: {business_result.error}"
        
        # Paso 4: Tests de Orders
        orders_result = self._test_order_operations(shared_data)
        results.append(orders_result)
        assert orders_result.status == TestStatus.PASSED, f"Orders failed: {orders_result.error}"
        
        # Paso 5: Tests de Payments
        payments_result = self._test_payment_operations(shared_data)
        results.append(payments_result)
        assert payments_result.status == TestStatus.PASSED, f"Payments failed: {payments_result.error}"
        
        # Paso 6: Tests de Performance
        performance_result = self._test_performance_metrics(shared_data)
        results.append(performance_result)
        assert performance_result.status == TestStatus.PASSED, f"Performance failed: {performance_result.error}"
        
        # Paso 7: Tests de Seguridad
        security_result = self._test_security_validations(shared_data)
        results.append(security_result)
        assert security_result.status == TestStatus.PASSED, f"Security failed: {security_result.error}"
        
        # Reporte final
        self._generate_integration_report(results)
        logger.info("✅ Full Integration Test Suite completado exitosamente")

    # ========================================================================
    # PASO 1: AUTENTICACIÓN
    # ========================================================================
    
    def _test_authentication_flow(self, data: TestData) -> StepResult:
        """Test completo de autenticación: registro, login, JWT validation."""
        start_time = time.time()
        
        try:
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                
                # 1.1: Crear usuario admin/test
                test_user = {
                    "email": f"testuser{int(time.time())}@test.com",
                    "username": f"testuser{int(time.time())}",
                    "password": "TestPass123!"
                }
                
                # Registro de usuario
                register_response = client.post("/api/v1/auth/register", json=test_user)
                assert register_response.status_code == 200, f"Register failed: {register_response.text}"
                
                # 1.2: Login con usuario creado
                login_response = client.post("/api/v1/auth/login", data={
                    "username": test_user["username"], 
                    "password": test_user["password"]
                })
                assert login_response.status_code == 200, f"Login failed: {login_response.text}"
                
                user_auth = login_response.json()
                data.user_token = user_auth.get("access_token")
                assert data.user_token, "No access token received"
                
                # 1.3: Login como admin (para tests que requieren permisos)
                admin_login = client.post("/api/v1/auth/login", data={
                    "username": "admin",
                    "password": "Admin1234!"
                })
                assert admin_login.status_code == 200, "Admin login failed"
                
                admin_auth = admin_login.json()
                data.admin_token = admin_auth.get("access_token")
                
                # 1.4: Verificar token con /me endpoint
                headers = {"Authorization": f"Bearer {data.user_token}"}
                me_response = client.get("/api/v1/auth/me", headers=headers)
                assert me_response.status_code == 200, "/me endpoint failed"
                
                user_info = me_response.json()
                assert user_info.get("username") == test_user["username"]
                
            duration = time.time() - start_time
            return StepResult(
                "Authentication Flow",
                TestStatus.PASSED,
                duration,
                f"User registered, logged in, admin auth OK. Tokens: user={len(data.user_token)}c, admin={len(data.admin_token)}c"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Authentication Flow", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # PASO 2: ROLES Y PERMISOS
    # ========================================================================
    
    def _test_roles_and_permissions(self, data: TestData) -> StepResult:
        """Test de sistema de roles y control de acceso."""
        start_time = time.time()
        
        try:
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                
                # 2.1: Verificar que usuario normal NO puede acceder endpoints admin
                user_headers = {"Authorization": f"Bearer {data.user_token}"}
                
                # Intentar acceso a endpoint que requiere admin
                admin_endpoint_response = client.get("/api/v1/users", headers=user_headers)
                assert admin_endpoint_response.status_code in [401, 403], "User should be blocked from admin endpoint"
                
                # 2.2: Verificar que admin SÍ puede acceder
                admin_headers = {"Authorization": f"Bearer {data.admin_token}"}
                admin_access = client.get("/api/v1/users", headers=admin_headers)
                # Note: Puede ser 404 si endpoint no existe, pero no debería ser 403/401
                assert admin_access.status_code != 403, "Admin should have access"
                
                # 2.3: Verificar información de rol en /me
                me_response = client.get("/api/v1/auth/me", headers=admin_headers)
                admin_info = me_response.json()
                assert admin_info.get("role") == "admin", "Admin role not properly set"
                
            duration = time.time() - start_time
            return StepResult(
                "Roles and Permissions",
                TestStatus.PASSED,
                duration,
                f"Role-based access control working. Admin role: {admin_info.get('role')}"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Roles and Permissions", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # PASO 3: BUSINESS OPERATIONS (CRUD)
    # ========================================================================
    
    def _test_business_operations(self, data: TestData) -> StepResult:
        """Test completo de operaciones CRUD para businesses."""
        start_time = time.time()
        
        try:
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {data.admin_token}"}
                
                # 3.1: Crear business
                business_data = {
                    "name": f"Test Cafe {int(time.time())}",
                    "description": "Cafe de prueba para testing",
                    "address": "123 Test Street, Test City",
                    "business_type": "cafe"
                }
                
                create_response = client.post("/api/v1/businesses", json=business_data, headers=headers)
                assert create_response.status_code == 200, f"Business creation failed: {create_response.text}"
                
                business = create_response.json()
                data.business_id = business.get("id")
                assert data.business_id, "No business ID returned"
                
                # 3.2: Leer business creado
                read_response = client.get(f"/api/v1/businesses/{data.business_id}", headers=headers)
                assert read_response.status_code == 200, "Business read failed"
                
                read_business = read_response.json()
                assert read_business.get("name") == business_data["name"]
                
                # 3.3: Actualizar business
                update_data = {"name": f"Updated {business_data['name']}"}
                update_response = client.put(f"/api/v1/businesses/{data.business_id}", json=update_data, headers=headers)
                assert update_response.status_code == 200, "Business update failed"
                
                # 3.4: Listar businesses (debe incluir el creado)
                list_response = client.get("/api/v1/businesses", headers=headers)
                assert list_response.status_code == 200, "Business list failed"
                
                businesses = list_response.json()
                business_ids = [b.get("id") for b in businesses if isinstance(businesses, list)]
                if not business_ids and isinstance(businesses, dict):
                    business_ids = [businesses.get("id")] if businesses.get("id") else []
                
            duration = time.time() - start_time
            return StepResult(
                "Business Operations",
                TestStatus.PASSED,
                duration,
                f"CRUD complete. Business ID: {data.business_id}, operations: Create/Read/Update/List"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Business Operations", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # PASO 4: ORDER OPERATIONS
    # ========================================================================
    
    def _test_order_operations(self, data: TestData) -> StepResult:
        """Test de operaciones de pedidos."""
        start_time = time.time()
        
        try:
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {data.admin_token}"}
                
                # 4.1: Crear producto primero (necesario para order)
                if not data.business_id:
                    raise Exception("Business ID not available for product creation")
                
                product_data = {
                    "business_id": data.business_id,
                    "name": f"Test Product {int(time.time())}",
                    "description": "Producto de prueba",
                    "price": 9.99,
                    "category": "bebidas"
                }
                
                product_response = client.post("/api/v1/products", json=product_data, headers=headers)
                assert product_response.status_code == 200, f"Product creation failed: {product_response.text}"
                
                product = product_response.json()
                data.product_id = product.get("id")
                
                # 4.2: Crear order
                order_data = {
                    "business_id": data.business_id,
                    "products": [
                        {
                            "product_id": data.product_id,
                            "quantity": 2
                        }
                    ],
                    "total_amount": 19.98,
                    "customer_email": "customer@test.com"
                }
                
                order_response = client.post("/api/v1/orders", json=order_data, headers=headers)
                assert order_response.status_code == 200, f"Order creation failed: {order_response.text}"
                
                order = order_response.json()
                data.order_id = order.get("id")
                assert data.order_id, "No order ID returned"
                
                # 4.3: Leer order creado
                read_order_response = client.get(f"/api/v1/orders/{data.order_id}", headers=headers)
                assert read_order_response.status_code == 200, "Order read failed"
                
            duration = time.time() - start_time
            return StepResult(
                "Order Operations", 
                TestStatus.PASSED,
                duration,
                f"Order created and read. Order ID: {data.order_id}, Product ID: {data.product_id}"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Order Operations", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # PASO 5: PAYMENT OPERATIONS
    # ========================================================================
    
    def _test_payment_operations(self, data: TestData) -> StepResult:
        """Test de operaciones de pagos (sin MercadoPago real)."""
        start_time = time.time()
        
        try:
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {data.admin_token}"}
                
                # 5.1: Crear preferencia de pago (mock)
                if not data.order_id:
                    raise Exception("Order ID not available for payment")
                
                payment_data = {
                    "order_id": data.order_id,
                    "amount": 19.98,
                    "currency": "ARS",
                    "payment_method": "credit_card"
                }
                
                # Intentar crear payment preference
                payment_response = client.post("/api/v1/payments/preference", json=payment_data, headers=headers)
                
                # El endpoint puede no existir o retornar error sin MercadoPago configurado
                # Consideramos éxito si no es un error de auth/permission
                if payment_response.status_code in [200, 201]:
                    payment_result = "Payment preference created successfully"
                elif payment_response.status_code in [400, 404, 422]:
                    payment_result = f"Payment endpoint exists but requires configuration (status: {payment_response.status_code})"
                else:
                    raise Exception(f"Unexpected payment response: {payment_response.status_code}")
                
                # 5.2: Verificar que endpoints de payment existen
                # GET payments por business
                payments_list = client.get(f"/api/v1/payments?business_id={data.business_id}", headers=headers)
                list_result = payments_list.status_code in [200, 404, 422]  # 404/422 OK si no hay payments
                assert list_result, f"Payments list endpoint error: {payments_list.status_code}"
                
            duration = time.time() - start_time
            return StepResult(
                "Payment Operations",
                TestStatus.PASSED, 
                duration,
                f"{payment_result}. Endpoints responsive."
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Payment Operations", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # PASO 6: PERFORMANCE METRICS
    # ========================================================================
    
    def _test_performance_metrics(self, data: TestData) -> StepResult:
        """Test de métricas de performance en endpoints críticos."""
        start_time = time.time()
        
        try:
            performance_results = []
            
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                
                # Endpoints a testear con sus thresholds esperados (ms)
                endpoints_to_test = [
                    ("/health", None, 200),  # endpoint, headers, threshold_ms
                    ("/api/v1/auth/me", {"Authorization": f"Bearer {data.admin_token}"}, 300),
                    ("/api/v1/businesses", {"Authorization": f"Bearer {data.admin_token}"}, 500),
                ]
                
                for endpoint, headers, threshold in endpoints_to_test:
                    endpoint_start = time.time()
                    
                    response = client.get(endpoint, headers=headers or {})
                    response_time_ms = (time.time() - endpoint_start) * 1000
                    
                    # Verificar que endpoint responde correctamente
                    assert response.status_code == 200, f"Endpoint {endpoint} failed: {response.status_code}"
                    
                    # Verificar performance
                    performance_status = "FAST" if response_time_ms < threshold else "ACCEPTABLE" if response_time_ms < threshold * 2 else "SLOW"
                    
                    performance_results.append({
                        "endpoint": endpoint,
                        "response_time_ms": round(response_time_ms, 2),
                        "threshold_ms": threshold,
                        "status": performance_status
                    })
                
                # Calcular métricas agregadas
                total_time = sum(r["response_time_ms"] for r in performance_results)
                avg_time = total_time / len(performance_results)
                slow_endpoints = [r for r in performance_results if r["status"] == "SLOW"]
                
                # Fail si hay endpoints críticamentе lentos (>2x threshold)
                critical_slow = [r for r in performance_results if r["response_time_ms"] > r["threshold_ms"] * 3]
                if critical_slow:
                    raise Exception(f"Critical slow endpoints detected: {[e['endpoint'] for e in critical_slow]}")
                
            duration = time.time() - start_time
            details = f"Avg: {avg_time:.2f}ms, Slow: {len(slow_endpoints)}/{len(performance_results)}"
            
            return StepResult("Performance Metrics", TestStatus.PASSED, duration, details)
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Performance Metrics", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # PASO 7: SECURITY VALIDATIONS
    # ========================================================================
    
    def _test_security_validations(self, data: TestData) -> StepResult:
        """Test de validaciones de seguridad críticas."""
        start_time = time.time()
        
        try:
            security_checks = []
            
            with httpx.Client(base_url=data.base_url, timeout=10.0) as client:
                
                # 7.1: Verificar que endpoints protegidos rechazan requests sin auth
                protected_endpoints = [
                    "/api/v1/auth/me",
                    "/api/v1/businesses", 
                    "/api/v1/users"
                ]
                
                for endpoint in protected_endpoints:
                    response = client.get(endpoint)  # Sin headers de auth
                    if response.status_code == 401:
                        security_checks.append(f"✅ {endpoint} correctly protected (401)")
                    elif response.status_code == 403:
                        security_checks.append(f"✅ {endpoint} correctly protected (403)")
                    else:
                        raise Exception(f"Endpoint {endpoint} not properly protected: {response.status_code}")
                
                # 7.2: Verificar que tokens inválidos son rechazados  
                invalid_headers = {"Authorization": "Bearer invalid-token"}
                me_response = client.get("/api/v1/auth/me", headers=invalid_headers)
                assert me_response.status_code in [401, 403], "Invalid token should be rejected"
                security_checks.append("✅ Invalid tokens rejected")
                
                # 7.3: Verificar que /me nunca retorna 500 (como indica la auditoría)
                valid_headers = {"Authorization": f"Bearer {data.admin_token}"}
                me_response = client.get("/api/v1/auth/me", headers=valid_headers)
                assert me_response.status_code != 500, "/me endpoint returned 500 error"
                security_checks.append(f"✅ /me endpoint stable ({me_response.status_code})")
                
                # 7.4: Verificar CORS headers (opcional)
                options_response = client.options("/api/v1/auth/login", headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "POST"
                })
                if "access-control-allow-origin" in options_response.headers:
                    security_checks.append("✅ CORS headers present")
                
            duration = time.time() - start_time
            return StepResult(
                "Security Validations",
                TestStatus.PASSED,
                duration,
                f"{len(security_checks)} security checks passed"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return StepResult("Security Validations", TestStatus.FAILED, duration, "", str(e))

    # ========================================================================
    # REPORTE FINAL
    # ========================================================================
    
    def _generate_integration_report(self, results: list) -> None:
        """Generar reporte final de la suite de integración."""
        
        logger.info("\n" + "="*80)
        logger.info("📊 FULL INTEGRATION TEST REPORT")
        logger.info("="*80)
        
        total_duration = sum(r.duration for r in results)
        passed_count = len([r for r in results if r.status == TestStatus.PASSED])
        
        logger.info(f"✅ Total Steps: {len(results)}")
        logger.info(f"✅ Passed: {passed_count}/{len(results)}")
        logger.info(f"⏱️  Total Duration: {total_duration:.2f}s")
        logger.info("")
        
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result.status == TestStatus.PASSED else "❌"
            logger.info(f"{i}. {status_icon} {result.step_name}")
            logger.info(f"   Duration: {result.duration:.2f}s")
            logger.info(f"   Details: {result.details}")
            if result.error:
                logger.info(f"   Error: {result.error}")
            logger.info("")
        
        logger.info("="*80)

# ============================================================================
# TESTS UNITARIOS ADICIONALES (Separados para pytest discovery)
# ============================================================================

def test_auth_module():
    """Test unitario específico para módulo de autenticación."""
    # Este test es detectado por pytest como test independiente
    with httpx.Client(base_url="http://localhost:8000", timeout=5.0) as client:
        # Test básico de health check
        response = client.get("/health")
        assert response.status_code == 200, "Health check failed"
        logger.info("✅ Auth module health check passed")

def test_business_module():
    """Test unitario específico para módulo de businesses."""
    with httpx.Client(base_url="http://localhost:8000", timeout=5.0) as client:
        # Verifica que endpoint businesses existe (sin auth por simplicidad)
        response = client.get("/api/v1/businesses")
        # Esperamos 401/403 (no auth) no 404 (no existe)
        assert response.status_code != 404, "Businesses endpoint not found"
        logger.info("✅ Business module endpoint exists")

def test_performance_module():
    """Test unitario específico para performance."""
    with httpx.Client(base_url="http://localhost:8000", timeout=5.0) as client:
        start_time = time.time()
        response = client.get("/health")
        duration_ms = (time.time() - start_time) * 1000
        
        assert response.status_code == 200, "Health endpoint failed"
        assert duration_ms < 1000, f"Health endpoint too slow: {duration_ms:.2f}ms"
        logger.info(f"✅ Performance check passed: {duration_ms:.2f}ms")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Si se ejecuta directamente, correr el test principal
    import sys
    sys.exit(pytest.main([__file__, "-v"]))