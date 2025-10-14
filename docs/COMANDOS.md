# 📚 Comandos Ejecutables del Proyecto SaaS Cafeterías

> Guía completa de todos los comandos disponibles en el proyecto

---

## 📑 Tabla de Contenidos

- [🐳 Docker & Servicios](#-docker--servicios)
- [🔧 Backend (FastAPI + Python)](#-backend-fastapi--python)
- [⚛️ Frontend (React + TypeScript)](#️-frontend-react--typescript)
- [🧪 Testing](#-testing)
- [🔐 Seguridad & Secrets](#-seguridad--secrets)
- [📊 Monitoring & Logs](#-monitoring--logs)
- [🚀 Deployment](#-deployment)
- [🛠️ Utilidades](#️-utilidades)

---

## 🐳 Docker & Servicios

### Iniciar todos los servicios

```bash
# Desarrollo
docker-compose up -d

# Producción
docker-compose -f docker-compose.prod.yml up -d

# Con monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Solo testing
docker-compose -f docker-compose.test.yml up -d
```

### Detener servicios

```bash
# Detener todos
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Detener producción
docker-compose -f docker-compose.prod.yml down
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f redis
docker-compose logs -f celery-worker
```

### Reconstruir servicios

```bash
# Reconstruir todo
docker-compose build

# Reconstruir un servicio específico
docker-compose build backend
docker-compose build frontend

# Rebuild sin caché
docker-compose build --no-cache
```

### Scripts Docker simplificados

```bash
# Desarrollo (wrapper script)
./scripts/docker-dev.sh

# Producción (wrapper script)
./scripts/docker-prod.sh

# Escanear imágenes de seguridad
./scripts/scan-images.sh
```

### Servicios individuales

```bash
# Solo base de datos
docker-compose up -d db

# Solo Redis
docker-compose up -d redis

# Backend + dependencias
docker-compose up -d db redis backend

# Frontend
docker-compose up -d frontend

# Celery worker
docker-compose up -d celery-worker

# Celery beat (tareas programadas)
docker-compose up -d celery-beat

# Flower (monitoring Celery)
docker-compose up -d flower
# Acceder: http://localhost:5555
```

---

## 🔧 Backend (FastAPI + Python)

### Entorno virtual

```bash
# Crear entorno virtual
cd backend
python -m venv venv

# Activar (Linux/Mac)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
```

### Servidor de desarrollo

```bash
cd backend

# Iniciar servidor dev
python start_dev.py
# URL: http://localhost:8000

# Con Uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Con hot-reload avanzado
uvicorn app.main:app --reload --reload-dir app
```

### Verificación y setup

```bash
cd backend

# Verificar configuración
python verify_setup.py

# Pre-start checks (ejecutado por Docker)
./prestart.sh
```

### Base de datos

```bash
cd backend

# Migraciones con Alembic
alembic upgrade head          # Aplicar migraciones
alembic downgrade -1          # Revertir última migración
alembic revision --autogenerate -m "mensaje"  # Crear migración
alembic current              # Ver versión actual
alembic history              # Ver historial

# Test conexión DB
python scripts/test_database_connection.py
```

### Administración

```bash
cd backend

# Crear admin (interactivo)
python create_admin.py

# Crear admin dev (automatizado)
python scripts/create_dev_admin.py
```

### Celery (tareas asíncronas)

```bash
cd backend

# Iniciar Celery worker
python start_celery.py

# Worker con nivel de log específico
celery -A app.services_directory.celery_app worker --loglevel=info

# Worker con concurrencia
celery -A app.services_directory.celery_app worker --concurrency=4

# Beat (tareas programadas)
celery -A app.services_directory.celery_app beat --loglevel=info

# Flower (UI de monitoring)
celery -A app.services_directory.celery_app flower --port=5555
# Acceder: http://localhost:5555
```

### Coverage de código

```bash
cd backend

# Ejecutar coverage
python run_coverage.py

# Ver reporte HTML
python run_coverage.py && open htmlcov/index.html
```

---

## ⚛️ Frontend (React + TypeScript)

### Instalación

```bash
cd frontend

# Instalar dependencias
npm install

# Instalación limpia
npm ci
```

### Desarrollo

```bash
cd frontend

# Servidor dev (Vite)
npm run dev
# URL: http://localhost:3000

# Preview build
npm run preview
```

### Build

```bash
cd frontend

# Build producción
npm run build

# Build con type-check
npm run type-check && npm run build
```

### Linting y formato

```bash
cd frontend

# Lint
npm run lint

# Lint con auto-fix
npm run lint:fix

# Type-check TypeScript
npm run type-check
```

### Testing (Jest)

```bash
cd frontend

# Ejecutar tests
npm test

# Tests con watch mode
npm run test:watch

# Coverage
npm run test:coverage

# Tests CI
npm run test:ci
```

---

## 🧪 Testing

### Backend (Pytest)

```bash
cd backend

# Todos los tests
pytest

# Tests con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth_comprehensive.py
pytest tests/test_orders.py
pytest tests/test_payments.py

# Test específico
pytest tests/test_auth_comprehensive.py::TestUserRegistration::test_register_new_user_success

# Con output detallado
pytest -vvs

# Solo tests rápidos (excluir slow)
pytest -m "not slow"

# Solo tests de integración
pytest -m integration

# Parallel execution
pytest -n auto

# Stop en primer fallo
pytest -x

# Ver print statements
pytest -s
```

### Scripts de testing automatizados

```bash
# Tests completos
python scripts/run_tests.py

# Tests completos con reporte
python scripts/run_tests_complete.py

# Tests con fix aplicado
python scripts/run_tests_fixed.py
```

### E2E Testing (Playwright)

```bash
cd e2e

# Instalar navegadores
npm run install-browsers

# Instalar dependencias del sistema
npm run install-deps

# Ejecutar tests E2E
npm test

# UI mode (interactivo)
npm run test:ui

# Headed mode (ver navegador)
npm run test:headed

# Debug mode
npm run test:debug

# Ver reporte
npm run test:report

# Code generation
npm run test:codegen
```

### Validación completa

```bash
# Validar solución completa
python validate_solution.py
```

---

## 🔐 Seguridad & Secrets

### Git Secrets

```bash
# Setup git-secrets
./setup_git_secrets.sh

# Escanear repositorio
git secrets --scan

# Escanear historial completo
git secrets --scan-history
```

### Remediar secrets expuestos

```bash
# Script de remediación automática
./remediate_secrets.sh

# Ver patterns de secrets
cat .git-secrets-patterns
```

### Generar secrets

```bash
cd backend

# Generar nuevos secrets
python scripts/generate_secrets.py

# Generar y actualizar .env
python scripts/generate_secrets.py --update-env
```

---

## 📊 Monitoring & Logs

### Prometheus + Grafana

```bash
# Iniciar stack de monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Acceso a servicios:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)
# - AlertManager: http://localhost:9093
```

### Logs centralizados (ELK)

```bash
# Iniciar Logstash
docker-compose -f monitoring/docker-compose.monitoring.yml up -d logstash

# Ver logs en Elasticsearch
curl http://localhost:9200/_cat/indices

# Filebeat logs
docker-compose -f monitoring/docker-compose.monitoring.yml up -d filebeat
```

### Health checks

```bash
# Backend health
curl http://localhost:8000/health

# Backend readiness
curl http://localhost:8000/readyz

# DB health (legacy)
curl http://localhost:8000/health/db

# Frontend health (nginx)
curl http://localhost:80
```

---

## 🚀 Deployment

### Deploy producción

```bash
cd backend

# Deploy script
python deploy.py

# Deploy con Docker
docker-compose -f docker-compose.prod.yml up -d --build

# Deploy con secrets
docker-compose -f docker-compose.prod.yml -f docker-compose.secrets.yml up -d
```

### Pre-deployment checks

```bash
# Verificar setup
cd backend
python verify_setup.py

# Ejecutar pre-start
./prestart.sh

# Tests de integración
pytest tests/test_integration.py

# Tests de seguridad
pytest tests/test_security.py
pytest tests/test_security_fixes.py

# Performance tests
pytest tests/test_performance.py
```

### Iniciar servicios manualmente

```bash
# Script de inicio general
./start.sh

# Backend manual
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend manual (después de build)
cd frontend
npm run build
npx serve -s dist -p 3000
```

---

## 🛠️ Utilidades

### Gestión de base de datos

```bash
# Acceso directo a PostgreSQL
docker-compose exec db psql -U saasuser -d saas_cafeterias

# Backup
docker-compose exec db pg_dump -U saasuser saas_cafeterias > backup.sql

# Restore
docker-compose exec -T db psql -U saasuser saas_cafeterias < backup.sql

# Ver tablas
docker-compose exec db psql -U saasuser -d saas_cafeterias -c "\dt"
```

### Redis CLI

```bash
# Acceso a Redis
docker-compose exec redis redis-cli

# Ver keys
docker-compose exec redis redis-cli KEYS '*'

# Flush cache
docker-compose exec redis redis-cli FLUSHALL
```

### Limpiar sistema

```bash
# Limpiar containers detenidos
docker-compose rm -f

# Limpiar volúmenes no usados
docker volume prune

# Limpiar imágenes no usadas
docker image prune -a

# Limpieza completa Docker
docker system prune -a --volumes
```

### Python virtual env (Windows)

```bash
# Setup UTF-8 en Windows
scripts\setup_windows_utf8.bat
```

### Variables de entorno

```bash
# Ver variables actuales
printenv | grep POSTGRES
printenv | grep REDIS

# Cargar .env
export $(cat .env | xargs)

# Crear .env desde template
cp .env.example .env
```

---

## 📝 Comandos útiles por contexto

### Desarrollo local completo

```bash
# 1. Levantar infraestructura
docker-compose up -d db redis

# 2. Backend
cd backend
source venv/bin/activate  # o venv\Scripts\activate en Windows
python start_dev.py

# 3. Frontend (nueva terminal)
cd frontend
npm run dev

# 4. Celery worker (nueva terminal)
cd backend
python start_celery.py
```

### Testing completo antes de commit

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
python run_coverage.py

# Frontend
cd frontend
npm run lint
npm run type-check
npm run test:ci

# E2E
cd e2e
npm test
```

### CI/CD local simulation

```bash
# Simular pipeline CI
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Ejecutar todos los checks
./scripts/run_tests_complete.py
pytest tests/test_security.py
npm run --prefix frontend test:ci
npm run --prefix e2e test
```

---

## 🔗 URLs de Servicios (Desarrollo)

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **ReDoc** | http://localhost:8000/redoc | API Documentation |
| **Frontend** | http://localhost:3000 | React App |
| **Flower** | http://localhost:5555 | Celery Monitoring |
| **Grafana** | http://localhost:3001 | Metrics Dashboard |
| **Prometheus** | http://localhost:9090 | Metrics Server |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache & Queue |

---

## 📌 Notas Importantes

### Testing
- ✅ **108 tests** pasando en backend
- ✅ Coverage > 80% en componentes críticos
- ⚠️ Ejecutar `TESTING=true` para tests sin middlewares

### Docker
- 🐳 Usar `-d` para modo detached
- 📊 Monitorear con `docker stats`
- 🔍 Logs con `-f` para follow

### Seguridad
- 🔐 Nunca commitear `.env` o secrets
- 🛡️ Ejecutar `git-secrets` antes de push
- 🔑 Rotar secrets regularmente con `generate_secrets.py`

---

## 🆘 Troubleshooting

### Puerto ocupado
```bash
# Ver proceso en puerto
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Matar proceso
kill -9 <PID>
```

### Permisos en Linux/WSL
```bash
# Dar permisos de ejecución
chmod +x scripts/*.sh
chmod +x *.sh
```

### Reset completo
```bash
# Parar todo
docker-compose down -v

# Limpiar
docker system prune -a --volumes

# Reiniciar
docker-compose up -d --build
```

---

**📅 Última actualización:** Octubre 2025  
**👥 Proyecto:** SaaS Cafeterías - Sistema de gestión integral
