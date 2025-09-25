# 🧪 Instrucciones de Testing - SaaS 

## 📋 Organización de Tests

### Tests Unitarios Separados (Existentes)
```
tests/
├── test_auth.py              # 🔐 Autenticación (registro, login, JWT)
├── test_roles.py             # 👮 Roles y permisos de usuario
├── test_businesses.py        # 🏢 CRUD de negocios
├── test_orders.py            # 📋 Gestión de pedidos
├── test_payments.py          # 💳 Sistema de pagos
├── test_secrets.py           # 🔐 Manejo de secretos y configuración
├── test_performance_analysis.py  # ⚡ Análisis de rendimiento
├── test_business_flow_security.py  # 🛡️ Seguridad de flujos
└── full_test.py              # 🎯 Suite de integración completa
```

### Test de Integración Global (Nuevo)
**`full_test.py`** - Completamente reescrito para compatibilidad pytest:
- ✅ **Flujo lógico**: auth → roles → businesses → orders → payments → performance → security
- ✅ **Compatible pytest**: Sin clases con `__init__` propios
- ✅ **Clases de soporte** fuera de clases de test
- ✅ **Comentarios explicativos** en cada paso del flujo

## 🚀 Comandos de Ejecución

### 1. Ejecutar Todos los Tests
```bash
# Desde la raíz del proyecto
pytest tests/ -v

# O específicamente
pytest tests/ -v --tb=short
```

### 2. Ejecutar Solo el Test de Integración
```bash
# Test completo de integración
pytest tests/full_test.py -v

# Test específico del flujo principal
pytest tests/full_test.py::TestFullIntegrationFlow::test_full_integration_flow -v
```

### 3. Ejecutar Tests Unitarios Específicos
```bash
# Autenticación
pytest tests/test_auth.py -v

# Businesses CRUD
pytest tests/test_businesses.py -v

# Roles y permisos
pytest tests/test_roles.py -v

# Performance
pytest tests/test_performance_analysis.py -v

# Todos los módulos específicos
pytest tests/test_auth.py tests/test_businesses.py tests/test_orders.py -v
```

### 4. Tests con Coverage
```bash
# Coverage básico
pytest tests/ --cov=backend/app --cov-report=term-missing

# Coverage detallado con HTML
pytest tests/ --cov=backend/app --cov-report=html --cov-report=term-missing

# Coverage por módulos específicos
pytest tests/test_auth.py --cov=backend/app/api/v1/auth --cov-report=term-missing
```

## 🎯 Flujo del Test de Integración Global

### Paso 1: 🔐 Authentication Flow
- Registro de usuario test
- Login con credenciales válidas 
- Obtención de tokens JWT (user + admin)
- Validación con endpoint `/me`

### Paso 2: 👮 Roles and Permissions
- Verificar que usuario normal no accede a endpoints admin
- Confirmar que admin tiene permisos elevados
- Validar información de roles en respuestas

### Paso 3: 🏢 Business Operations (CRUD)
- Crear nuevo negocio con admin token
- Leer negocio creado
- Actualizar información del negocio
- Listar todos los negocios

### Paso 4: 📋 Order Operations
- Crear producto dentro del negocio
- Crear pedido con productos
- Leer pedido creado
- Validar integridad de datos

### Paso 5: 💳 Payment Operations
- Intentar crear preferencia de pago
- Validar endpoints de payments existen
- Manejo de errores sin MercadoPago real

### Paso 6: ⚡ Performance Metrics
- Medir tiempos de respuesta de endpoints críticos
- Validar thresholds de performance
- Identificar endpoints lentos

### Paso 7: 🛡️ Security Validations
- Verificar rechazo de requests sin autenticación
- Validar rechazo de tokens inválidos
- Confirmar que `/me` nunca retorna error 500
- Verificar headers CORS

## 📊 Características del Test Suite

### Compatibilidad Pytest
✅ **Sin problemas de inicialización**:
- Clases de soporte (`TestData`, `TestStatus`, `StepResult`) fuera de clases de test
- No usa `__init__` en clases de test
- Fixtures apropiados para datos compartidos

### Logging y Debugging  
✅ **Información detallada**:
```python
# Logs informativos durante ejecución
logger.info("🚀 Iniciando Full Integration Test Suite")
logger.info("✅ Auth module health check passed")

# Reportes detallados al final
📊 FULL INTEGRATION TEST REPORT
✅ Total Steps: 7
✅ Passed: 7/7  
⏱️ Total Duration: 3.45s
```

### Manejo de Errores
✅ **Robusto**:
- Timeouts configurables
- Manejo de excepciones por paso
- Assertions informativas con detalles
- Fallback para endpoints no configurados

## 🔧 Configuración Previa

### 1. Backend Ejecutándose
```bash
cd backend
python -m uvicorn app.main:app --reload
# Backend debe estar en http://localhost:8000
```

### 2. Usuario Admin Creado
```bash
cd backend
python create_admin.py
# Credenciales: admin / Admin1234!
```

### 3. Dependencias de Testing
```bash
pip install pytest pytest-cov httpx
```

## 📈 Métricas de Éxito

### Coverage Target
- **Meta global**: 85% coverage
- **Auth module**: 28% → 80%
- **Business module**: 25% → 75% 
- **Orders module**: 25% → 75%
- **Payments module**: 25% → 70%

### Performance Benchmarks
- **Health endpoint**: < 200ms
- **/auth/me**: < 300ms
- **/businesses**: < 500ms
- **Ningún endpoint**: > 2000ms (crítico)

### Security Validations
- ✅ Endpoints protegidos rechazan acceso sin auth (401/403)
- ✅ Tokens inválidos son rechazados
- ✅ Endpoint `/me` nunca retorna error 500
- ✅ Role-based access control funcional

## 🚨 Troubleshooting

### Error: "Backend not running"
```bash
# Verificar que backend está corriendo
curl http://localhost:8000/health

# Si no responde, iniciar backend
cd backend && python -m uvicorn app.main:app --reload
```

### Error: "Admin user not found"
```bash
# Crear usuario admin
cd backend && python create_admin.py

# Verificar en logs que se creó correctamente
```

### Error: "Import failed"
```bash
# Verificar PYTHONPATH
export PYTHONPATH=backend:$PYTHONPATH

# O ejecutar desde raíz del proyecto
cd /path/to/Saas-inicial && pytest tests/
```

### Tests Lentos
```bash
# Ejecutar con timeout más alto
pytest tests/full_test.py -v --timeout=30

# O tests específicos más rápidos
pytest tests/test_auth.py tests/test_roles.py -v
```

## ✅ Validación Final

Para confirmar que todo funciona:

```bash
# 1. Test rápido de health
curl http://localhost:8000/health

# 2. Test unitario simple
pytest tests/test_auth.py::test_register_user -v

# 3. Test de integración completo
pytest tests/full_test.py::TestFullIntegrationFlow::test_full_integration_flow -v

# 4. Coverage general
pytest tests/ --cov=backend/app --cov-report=term-missing
```

Si todos los pasos pasan, el suite de testing está funcionando correctamente y listo para desarrollo continuo.

---

**📞 Soporte**: Si encuentras problemas, revisar logs detallados con `-v` y verificar que el backend esté ejecutándose correctamente.