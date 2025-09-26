# 🎯 Plan de Acción: Elevar Coverage al 85%

## 📊 Estado Actual
- **Coverage actual**: 40%
- **Meta requerida**: 85%
- **Gap a cubrir**: +45%

## 🔍 Análisis de Coverage por Módulo

### Módulos con Bajo Coverage (<50%)
1. **auth.py** (28%) - CRÍTICO
2. **businesses.py** (25%) - CRÍTICO  
3. **orders.py** (25%) - CRÍTICO
4. **payments.py** (25%) - CRÍTICO
5. **ai_service.py** (27%) - MEDIO
6. **secrets_service.py** (21%) - CRÍTICO

### Módulos con Coverage Aceptable (>80%)
1. **schemas.py** (97%) - ✅ EXCELENTE
2. **api.py** (100%) - ✅ EXCELENTE
3. **config.py** (84%) - ✅ BUENO

## 🎯 Plan de Implementación

### Fase 1: Endpoints Críticos (70% objetivo)
**Tiempo estimado**: 2-3 días

#### Tests para auth.py (CRÍTICO)
```python
# Crear: tests/test_auth_comprehensive.py
- test_login_success()
- test_login_invalid_credentials()  
- test_me_endpoint_all_scenarios()
- test_token_refresh()
- test_role_validation()
- test_user_registration()
```

#### Tests para businesses.py (CRÍTICO)
```python
# Expandir: tests/test_businesses_extended.py  
- test_create_business_validation()
- test_update_business_permissions()
- test_delete_business_cascade()
- test_business_owner_permissions()
- test_business_manager_permissions()
```

#### Tests para orders.py (CRÍTICO)
```python
# Crear: tests/test_orders_comprehensive.py
- test_create_order_flow()
- test_order_status_transitions()
- test_order_permissions()
- test_order_payment_integration()
```

#### Tests para payments.py (CRÍTICO)
```python
# Crear: tests/test_payments_comprehensive.py
- test_mercadopago_webhook()
- test_payment_status_validation()
- test_payment_security()
- test_refund_process()
```

### Fase 2: Servicios y Middleware (85% objetivo)
**Tiempo estimado**: 1-2 días

#### Tests para ai_service.py
```python
# Crear: tests/test_ai_service.py
- test_openai_integration()
- test_ai_fallback_scenarios()
- test_ai_response_validation()
```

#### Tests para secrets_service.py
```python
# Crear: tests/test_secrets_service.py  
- test_environment_validation()
- test_secret_encryption()
- test_configuration_loading()
```

#### Tests para middleware
```python
# Crear: tests/test_middleware_comprehensive.py
- test_logging_middleware()
- test_security_middleware()
- test_error_handler()
```

## 🛠️ Comandos de Implementación

### 1. Crear Tests Faltantes
```bash
# Crear estructura de tests
mkdir -p tests/unit tests/integration tests/security

# Tests unitarios críticos
touch tests/unit/test_auth_comprehensive.py
touch tests/unit/test_businesses_extended.py  
touch tests/unit/test_orders_comprehensive.py
touch tests/unit/test_payments_comprehensive.py

# Tests de integración
touch tests/integration/test_full_workflow.py
touch tests/integration/test_database_operations.py

# Tests de seguridad
touch tests/security/test_permission_validation.py
touch tests/security/test_input_validation.py
```

### 2. Ejecutar y Medir Coverage
```bash
# Instalar dependencias de testing
pip install pytest-mock factory-boy

# Ejecutar con coverage detallado
pytest --cov=backend/app --cov-report=html --cov-report=term-missing --cov-fail-under=85

# Generar reporte de gaps
pytest --cov=backend/app --cov-report=term-missing | grep TOTAL
```

### 3. Validar CI/CD
```bash
# Actualizar pytest.ini con nuevo threshold
sed -i 's/--cov-fail-under=80/--cov-fail-under=85/g' backend/pytest.ini

# Verificar CI/CD pase con nuevo coverage
git add . && git commit -m "feat: increase test coverage to 85%"
```

## 📈 Cronograma de Ejecución

### Día 1: Tests Críticos de Auth y Business
- ✅ auth.py → 80% coverage
- ✅ businesses.py → 75% coverage
- **Target día 1**: 60% overall coverage

### Día 2: Tests de Orders y Payments  
- ✅ orders.py → 75% coverage
- ✅ payments.py → 70% coverage
- **Target día 2**: 75% overall coverage

### Día 3: Tests de Servicios y Middleware
- ✅ ai_service.py → 60% coverage
- ✅ secrets_service.py → 60% coverage
- ✅ middleware → 70% coverage
- **Target día 3**: 85% overall coverage

## ✅ Criterios de Aceptación

### Coverage por Módulo (Mínimo)
- **auth.py**: ≥80%
- **businesses.py**: ≥75%  
- **orders.py**: ≥75%
- **payments.py**: ≥70%
- **ai_service.py**: ≥60%
- **Overall**: ≥85%

### Casos Críticos Cubiertos
- ✅ Flujos de autenticación completos
- ✅ Validación de permisos admin/user
- ✅ CRUD operations con validaciones
- ✅ Error handling (400/401/403/404/500)
- ✅ Integración de pagos
- ✅ Validación de entrada robusta

### Tests de Integración
- ✅ Login → CRUD → Logout flow
- ✅ Admin → Create Business → Manage Products
- ✅ User → Make Order → Process Payment
- ✅ Error scenarios → Recovery paths

## 🚀 Resultado Esperado

Al completar este plan:
- **Coverage**: 40% → 85% (+45%)
- **Tests críticos**: 100% cubiertos
- **CI/CD**: Pasa automáticamente
- **Calidad**: Production-ready
- **Roadmap**: ✅ Habilitado para continuar

---

**⚠️ IMPORTANTE**: No proceder con Plan A del roadmap hasta alcanzar 85% coverage y validar que todos los tests críticos pasen en CI/CD.