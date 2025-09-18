# SaaS Cafeterías - Plataforma de Gestión Integral

Sistema SaaS completo para gestión de cafeterías con autenticación, pagos, analytics y arquitectura escalable.

## 🚀 Inicio Rápido

### Prerrequisitos
- [Python 3.11+](https://www.python.org/)
- [Node.js 20+](https://nodejs.org/)
- [PostgreSQL 15+](https://www.postgresql.org/) (recomendado) o SQLite para desarrollo

### 1. Backend Setup

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Configurar base de datos
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables
cp .env.example .env
# Configurar VITE_API_URL=http://localhost:8000

# Iniciar desarrollo
npm run dev
```

### 3. URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Aplicación React |
| **Backend API** | http://localhost:8000 | API FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentación Swagger |

## ⚙️ Variables de Entorno

### Backend (.env)
```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/saas_cafeterias
# o para SQLite: DATABASE_URL=sqlite:///./saas_cafeterias.db

# Seguridad
SECRET_KEY=your-super-secret-key-64-characters-minimum
JWT_SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# APIs externas (opcional)
MERCADOPAGO_ACCESS_TOKEN=your-mercadopago-token
OPENAI_API_KEY=your-openai-api-key

# Entorno
ENVIRONMENT=development
DEBUG=true
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🛠️ Comandos Útiles

### Backend
```bash
# Tests
pytest

# Linting
ruff check . --fix

# Nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head
```

### Frontend
```bash
# Tests
npm test

# Build
npm run build

# Linting
npm run lint
```

## 📚 Documentación

- **[Roadmap.md](Roadmap.md)** - Planificación y fases del proyecto
- **[Changelog.md](Changelog.md)** - Registro de cambios
- **API Docs** - Disponible en `/docs` cuando el backend esté corriendo

## 🏗️ Arquitectura

- **Backend**: FastAPI + PostgreSQL + Alembic + JWT
- **Frontend**: React + TypeScript + Zustand + Tailwind CSS
- **Cache**: Redis (opcional)
- **Pagos**: MercadoPago
- **IA**: OpenAI

## 🤝 Contribución

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push y crear Pull Request

Ver [Roadmap.md](Roadmap.md) para ver qué funcionalidades están planificadas.