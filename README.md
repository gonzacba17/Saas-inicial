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
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

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

**Usuario Administrador:**
- **Email**: `admin@saas.test`
- **Password**: `Admin1234!`
- **Rol**: admin (permisos completos)

**URLs de Acceso:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

> ⚠️ **Importante**: Estas credenciales son solo para desarrollo local.

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

### Estado Actual del Proyecto
- **✅ Backend API**: 50+ endpoints implementados y documentados
- **✅ Base de Datos**: 8 modelos relacionales con migraciones
- **✅ Autenticación**: JWT con roles y permisos granulares
- **✅ Frontend**: React SPA con 8 páginas funcionales  
- **✅ Testing**: Suite completa con full_test.py
- **✅ Infraestructura**: Docker, monitoring, deployment scripts
- **🔄 En desarrollo**: Integración completa de todas las funcionalidades

### Servicios Implementados
- **AuthService**: JWT + roles + permisos
- **PaymentService**: MercadoPago + webhooks
- **AIService**: OpenAI + 4 tipos de asistentes
- **CacheService**: Redis con fallback a memoria
- **AuditService**: Logs para compliance
- **SecretsService**: Gestión segura de variables

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

Este script ejecuta una suite completa que valida:
- ✅ Configuración de entorno y dependencias
- ✅ Seguridad (hashing, CORS, configuración)
- ✅ Base de datos (conexión, integridad, migraciones)
- ✅ Autenticación (login, JWT, registro)
- ✅ Autorización (permisos por rol)
- ✅ Lógica de negocio (CRUD businesses/products)
- ✅ API endpoints (documentación, respuestas)
- ✅ Rendimiento (tiempos de respuesta)
- ✅ Frontend (accesibilidad, conectividad)

### ⚙️ Variables de Entorno Esenciales

**Backend (.env):**
```env
# Base de datos (SQLite para desarrollo)
DATABASE_URL=sqlite:///./saas_cafeterias_local.db

# Seguridad (generar claves únicas en producción)
SECRET_KEY=development-secret-key-64-chars-minimum-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Entorno
ENVIRONMENT=development
DEBUG=true

# Opcionales para funcionalidades completas
REDIS_URL=redis://localhost:6379/0
MERCADOPAGO_ACCESS_TOKEN=your-token-here
OPENAI_API_KEY=your-key-here
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

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