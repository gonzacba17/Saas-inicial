# 🚀 ModularBiz SaaS

**Evolución de Cafetería IA hacia una plataforma SaaS modular y escalable**

Plataforma SaaS construida con FastAPI y React TypeScript, diseñada para adaptarse a cualquier rubro de negocio. Comenzó como "Cafetería IA" y evolucionó hacia una solución modular que puede configurarse para restaurantes, tiendas, servicios, y más.

## 📁 Estructura del Proyecto

```
modularbiz-saas/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── auth.py (JWT authentication)
│   │   │   ├── users.py (user management)
│   │   │   ├── products.py (CRUD productos)
│   │   │   └── orders.py (checkout & payments)
│   │   ├── core/
│   │   │   ├── config.py (environment settings)
│   │   │   └── security.py (JWT & permissions)
│   │   ├── db/
│   │   │   ├── models.py (User, Business, Product, Order)
│   │   │   ├── repositories/ (data access layer)
│   │   │   └── session.py (database connection)
│   │   ├── schemas/ (Pydantic models)
│   │   ├── services/ (business logic)
│   │   │   ├── auth.py (authentication)
│   │   │   ├── payment.py (MercadoPago integration)
│   │   │   └── ai_service.py (OpenAI integration)
│   │   └── workers/ (background tasks)
│   ├── tests/ (pytest suite)
│   ├── alembic/ (database migrations)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/ (reusable UI components)
│   │   ├── pages/ (route components)
│   │   ├── store/ (Zustand state management)
│   │   ├── services/ (API layer)
│   │   ├── types/ (TypeScript definitions)
│   │   └── tests/ (Vitest suite)
│   ├── package.json (dependencies & scripts)
│   └── vite.config.ts (build configuration)
├── .github/workflows/ (CI/CD automation)
├── docs/ (project documentation)
├── infra/ (deployment configurations)
├── CHANGELOG.md (version history)
├── Roadmap.md (development roadmap)
└── docker-compose.yml (local development)
```

## 🚀 Instrucciones de Ejecución (Windows PowerShell)

### Prerrequisitos

- [Node.js](https://nodejs.org/) (v18 o superior)
- [Python](https://www.python.org/) (v3.11 o superior)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### 1. Configuración Inicial

```powershell
# Clonar el repositorio
git clone <repository-url>
cd modularbiz-saas

# Copiar archivos de configuración
Copy-Item "backend\.env.example" "backend\.env"
Copy-Item "frontend\.env.example" "frontend\.env"

# Editar variables de entorno según necesidades
# Importante: Cambiar SECRET_KEY en producción
```

### 2. Ejecutar con Docker (Recomendado)

```powershell
# Construir y ejecutar todos los servicios
docker-compose up --build

# Para ejecutar en segundo plano
docker-compose up -d --build

# Para detener los servicios
docker-compose down
```

Los servicios estarán disponibles en:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Desarrollo Local

#### Backend

```powershell
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Editar el archivo .env con los valores correctos

# Ejecutar el servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```powershell
# Abrir nueva terminal y navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar el servidor de desarrollo
npm run dev
```

#### Base de Datos (PostgreSQL local)

```powershell
# Instalar PostgreSQL o usar Docker
docker run --name postgres-modularbiz -e POSTGRES_DB=modularbiz_saas -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15

# Crear las tablas (desde el directorio backend)
# Nota: Implementar Alembic migrations según necesidades
```

### 4. Comandos Útiles

```powershell
# Ver logs de Docker
docker-compose logs -f

# Reconstruir un servicio específico
docker-compose up --build backend
docker-compose up --build frontend

# Ejecutar comandos dentro de contenedores
docker-compose exec backend bash
docker-compose exec frontend sh

# Limpiar volúmenes y contenedores
docker-compose down -v
docker system prune -a
```

### 5. Variables de Entorno

#### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/modularbiz_saas
SECRET_KEY=your-super-secret-key-here-change-this-in-production-minimum-32-characters
OPENAI_API_KEY=your-openai-api-key-here
MERCADOPAGO_ACCESS_TOKEN=your-mercadopago-access-token-here
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=ModularBiz SaaS
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_PAYMENTS=true
```

## 🔧 Desarrollo

### Estructura de la API

#### Auth Endpoints
- **POST** `/api/v1/auth/register` - Registro de usuario
- **POST** `/api/v1/auth/login` - Login de usuario  
- **POST** `/api/v1/auth/refresh` - Renovar token
- **GET** `/api/v1/auth/me` - Información del usuario actual

#### User Management
- **GET** `/api/v1/users/` - Lista de usuarios
- **GET** `/api/v1/users/{user_id}` - Usuario específico
- **PUT** `/api/v1/users/{user_id}` - Actualizar usuario

#### Cafe & Products (Próximamente en Fase 3)
- **GET** `/api/v1/cafes/` - Lista de cafeterías
- **GET** `/api/v1/cafes/{cafe_id}/products` - Productos de una cafetería
- **POST** `/api/v1/orders/` - Crear pedido

#### AI Assistant (Próximamente en Fase 5)
- **POST** `/api/v1/assistant/` - Consulta al asistente IA
- **GET** `/api/v1/analytics/sales` - Análisis de ventas

### Tecnologías Utilizadas

#### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **Alembic** - Migraciones de base de datos
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y sesiones
- **JWT** - Autenticación con tokens
- **OpenAI** - Integración de IA (opcional)
- **Celery** - Tareas en segundo plano
- **Python-dotenv** - Variables de entorno

#### Frontend
- **React 18** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool rápido
- **Tailwind CSS** - Framework de CSS
- **Zustand** - State management
- **React Router** - Navegación SPA
- **Vitest** - Testing framework

#### DevOps & CI/CD
- **Docker & Docker Compose** - Contenarización
- **GitHub Actions** - CI/CD automatizado
- **PostgreSQL & Redis** - Servicios de datos

## 📝 Estado del Proyecto

### 🏗️ Evolución: De Cafetería IA a ModularBiz SaaS

Este proyecto comenzó como una solución específica para cafeterías y evolucionó hacia una **plataforma SaaS modular** que puede adaptarse a cualquier tipo de negocio.

### ✅ Completado (v0.2.0)
- ✅ **Arquitectura modular** - Estructura escalable backend/frontend
- ✅ **Autenticación JWT** - Sistema completo de auth con refresh tokens
- ✅ **Frontend SPA** - React + TypeScript + Tailwind CSS
- ✅ **State Management** - Zustand para auth y carrito
- ✅ **API Foundation** - FastAPI con documentación automática
- ✅ **Database Layer** - SQLAlchemy + Alembic migrations
- ✅ **Containerización** - Docker Compose para desarrollo
- ✅ **CI/CD Pipeline** - GitHub Actions con tests automatizados
- ✅ **Testing Setup** - Pytest (backend) y Vitest (frontend)

### 🎯 MVP En Desarrollo (v0.3.0)

**Core Features:**
- 🔄 CRUD completo de productos/servicios
- 💳 Checkout con integración MercadoPago
- 📊 Dashboard de ventas y métricas
- 🏪 Sistema multi-tenant (configuración por negocio)

**Seguridad & Performance:**
- 🛡️ Rate limiting con Redis
- 🔒 Validación de webhooks de pago
- ⚡ Optimización de queries y caching

### 🎯 Checklist de Desarrollo
1. ✅ Clonar y configurar `.env` files
2. ✅ Levantar con `docker-compose up --build`
3. ✅ Acceder a API docs: http://localhost:8000/docs
4. ✅ Acceder a frontend: http://localhost:5173

## 🔒 Seguridad

- Cambiar `SECRET_KEY` en producción
- Configurar CORS apropiadamente
- Usar HTTPS en producción
- Configurar variables de entorno seguras