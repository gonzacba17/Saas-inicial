# SaaS Inicial

Un proyecto inicial para aplicaciones SaaS construido con FastAPI (backend) y React TypeScript (frontend).

## 📁 Estructura del Proyecto

```
Saas inicial/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   └── token.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   └── user.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── cafe-frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── auth.ts
│   │   └── App.tsx
│   ├── Dockerfile
│   └── .env.example
├── infra/
├── docs/
├── tests/
└── docker-compose.yml
```

## 🚀 Instrucciones de Ejecución (Windows PowerShell)

### Prerrequisitos

- [Node.js](https://nodejs.org/) (v18 o superior)
- [Python](https://www.python.org/) (v3.11 o superior)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### 1. Configuración Inicial

```powershell
# Clonar el repositorio (si viene de Git)
git clone <repository-url>
cd "Saas inicial"

# Copiar archivos de configuración
Copy-Item "backend\.env.example" "backend\.env"
Copy-Item "cafe-frontend\.env.example" "cafe-frontend\.env"
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
cd cafe-frontend

# Instalar dependencias
npm install

# Ejecutar el servidor de desarrollo
npm run dev
```

#### Base de Datos (PostgreSQL local)

```powershell
# Instalar PostgreSQL o usar Docker
docker run --name postgres-saas -e POSTGRES_DB=saas_inicial -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15

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
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saas_inicial
SECRET_KEY=your-super-secret-key-here-change-this-in-production
OPENAI_API_KEY=your-openai-api-key-here
MERCADOPAGO_KEY=your-mercadopago-key-here
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 🔧 Desarrollo

### Estructura de la API

- **POST** `/api/v1/auth/register` - Registro de usuario
- **POST** `/api/v1/auth/token` - Login de usuario
- **GET** `/api/v1/auth/me` - Información del usuario actual
- **GET** `/api/v1/users/` - Lista de usuarios
- **GET** `/api/v1/users/{user_id}` - Usuario específico
- **PUT** `/api/v1/users/{user_id}` - Actualizar usuario

### Tecnologías Utilizadas

#### Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT Authentication
- Python-dotenv

#### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Fetch API

#### DevOps
- Docker
- Docker Compose
- PostgreSQL
- Redis

## 📝 Notas

- El proyecto incluye autenticación JWT completa
- Las contraseñas se hashean con bcrypt
- El frontend incluye formularios de login y registro
- Configuración lista para desarrollo y producción
- Estructura escalable para funcionalidades adicionales

## 🔒 Seguridad

- Cambiar `SECRET_KEY` en producción
- Configurar CORS apropiadamente
- Usar HTTPS en producción
- Configurar variables de entorno seguras