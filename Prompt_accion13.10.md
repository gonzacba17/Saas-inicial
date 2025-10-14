# 🎯 PROMPT DE ACCIÓN EJECUTIVO - SAAS CAFETERÍAS

## 📋 CONTEXTO DEL PROYECTO

**Proyecto**: Sistema SaaS de Gestión de Cafeterías  
**Repositorio**: https://github.com/gonzacba17/Saas-inicial  
**Estado Actual**: 72/100 - Production-ready con gaps críticos  
**Score de Riesgo**: 🟡 MEDIO-ALTO

### Stack Tecnológico
```
Frontend:  React 18 + TypeScript + Zustand + Tailwind + Vite
Backend:   FastAPI + Python 3.11 + SQLAlchemy + Alembic
Database:  PostgreSQL + Redis
Infra:     Docker + Prometheus + Grafana
```

### Situación Actual
El proyecto tiene **fundamentos sólidos** pero presenta **3 bloqueantes críticos** que impiden el despliegue a producción:

1. 🔴 **Testing Coverage Insuficiente**: 40% vs 85% requerido
2. 🔴 **Vulnerabilidades de Seguridad**: Credenciales expuestas + secretos débiles
3. 🟡 **Backups No Validados**: Sin garantía de recuperación ante desastres

---

## 🚨 BLOQUEANTES CRÍTICOS IDENTIFICADOS

### 1. Testing Coverage: 40% → 85% (CRÍTICO)
**Impacto**: Sin tests robustos, cualquier cambio puede romper funcionalidad existente.

**Módulos afectados**:
- `app/api/v1/auth.py`: 28% coverage (necesita 80%)
- `app/api/v1/businesses.py`: 25% coverage (necesita 75%)
- `app/api/v1/orders.py`: 25% coverage (necesita 75%)
- `app/api/v1/payments.py`: 25% coverage (necesita 70%)

**Tests faltantes estimados**: 45-50 tests unitarios + 10-15 tests de integración

### 2. Seguridad Comprometida (URGENTE)
**Vulnerabilidades detectadas**:

```markdown
🔴 CRÍTICO - Credenciales públicas en README:
- Email: admin@saas.test
- Password: Admin1234!
- Acción: Remover AHORA + limpiar git history

🔴 CRÍTICO - Secret key débil en .env:
- Actual: "development-secret-key-64-chars-minimum"
- Solución: Usar secrets.token_urlsafe(64)

🟠 ALTA - Sin HTTPS forzado:
- Tokens JWT pueden interceptarse
- Implementar HTTPSRedirectMiddleware

🟠 ALTA - Sin CSRF protection:
- Vulnerable a ataques cross-site
- Implementar CSRFMiddleware

🟡 MEDIA - Secrets en .env plano:
- Migrar a AWS Secrets Manager / Google Secret Manager
```

### 3. Backups Sin Validar (ALTA)
- Scripts existen pero nunca se probó una restauración real
- Sin monitoreo de éxito/fallo de backups
- No hay plan documentado de disaster recovery
- RPO/RTO no definidos

---

## 🎯 PLAN DE ACCIÓN INMEDIATO (2 SEMANAS)

### 📅 SEMANA 1: SEGURIDAD + TESTING SETUP

#### 🔴 DÍA 1 (LUNES) - URGENCIA MÁXIMA
**Foco**: Eliminar vulnerabilidades críticas de seguridad

```bash
# TAREA 1: Remover credenciales expuestas (1 hora)
□ Editar README.md y remover sección de credenciales
□ Mover credenciales a .env.example con placeholders
□ Commit: "security: remove exposed credentials from README"
□ Force push si es necesario (git history cleanup)

# TAREA 2: Generar secret key seguro (30 min)
□ Ejecutar en Python:
  python -c "import secrets; print(secrets.token_urlsafe(64))"
□ Actualizar .env con nuevo SECRET_KEY
□ Documentar en .env.example

# TAREA 3: Configurar secrets manager (2 horas)
□ Elegir proveedor (AWS Secrets Manager recomendado)
□ Migrar: MERCADOPAGO_ACCESS_TOKEN, OPENAI_API_KEY, DATABASE_PASSWORD
□ Actualizar código para leer desde secrets manager
□ Probar en ambiente dev

# TAREA 4: Forzar HTTPS y agregar security headers (1 hora)
□ Editar app/main.py:
  from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
  if settings.environment == "production":
      app.add_middleware(HTTPSRedirectMiddleware)
□ Agregar security headers (HSTS, X-Frame-Options, CSP)
```

**Entregables Día 1**:
- ✅ README sin credenciales
- ✅ SECRET_KEY robusto generado
- ✅ Secrets en manager externo
- ✅ HTTPS forzado en producción

---

#### 🟡 DÍA 2 (MARTES) - SEGURIDAD COMPLEMENTARIA
**Foco**: Completar hardening de seguridad

```bash
# TAREA 5: Implementar CSRF protection (2 horas)
□ pip install starlette-csrf
□ Agregar middleware en app/main.py
□ Configurar cookies: httponly=True, secure=True, samesite="lax"
□ Actualizar frontend para enviar CSRF token

# TAREA 6: Auditoría de dependencias (1 hora)
□ pip install pip-audit safety
□ Ejecutar: pip-audit --desc
□ Ejecutar: safety check
□ Actualizar dependencias vulnerables
□ Crear requirements.txt con versiones pinned

# TAREA 7: Rate limiting agresivo (1 hora)
□ Revisar middleware actual de rate limiting
□ Endurecer límites en endpoints críticos:
  - /auth/login: 5 requests/min
  - /auth/register: 3 requests/min
  - /payments/*: 10 requests/min
□ Agregar logs de rate limit hits
```

**Entregables Día 2**:
- ✅ CSRF protection activo
- ✅ Dependencias auditadas y actualizadas
- ✅ Rate limiting configurado

---

#### 🔧 DÍA 3 (MIÉRCOLES) - TESTING SETUP
**Foco**: Preparar infraestructura de testing

```bash
# TAREA 8: Configurar pytest-cov (2 horas)
□ pip install pytest pytest-cov pytest-asyncio faker
□ Crear pytest.ini con configuración:
  [tool:pytest]
  testpaths = tests
  python_files = test_*.py
  addopts = --cov=app --cov-report=html --cov-report=term --cov-fail-under=85
□ Crear conftest.py con fixtures base

# TAREA 9: Estructura de tests (1 hora)
□ Crear directorio: tests/unit/api/v1/
□ Crear directorio: tests/integration/
□ Crear directorio: tests/e2e/
□ Crear archivos base: test_auth.py, test_businesses.py, etc.

# TAREA 10: Fixtures y mocks (2 horas)
□ Crear fixture de client HTTP
□ Crear fixture de database session
□ Crear factory de usuarios/businesses/orders
□ Mock de servicios externos (MercadoPago, OpenAI)
```

**Código de ejemplo**:
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.core.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Test1234!"
    })
    return response.json()["access_token"]
```

**Entregables Día 3**:
- ✅ pytest-cov configurado
- ✅ Estructura de tests creada
- ✅ Fixtures base implementados

---

#### 🧪 DÍAS 4-5 (JUEVES-VIERNES) - TESTS UNITARIOS BATCH 1
**Foco**: Elevar coverage de auth.py y businesses.py

```python
# META: +27 tests → Coverage 40% → 65%

# tests/unit/api/v1/test_auth.py (+15 tests)
□ test_register_new_user_success
□ test_register_duplicate_email_fails
□ test_register_weak_password_fails
□ test_register_invalid_email_fails
□ test_login_valid_credentials_success
□ test_login_invalid_credentials_fails
□ test_login_returns_jwt_token
□ test_jwt_token_expiration
□ test_jwt_token_decode_valid
□ test_jwt_token_decode_expired_fails
□ test_password_hashing_is_bcrypt
□ test_password_verify_correct
□ test_password_verify_incorrect
□ test_role_assignment_on_register
□ test_refresh_token_generation

# tests/unit/api/v1/test_businesses.py (+12 tests)
□ test_create_business_as_owner_success
□ test_create_business_as_customer_fails
□ test_create_business_duplicate_name_fails
□ test_create_business_missing_required_fields
□ test_get_businesses_returns_list
□ test_get_business_by_id_success
□ test_get_business_by_id_not_found
□ test_update_business_as_owner_success
□ test_update_business_as_non_owner_fails
□ test_delete_business_as_owner_success
□ test_delete_business_with_orders_fails
□ test_business_products_relationship
```

**Entregables Días 4-5**:
- ✅ 27 tests nuevos
- ✅ Coverage: auth.py → 80%, businesses.py → 70%
- ✅ Coverage total → ~65%

---

### 📅 SEMANA 2: TESTING COMPLETO + BACKUPS

#### 🧪 DÍAS 6-7 (LUNES-MARTES) - TESTS UNITARIOS BATCH 2
**Foco**: Completar coverage de orders.py y payments.py

```python
# META: +18 tests → Coverage 65% → 85%

# tests/unit/api/v1/test_orders.py (+10 tests)
□ test_create_order_success
□ test_create_order_invalid_product_fails
□ test_create_order_out_of_stock_fails
□ test_order_status_transitions_valid
□ test_order_status_transitions_invalid_fails
□ test_update_order_status_as_owner
□ test_update_order_status_as_customer_fails
□ test_calculate_order_total_correctly
□ test_order_with_multiple_items
□ test_cancel_order_before_completion

# tests/unit/api/v1/test_payments.py (+8 tests)
□ test_create_payment_mercadopago_success
□ test_create_payment_invalid_amount_fails
□ test_payment_webhook_approved_updates_order
□ test_payment_webhook_rejected_updates_order
□ test_payment_webhook_invalid_signature_fails
□ test_refund_payment_success
□ test_refund_payment_already_refunded_fails
□ test_payment_status_transitions
```

**Entregables Días 6-7**:
- ✅ 18 tests nuevos
- ✅ Coverage: orders.py → 75%, payments.py → 70%
- ✅ Coverage total → ~80%

---

#### 🔗 DÍA 8 (MIÉRCOLES) - TESTS DE INTEGRACIÓN
**Foco**: Validar flujos completos end-to-end

```python
# tests/integration/test_complete_flows.py (+5 tests)
□ test_complete_user_journey:
  # Register → Login → Create business → Add products → Create order → Payment
  
□ test_business_owner_flow:
  # Create business → Add employee → Employee creates order
  
□ test_payment_flow_with_webhook:
  # Create order → Payment → Webhook → Order status updated
  
□ test_admin_permissions_flow:
  # Admin can access all businesses → CRUD operations
  
□ test_concurrent_order_creation:
  # Multiple users creating orders simultaneously
```

**Entregables Día 8**:
- ✅ 5 tests de integración
- ✅ Coverage total → 85%+
- ✅ Validación de flujos críticos

---

#### 💾 DÍAS 9-10 (JUEVES-VIERNES) - BACKUPS + DISASTER RECOVERY

```bash
# TAREA 11: Script de backup automatizado (3 horas)
□ Crear scripts/backup.sh:
  #!/bin/bash
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  BACKUP_DIR="/backups"
  
  # Backup PostgreSQL
  pg_dump $DATABASE_URL > $BACKUP_DIR/db_$TIMESTAMP.sql
  
  # Backup archivos estáticos
  tar -czf $BACKUP_DIR/files_$TIMESTAMP.tar.gz /app/uploads
  
  # Upload a S3
  aws s3 cp $BACKUP_DIR/ s3://saas-backups/ --recursive
  
  # Limpiar backups locales > 7 días
  find $BACKUP_DIR -mtime +7 -delete
  
□ Dar permisos de ejecución: chmod +x scripts/backup.sh
□ Probar ejecución manual

# TAREA 12: Test de restauración (4 horas)
□ Crear scripts/restore.sh
□ Ejecutar backup completo
□ Destruir base de datos de test
□ Restaurar desde backup
□ Validar integridad de datos:
  - Contar registros en cada tabla
  - Verificar relaciones FK
  - Validar archivos estáticos
□ Documentar tiempo de restauración (RTO)

# TAREA 13: Automatización con cron (1 hora)
□ Configurar cronjob:
  # Backup diario a las 2 AM
  0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
  
  # Backup semanal completo (domingos)
  0 3 * * 0 /app/scripts/backup_full.sh >> /var/log/backup.log 2>&1

# TAREA 14: Monitoreo de backups (2 horas)
□ Script que verifica último backup exitoso
□ Alerta si backup falla o es > 24 horas antiguo
□ Integrar con Prometheus
□ Dashboard en Grafana
```

**Entregables Días 9-10**:
- ✅ Script de backup automatizado
- ✅ Proceso de restauración validado y documentado
- ✅ Cronjobs configurados
- ✅ Monitoreo de backups activo

---

## 📊 CHECKLIST DE VALIDACIÓN FINAL

### Pre-Deploy a Staging

```markdown
## Seguridad ✅
- [ ] Credenciales removidas de README
- [ ] SECRET_KEY generado con secrets.token_urlsafe(64)
- [ ] Secrets migrados a secrets manager
- [ ] HTTPS forzado en producción
- [ ] CSRF protection implementado
- [ ] Rate limiting configurado
- [ ] Dependencias auditadas (pip-audit + safety)
- [ ] Security headers configurados

## Testing ✅
- [ ] Coverage ≥ 85% en módulos críticos
- [ ] auth.py: 80%+
- [ ] businesses.py: 75%+
- [ ] orders.py: 75%+
- [ ] payments.py: 70%+
- [ ] 50+ tests unitarios pasando
- [ ] 5+ tests de integración pasando
- [ ] CI/CD ejecutando tests automáticamente

## Backups ✅
- [ ] Script de backup creado y probado
- [ ] Restauración validada exitosamente
- [ ] Backups automáticos configurados (cron)
- [ ] Monitoreo de backups activo
- [ ] Documentado RTO (Recovery Time Objective)
- [ ] Documentado RPO (Recovery Point Objective)
- [ ] Plan de disaster recovery escrito

## Deployment ✅
- [ ] Ambiente staging configurado
- [ ] Variables de entorno correctas en staging
- [ ] Health checks funcionando
- [ ] Monitoreo con Prometheus/Grafana activo
- [ ] Logs centralizados
- [ ] Alertas configuradas
- [ ] Runbook de incidentes documentado
```

---

## 🚀 COMANDOS ÚTILES PARA EJECUTAR

### Testing
```bash
# Ejecutar todos los tests con coverage
pytest --cov=app --cov-report=html --cov-report=term

# Ejecutar solo tests unitarios
pytest tests/unit/ -v

# Ejecutar tests de un módulo específico
pytest tests/unit/api/v1/test_auth.py -v

# Ver reporte de coverage en HTML
python -m http.server 8080 -d htmlcov/
```

### Seguridad
```bash
# Auditoría de dependencias
pip-audit --desc
safety check

# Escaneo de seguridad del código
bandit -r app/ -ll

# Generar secret key seguro
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Backups
```bash
# Backup manual
./scripts/backup.sh

# Restauración
./scripts/restore.sh /backups/db_20241013_140000.sql

# Verificar último backup
ls -lth /backups/ | head -n 5

# Test de integridad
psql $DATABASE_URL -c "SELECT COUNT(*) FROM businesses;"
```

### Deployment
```bash
# Deploy a staging
./scripts/deploy.sh staging

# Smoke tests
curl -f https://staging-api.domain.com/health || exit 1

# Ver logs
docker-compose logs -f backend

# Rollback si es necesario
docker-compose down
docker-compose up -d --build
```

---

## 📞 SIGUIENTE PASO INMEDIATO

### ACCIÓN #1 (AHORA MISMO)
```bash
# 1. Crear branch de trabajo
git checkout -b feature/production-readiness

# 2. Remover credenciales del README
# Editar README.md manualmente y eliminar:
#   Email: admin@saas.test
#   Password: Admin1234!

# 3. Commit urgente
git add README.md
git commit -m "security: remove exposed credentials from README"
git push origin feature/production-readiness

# 4. Crear PR inmediato
# Ir a GitHub y crear Pull Request con título:
# "🔴 SECURITY: Remove exposed credentials"
```

### ACCIÓN #2 (SIGUIENTES 2 HORAS)
```bash
# 1. Generar secret key robusto
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Copiar output y reemplazar en .env

# 2. Instalar herramientas de testing
pip install pytest pytest-cov pytest-asyncio faker

# 3. Crear estructura de tests
mkdir -p tests/unit/api/v1
mkdir -p tests/integration
touch tests/conftest.py
touch tests/unit/api/v1/test_auth.py

# 4. Commit
git add .
git commit -m "chore: setup testing infrastructure"
```

---

## 📈 MÉTRICAS DE ÉXITO

### Objetivos de las 2 Semanas

| Métrica | Antes | Después | Status |
|---------|-------|---------|--------|
| **Test Coverage** | 40% | 85%+ | 🎯 |
| **Vulnerabilidades Críticas** | 3 | 0 | 🎯 |
| **Backup Validado** | ❌ | ✅ | 🎯 |
| **CI/CD Activo** | ❌ | ✅ | 🎯 |
| **Score General** | 72/100 | 85/100+ | 🎯 |

### KPIs de Producción (Post-Deploy)

```markdown
## Performance
- Tiempo de respuesta promedio: < 200ms
- P95 response time: < 500ms
- Throughput: > 1000 req/s

## Reliability
- Uptime: 99.9%
- MTTR (Mean Time To Recovery): < 1 hora
- Backup success rate: 100%

## Security
- Vulnerabilidades críticas: 0
- Security score OWASP: 90/100+
- Incident response time: < 15 minutos
```

---

## 🎯 RESUMEN EJECUTIVO PARA STAKEHOLDERS

**Situación Actual**:
El sistema SaaS de cafeterías tiene fundamentos técnicos sólidos (72/100) pero presenta 3 bloqueantes críticos que impiden su despliegue seguro a producción.

**Bloqueantes Identificados**:
1. Testing insuficiente (40% vs 85% requerido)
2. Vulnerabilidades de seguridad (credenciales expuestas)
3. Backups sin validar (riesgo de pérdida de datos)

**Plan de Acción**:
2 semanas de trabajo enfocado para resolver los 3 bloqueantes, dividido en:
- Semana 1: Seguridad + Setup de testing
- Semana 2: Completar tests + Validar backups

**Inversión Requerida**:
- 80 horas de desarrollo (1 desarrollador full-time)
- Costo estimado: $4,000 - $6,000 USD

**Resultado Esperado**:
- Sistema production-ready con 85%+ test coverage
- Vulnerabilidades críticas eliminadas
- Backups automatizados y validados
- Score aumentado de 72/100 a 85/100+
- Listo para despliegue a producción con confianza

**Próximos Pasos Después de las 2 Semanas**:
1. Deploy a staging (día 11)
2. QA y smoke tests (días 12-13)
3. Deploy a producción (día 14)
4. Monitoreo intensivo primera semana
5. Inicio de Fase 2: Funcionalidades avanzadas

---

## 📋 APÉNDICE: PLANTILLAS DE CÓDIGO

### Template: Test Unitario
```python
# tests/unit/api/v1/test_example.py
import pytest
from fastapi.testclient import TestClient

def test_example_endpoint_success(client, admin_token):
    """
    Test que el endpoint /example funciona correctamente
    con credenciales válidas.
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"name": "Test", "value": 123}
    
    # Act
    response = client.post("/api/v1/example", 
                          json=payload, 
                          headers=headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
    assert response.json()["value"] == 123

def test_example_endpoint_unauthorized(client):
    """
    Test que el endpoint rechaza requests sin autenticación.
    """
    payload = {"name": "Test"}
    response = client.post("/api/v1/example", json=payload)
    
    assert response.status_code == 401
    assert "unauthorized" in response.json()["detail"].lower()
```

### Template: Script de Backup
```bash
#!/bin/bash
# scripts/backup.sh

set -e  # Exit on error

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/backups}"
S3_BUCKET="${S3_BUCKET:-saas-backups}"

echo "[$(date)] Starting backup..."

# 1. Backup PostgreSQL
echo "[$(date)] Backing up database..."
pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# 2. Backup uploads directory
echo "[$(date)] Backing up files..."
tar -czf "$BACKUP_DIR/files_$TIMESTAMP.tar.gz" /app/uploads

# 3. Upload to S3
echo "[$(date)] Uploading to S3..."
aws s3 cp "$BACKUP_DIR/db_$TIMESTAMP.sql.gz" "s3://$S3_BUCKET/db/"
aws s3 cp "$BACKUP_DIR/files_$TIMESTAMP.tar.gz" "s3://$S3_BUCKET/files/"

# 4. Verify backup
echo "[$(date)] Verifying backup..."
if [ ! -f "$BACKUP_DIR/db_$TIMESTAMP.sql.gz" ]; then
    echo "ERROR: Database backup failed!"
    exit 1
fi

# 5. Cleanup old local backups
echo "[$(date)] Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "[$(date)] Backup completed successfully!"
```

---

**Documento creado**: Octubre 13, 2025  
**Prioridad**: 🔴 CRÍTICA  
**Timeline**: 2 semanas  
**Esfuerzo estimado**: 80 horas

---

*Este es un plan de acción ejecutable. Comienza por la ACCIÓN #1 inmediatamente.*