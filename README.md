# 🚀 ModularBiz SaaS

**Plataforma SaaS unificada y simplificada para desarrollo local**

Proyecto limpio y consolidado que evolucionó hacia una solución SaaS modular y adaptable para múltiples tipos de negocio. **Diseñado para funcionar 100% local sin Docker ni Git**, con toda la funcionalidad unificada en archivos simples y manejables.

## 📁 Estructura Simplificada

```
modularbiz-saas/
├── backend/
│   ├── app/
│   │   ├── api/v1/users.py        # 🔥 TODOS los endpoints unificados
│   │   ├── core/config.py         # Configuración centralizada
│   │   ├── db/db.py              # 🔥 Modelos + CRUD unificados
│   │   ├── schemas.py            # 🔥 Validaciones unificadas
│   │   ├── services.py           # 🔥 Lógica de negocio unificada
│   │   └── main.py               # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/Dashboard.tsx  # Layout principal
│   │   ├── pages/                   # Login, Register, Businesses, etc.
│   │   ├── services/api.ts          # API client
│   │   ├── store/                   # authStore, cartStore
│   │   └── App.tsx
│   └── package.json
├── CHANGELOG.md                     # 🔥 Hecho + Por hacer unificado
└── README.md
```

### 🎯 **Características de la Arquitectura Unificada**

- **Un solo archivo de endpoints**: `users.py` contiene auth + users + businesses + products
- **Un solo archivo de modelos**: `db.py` contiene todos los modelos SQLAlchemy + CRUD
- **Un solo archivo de schemas**: `schemas.py` contiene todas las validaciones Pydantic
- **Un solo archivo de servicios**: `services.py` contiene autenticación y lógica de negocio
- **Sin Docker**: Desarrollo local directo con Python + Node
- **Sin Git complexity**: Proyecto autocontenido sin CI/CD

## 🚀 Instrucciones de Ejecución

### Prerrequisitos

- [Python 3.11+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)

### 1. Configuración Inicial

```bash
# Ir al directorio del proyecto
cd modularbiz-saas

# Crear archivos de configuración
# Backend: crear backend/.env con las variables necesarias
# Frontend: crear frontend/.env con las variables necesarias
```

### 2. Ejecutar Backend

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Ejecutar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

## 🔧 Variables de Entorno

### Backend (.env)
```env
DATABASE_URL=sqlite:///./modularbiz.db
SECRET_KEY=your-secret-key-here-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=ModularBiz SaaS
VERSION=0.3.0
API_V1_STR=/api/v1
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=ModularBiz SaaS
```

## ✨ **Características Principales**

### 🔐 **Autenticación Completa**
- JWT tokens con refresh
- Registro y login de usuarios  
- Protección de rutas

### 🏢 **Gestión de Negocios**
- CRUD completo de businesses
- Tipos de negocio configurables
- Multi-tenant ready

### 📦 **Gestión de Productos**
- CRUD completo con filtros
- Categorías y precios
- Control de disponibilidad

### 💻 **Frontend Moderno**
- React + TypeScript
- Dashboard profesional
- Responsive design
- Estado global con Zustand

## 🎯 **API Endpoints Disponibles**

```bash
# Autenticación
POST /api/v1/auth/register
POST /api/v1/auth/login  
POST /api/v1/auth/refresh
GET  /api/v1/auth/me

# Usuarios
GET  /api/v1/users
GET  /api/v1/users/{id}
PUT  /api/v1/users/{id}

# Negocios
GET  /api/v1/businesses
POST /api/v1/businesses
GET  /api/v1/businesses/{id}
PUT  /api/v1/businesses/{id}
DELETE /api/v1/businesses/{id}

# Productos
GET  /api/v1/products
POST /api/v1/products
GET  /api/v1/products/{id}
PUT  /api/v1/products/{id}
DELETE /api/v1/products/{id}
GET  /api/v1/businesses/{id}/products
```

## 📚 **Arquitectura Técnica**

### Backend (FastAPI)
- **Unified endpoints**: Todos en `users.py`
- **Unified models**: SQLAlchemy en `db.py`
- **Unified schemas**: Pydantic en `schemas.py`
- **Unified services**: Auth y business logic en `services.py`

### Frontend (React)
- **Component-based**: Dashboard modular
- **Type-safe**: TypeScript en todo el proyecto
- **State management**: Zustand stores
- **Modern routing**: React Router v6

### Database
- **SQLite**: Para desarrollo local simple
- **PostgreSQL**: Para producción (configurable)
- **SQLAlchemy ORM**: Modelos declarativos

**Proyecto simplificado y listo para desarrollo local sin dependencias externas.**

---

## 📝 Más Información

Ver `CHANGELOG.md` para:
- ✅ Funcionalidades completadas
- 🚧 Roadmap de próximas versiones
- 📋 Instrucciones detalladas de configuración