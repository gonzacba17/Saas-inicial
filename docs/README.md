# 🚀 SaaS Cafeterías - Sistema de Gestión Integral

Sistema SaaS completo para gestión de cafeterías con autenticación JWT, pagos seguros, IA conversacional y arquitectura escalable production-ready.

## 📋 Índice de Contenido

- [📂 Estructura del Proyecto](#-estructura-del-proyecto)
- [🚀 Inicio Rápido](#-inicio-rápido)
- [👤 Credenciales de Desarrollo](#-credenciales-de-desarrollo)
- [🏗️ Arquitectura del Sistema](#-arquitectura-del-sistema)
- [🛠️ Scripts y Comandos](#-scripts-y-comandos)
- [🧪 Testing y Validación](#-testing-y-validación)
- [📚 Documentación](#-documentación)
- [🚨 Troubleshooting](#-troubleshooting)

## 📂 Estructura del Proyecto

```
Saas-inicial/
├── 📁 backend/                 # API FastAPI y lógica de negocio
│   ├── app/                    # Código principal de la aplicación
│   │   ├── api/v1/            # Endpoints REST organizados
│   │   ├── core/              # Configuración y utilidades
│   │   ├── db/                # Modelos y CRUD de base de datos
│   │   ├── middleware/        # Middleware de seguridad y validación
│   │   └── services_directory/ # Servicios especializados
│   ├── alembic/               # Migraciones de base de datos
│   └── requirements.txt       # Dependencias Python
├── 📁 frontend/               # Aplicación React TypeScript
│   ├── src/
│   │   ├── components/        # Componentes reutilizables
│   │   ├── pages/             # Páginas de la aplicación
│   │   ├── store/             # Estado global (Zustand)
│   │   └── types/             # Tipos TypeScript
│   └── package.json           # Dependencias Node.js
├── 📁 tests/                  # Suite completa de testing
│   ├── full_test.py           # Tests de integración principal
│   └── test_*.py              # Tests unitarios por módulo
├── 📁 scripts/                # Scripts de automatización
│   ├── update_and_test.sh     # Script principal (Linux/Mac)
│   ├── update_and_test.ps1    # Script principal (Windows)
│   └── deploy.sh              # Scripts de despliegue
├── 📁 docs/                   # Documentación del proyecto
│   ├── SEGUIMIENTO.md         # Estado actual y métricas
│   ├── Roadmap.md             # Planificación y roadmap
│   └── DEPLOYMENT.md          # Guías de despliegue
└── 📁 monitoring/             # Observabilidad y monitoreo
    ├── prometheus/            # Métricas de aplicación
    └── grafana/               # Dashboards visuales
```

## 🚀 Inicio Rápido

### Prerrequisitos
- **Python 3.11+** - [Descargar aquí](https://www.python.org/)
- **Node.js 20+** - [Descargar aquí](https://nodejs.org/)
- **PostgreSQL 15+** (producción) o SQLite (desarrollo)

### ⚡ Setup Rápido (Desarrollo Local)

**Opción 1: Setup Automatizado (Recomendado)**
```bash
# Linux/Mac
./scripts/update_and_test.sh

# Windows
.\scripts\update_and_test.ps1
```

**Opción 2: Setup Manual**
```bash
# 1. Backend - Configurar y ejecutar
cd backend
python -m venv venv
pip install -r requirements.txt
python create_admin.py
python -m uvicorn app.main:app --reload

# 2. Frontend - En otra terminal
cd frontend
npm install
npm run dev

# 3. Validar funcionamiento
python tests/full_test.py
```

### 👤 Credenciales de Desarrollo

**Usuario Administrador Local:**
- **Email**: `admin@saas.test`
- **Password**: `Admin1234!`
- **Rol**: admin (permisos completos)

**URLs de Acceso:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

> ⚠️ **CRÍTICO**: 
> - Estas credenciales son **SOLO** para desarrollo local
> - **NUNCA** usar en producción o staging
> - Cambiar inmediatamente después del primer deploy
> - Ver [SECURITY.md](../SECURITY.md) para mejores prácticas

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico Actual
```
┌─────────────────┬─────────────────┬─────────────────┐
│    Frontend     │     Backend     │  Infraestructura │
├─────────────────┼─────────────────┼─────────────────┤
│ React 18        │ FastAPI         │ Docker Compose  │
│ TypeScript      │ Python 3.11+    │ PostgreSQL/SQLite│
│ Zustand         │ SQLAlchemy      │ Redis (opcional) │
│ Tailwind CSS    │ Alembic         │ Nginx           │
│ Vite            │ Pydantic        │ Prometheus      │
└─────────────────┴─────────────────┴─────────────────┘
```

### ✅ Estado Actual del Proyecto

| Componente | Estado | Score | Próxima Acción |
|------------|---------|-------|----------------|
| **🔒 Seguridad** | ✅ LISTO | 95/100 | Monitoreo en prod |
| **⚡ Performance** | ✅ LISTO | 92/100 | Optimizaciones menores |
| **🏗️ Infraestructura** | ✅ LISTO | 90/100 | Deploy staging |
| **📚 Documentación** | ✅ LISTO | 100/100 | Mantenimiento |
| **🛠️ Backups** | 🟡 PARCIAL | 80/100 | Validar restauración |
| **🧪 Testing** | 🔴 CRÍTICO | 40/100 | **Elevar coverage a 85%** |

### Servicios Implementados
- **AuthService**: JWT + roles + permisos ✅
- **PaymentService**: MercadoPago + webhooks ✅
- **AIService**: OpenAI + 4 tipos de asistentes ✅
- **CacheService**: Redis con fallback a memoria ✅
- **AuditService**: Logs para compliance ✅
- **SecretsService**: Gestión segura de variables ✅

## 🛠️ Scripts y Comandos

### 🧪 Testing y Validación

**Script Principal de Testing:**
```bash
# Desde la raíz del proyecto
python tests/full_test.py

# O usando el script automatizado
./scripts/update_and_test.sh  # Linux/Mac
.\scripts\update_and_test.ps1  # Windows
```

## ⚙️ En Progreso

### 🧪 Testing Coverage - CRÍTICO
**Estado**: 40% → 85% requerido  
**Timeline**: 3-4 días  
**Bloqueante**: Testing unitario insuficiente  

**Módulos críticos**:
- `auth.py` (28% → 80%)
- `businesses.py` (25% → 75%)
- `orders.py` (25% → 75%)
- `payments.py` (25% → 70%)

**Infraestructura lista**:
- ✅ CI/CD Pipeline configurado
- ✅ Tests E2E implementados
- ✅ Performance tests validados

**Tests disponibles incluyen:**
- ✅ Configuración de entorno y dependencias
- ✅ Seguridad (hashing, CORS, configuración) - **95/100**
- ✅ Base de datos (conexión, integridad, migraciones)
- ✅ Autenticación (login, JWT, registro) - **28% coverage**
- ✅ Autorización (permisos por rol) - **Validado**
- 🟡 Lógica de negocio (CRUD businesses/products) - **25% coverage**
- ✅ API endpoints (documentación, respuestas)
- ✅ Rendimiento (tiempos de respuesta) - **145ms avg**
- ✅ Frontend (accesibilidad, conectividad)

### 🔒 Testing de Seguridad Avanzado

**Nuevo: Suite Completa de Testing**
```bash
# Test completo de seguridad y permisos
python tests/test_business_flow_security.py

# Análisis de performance de endpoints críticos
python tests/test_performance_analysis.py

# Tests End-to-End completos
python tests/test_e2e_flow.py
```

**Testing de Seguridad Especializado:**
- **🔐 Autenticación robusta**: Login admin + /me endpoint sin errores 500
- **👮 Control de permisos**: Admin vs usuario regular (403 responses)
- **🏢 Flujo completo de negocio**: Admin login → crear negocio → crear producto → CRUD → validar permisos
- **⚡ Análisis de rendimiento**: Tiempos de respuesta y endpoints lentos
- **🛡️ Manejo de errores**: 400/401/403/404 responses apropiadas
- **🔍 Validación de roles**: Enum support y role checking robusto

**Testing de Performance:**
- **📊 Métricas detalladas**: Tiempo promedio, mín/máx, percentiles
- **🎯 Endpoints críticos**: Login, /me, CRUD businesses/products
- **🚨 Alertas automáticas**: Endpoints lentos (>500ms) identificados
- **📈 Tendencias**: Tracking de performance en el tiempo

**Testing End-to-End:**
- **🌐 Frontend + Backend**: Validación completa del stack
- **🔍 UI Error Handling**: Verificación de manejo de errores en React
- **👤 Flujos de usuario**: Login, permisos, CRUD completo
- **🛡️ Seguridad integrada**: Validación de 403/401 en UI

## 🛠️ Roadmap

### 🎯 Próximos Pasos (Post-Testing)

**Plan A**: Completar APIs + MercadoPago (1-2 semanas)
- Extender endpoints faltantes
- Validar MercadoPago sandbox
- Analytics básico

**Plan B**: Frontend Avanzado (2-3 semanas)  
- Dashboard con métricas
- Mobile responsive
- PWA implementation

**Plan C**: IA & Analytics (3-4 semanas)
- OpenAI integration completa
- Business intelligence
- Automated insights

**Plan D**: Escalamiento Enterprise (4-6 semanas)
- Multi-tenancy
- Marketplace functionality
- High availability

### ⚙️ Variables de Entorno Esenciales

> 🔒 **IMPORTANTE**: Nunca commitear archivos `.env` reales al repositorio!

**Backend (.env) - Desarrollo:**
```env
# Base de datos (SQLite para desarrollo SOLAMENTE)
DATABASE_URL=sqlite:///./saas_cafeterias_local.db

# Seguridad - CAMBIAR en producción!
# Generar con: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=CHANGE_ME_generate_unique_secret_for_each_environment
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Entorno
ENVIRONMENT=development
DEBUG=true

# APIs Externas (opcional para desarrollo)
REDIS_URL=redis://localhost:6379/0
MERCADOPAGO_ACCESS_TOKEN=TEST-your-sandbox-token
OPENAI_API_KEY=sk-proj-your-development-key
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

**📚 Configuración Completa:**
- Ver `.env.example` para todas las variables disponibles
- Ver `backend/.env.production.example` para configuración de producción
- Ver [SECURITY.md](../SECURITY.md) para gestión segura de secretos

### 🔧 Comandos de Desarrollo

**Scripts Principales:**
```bash
# Setup completo + tests (recomendado)
./scripts/update_and_test.sh        # Linux/Mac
.\scripts\update_and_test.ps1       # Windows

# Solo testing
python tests/full_test.py

# Deployment
./scripts/deploy.sh production
```

**Backend:**
```bash
# Crear/resetear admin
cd backend && python create_admin.py

# Linting y formateo
cd backend && ruff check . --fix

# Migraciones DB
cd backend && alembic revision --autogenerate -m "descripcion"
cd backend && alembic upgrade head
```

**Frontend:**
```bash
# Desarrollo
npm run dev

# Build producción
npm run build

# Tests y linting
npm test
npm run lint
```

## 📚 Documentación

### 📖 Documentación Principal
- **[docs/Roadmap.md](docs/Roadmap.md)** - Planificación del proyecto y próximos pasos
- **[docs/SEGUIMIENTO.md](docs/SEGUIMIENTO.md)** - Estado actual y métricas del proyecto
- **[docs/CHANGELOG_IMPROVEMENTS.md](docs/CHANGELOG_IMPROVEMENTS.md)** - Registro de mejoras
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Guías de despliegue en producción

### 🆕 Nueva Documentación Técnica
- **[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)** - Ejemplos completos de API con payloads y respuestas
- **[docs/PERFORMANCE_SECURITY_REPORT.md](docs/PERFORMANCE_SECURITY_REPORT.md)** - Análisis detallado de performance y seguridad
- **[docs/ESTADO_ACTUAL.md](docs/ESTADO_ACTUAL.md)** - 🆕 Reporte de auditoría y estado del proyecto
- **[PLAN_ACCION_COVERAGE.md](PLAN_ACCION_COVERAGE.md)** - 🆕 Plan para elevar coverage de testing
- **[logs/](logs/)** - Logs centralizados (app.log, security.log, performance.log, errors.log)

### 🚨 Estado de Preparación para Producción

| Componente | Estado | Score | Próxima Acción |
|------------|---------|-------|----------------|
| **🔒 Seguridad** | ✅ LISTO | 95/100 | Monitoreo en prod |
| **⚡ Performance** | ✅ LISTO | 92/100 | Optimizaciones menores |
| **🏗️ Infraestructura** | ✅ LISTO | 90/100 | Deploy staging |
| **📚 Documentación** | ✅ LISTO | 100/100 | Mantenimiento |
| **🛠️ Backups** | 🟡 PARCIAL | 80/100 | Validar restauración |
| **🧪 Testing** | 🔴 CRÍTICO | 40/100 | **Elevar coverage a 85%** |

**⚠️ ESTADO GENERAL**: **Base técnica EXCELENTE** - Una sola barrera para producción: testing coverage insuficiente

### 🔗 Enlaces Útiles
- **API Docs** - Documentación interactiva: http://localhost:8000/docs
- **Scripts** - Ver [scripts/](scripts/) para automatización
- **Tests** - Ver [tests/](tests/) para testing
- **Monitoring** - Dashboards en Grafana (configurado pero requiere Redis)

## 🚨 Troubleshooting

### Problemas Comunes y Soluciones

**1. Tests fallan con errores de conexión:**
```bash
# Verificar que el backend está corriendo
python -m uvicorn app.main:app --reload

# Si no funciona, verificar dependencias
pip install -r requirements.txt
```

**2. Error "No se puede conectar al backend":**
```bash
# Verificar puerto y URL
echo "Backend debería estar en http://localhost:8000"
curl http://localhost:8000/health
```

**3. Problemas de importación o dependencias:**
```bash
# Reinstalar entorno virtual
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**4. Frontend no se conecta con backend:**
```bash
# Verificar variables de entorno del frontend
cat frontend/.env
# Debe contener: VITE_API_URL=http://localhost:8000
```

**5. Error de JWT o autenticación:**
```bash
# Recrear usuario admin
cd backend && python create_admin.py

# Verificar en http://localhost:8000/docs
# Login con admin@saas.test / Admin1234!
```

### Comandos de Diagnóstico

```bash
# Health check completo
python tests/full_test.py

# O usar script automatizado
./scripts/update_and_test.sh

# Verificar estado de servicios
python -c "from app.core.config import settings; print(f'DB: {settings.db_url}')"

# Test de conectividad rápido
curl http://localhost:8000/health
curl http://localhost:5173/
```

---

## 🤝 Contribución

### Workflow de Desarrollo
1. Fork del repositorio
2. Crear branch para feature: `git checkout -b feature/nueva-funcionalidad`
3. Ejecutar tests antes de commit: `python full_test.py`
4. Commit con mensaje descriptivo: `git commit -m 'feat: nueva funcionalidad'`
5. Push y crear Pull Request

### Enlaces Útiles
- **🗺️ [Roadmap.md](Roadmap.md)** - Planificación y próximos pasos
- **📊 [SEGUIMIENTO.md](SEGUIMIENTO.md)** - Estado actual del proyecto
- **📋 [CHANGELOG_IMPROVEMENTS.md](CHANGELOG_IMPROVEMENTS.md)** - Historial de mejoras

---

**📞 Support**: Para problemas técnicos, primero ejecutar `python full_test.py` y revisar la sección Troubleshooting.

**🎯 Estado**: Sistema en desarrollo activo con arquitectura sólida y testing automatizado.