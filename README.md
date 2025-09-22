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

- **[Roadmap.md](Roadmap.md)** - Planificación y evolución del proyecto
- **[SEGUIMIENTO.md](SEGUIMIENTO.md)** - Dashboard ejecutivo y métricas
- **[Changelog.md](Changelog.md)** - Registro detallado de cambios
- **API Docs** - Documentación interactiva en `/docs`
- **Monitoring** - Dashboards en Grafana (puerto 3001)

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico
```
┌─────────────────┬─────────────────┬─────────────────┐
│    Frontend     │     Backend     │  Infraestructura │
├─────────────────┼─────────────────┼─────────────────┤
│ React 18        │ FastAPI         │ Docker Compose  │
│ TypeScript      │ Python 3.11+    │ PostgreSQL 15   │
│ Zustand         │ SQLAlchemy      │ Redis 7         │
│ Tailwind CSS    │ Alembic         │ Nginx           │
│ Vite            │ Pydantic        │ Prometheus      │
└─────────────────┴─────────────────┴─────────────────┘
```

### Servicios y Componentes

#### Backend Services
- **AuthService**: Autenticación JWT y gestión de usuarios
- **PaymentService**: Integración MercadoPago con webhooks
- **AIService**: Asistentes OpenAI especializados
- **CacheService**: Cache Redis con fallback a memoria
- **AuditService**: Logs de auditoría para compliance
- **SecretsService**: Gestión segura de secretos

#### Integraciones Externas
- **MercadoPago**: Procesamiento de pagos seguro
- **OpenAI**: 4 tipos de asistentes de IA
- **Celery**: 12 background tasks asíncronos
- **Redis**: Cache distribuido y sesiones

### Diagrama de Arquitectura
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   React     │────│   Nginx     │────│   FastAPI   │
│  Frontend   │    │Load Balancer│    │   Backend   │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
                   ┌─────────────┐    ┌─────────────┐
                   │ PostgreSQL  │────│    Redis    │
                   │  Database   │    │    Cache    │
                   └─────────────┘    └─────────────┘
                                               │
                   ┌─────────────┐    ┌─────────────┐
                   │   Celery    │────│   External  │
                   │  Workers    │    │ APIs (MP/AI)│
                   └─────────────┘    └─────────────┘
```

## 📝 Ejemplos de API

### Autenticación
```bash
# Registro de usuario
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario",
    "password": "mipassword123",
    "role": "owner"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario&password=mipassword123"

# Respuesta
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Gestión de Negocios
```bash
# Crear negocio
curl -X POST "http://localhost:8000/api/v1/businesses" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Central",
    "description": "Cafetería en el centro de la ciudad",
    "address": "Av. Principal 123",
    "phone": "+54911234567",
    "email": "info@cafecentral.com",
    "business_type": "cafe"
  }'

# Listar negocios
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/businesses"
```

### Productos y Órdenes
```bash
# Crear producto
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Americano",
    "description": "Café negro tradicional",
    "price": 250.00,
    "business_id": "uuid-del-negocio",
    "category": "bebidas"
  }'

# Crear orden
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "uuid-del-negocio",
    "items": [
      {
        "product_id": "uuid-del-producto",
        "quantity": 2,
        "unit_price": 250.00
      }
    ]
  }'
```

### Pagos con MercadoPago
```bash
# Crear preferencia de pago
curl -X POST "http://localhost:8000/api/v1/payments/preference" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "uuid-de-la-orden",
    "title": "Pedido Café Central",
    "description": "2x Café Americano",
    "amount": 500.00
  }'

# Respuesta
{
  "preference_id": "123456789-abcd-efgh-ijkl-mnopqrstuvwx",
  "init_point": "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=...",
  "sandbox_init_point": "https://sandbox.mercadopago.com.ar/checkout/v1/redirect?pref_id=..."
}
```

## 🔧 Scripts Útiles

### Validación de Integraciones
```bash
# Validar todas las integraciones
python scripts/validate-integrations.py

# Resultado esperado:
# ✅ Environment Variables: OK
# ✅ Payment Service: Configured  
# ✅ AI Service: Initialized
# ✅ Cache Service: Working
# ✅ Docker Services: 8 services running
# ✅ API Health: OK
```

### Deployment Scripts
```bash
# Setup completo de producción
./scripts/deploy.sh production

# Configurar SSL automático
./scripts/ssl-setup.sh

# Backup de base de datos
./scripts/backup.sh

# Configurar gestión de secretos
./scripts/secrets-setup.sh
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```bash
# Verificar conexión PostgreSQL
psql $DATABASE_URL -c "SELECT version();"

# Si falla, verificar variables de entorno
echo $DATABASE_URL

# Reiniciar servicios Docker
docker-compose down && docker-compose up -d
```

#### 2. Tests Fallan
```bash
# Ejecutar tests en modo verbose
pytest -v --tb=short

# Limpiar cache de pytest
pytest --cache-clear

# Verificar base de datos de test
echo $TEST_DATABASE_URL
```

#### 3. Frontend No Se Conecta al Backend
```bash
# Verificar variables de entorno del frontend
cat frontend/.env

# Debe contener:
# VITE_API_URL=http://localhost:8000

# Verificar CORS en el backend
# En backend/app/main.py, verificar allow_origins
```

#### 4. Celery Workers No Funcionan
```bash
# Verificar Redis
redis-cli ping

# Iniciar worker manualmente
cd backend && celery -A app.services_directory.celery_app worker --loglevel=info

# Verificar tareas pendientes
celery -A app.services_directory.celery_app inspect active
```

#### 5. Problemas con MercadoPago
```bash
# Verificar token de acceso
echo $MERCADOPAGO_ACCESS_TOKEN

# Test de conectividad
curl -H "Authorization: Bearer $MERCADOPAGO_ACCESS_TOKEN" \
  "https://api.mercadopago.com/users/me"

# Verificar webhook URL en el dashboard de MercadoPago
```

### Logs y Monitoreo

#### Acceder a Logs
```bash
# Logs del backend
docker-compose logs -f backend

# Logs de la base de datos
docker-compose logs -f postgres

# Logs de Redis
docker-compose logs -f redis

# Logs de Celery
docker-compose logs -f celery
```

#### Dashboard de Monitoreo
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Docs**: http://localhost:8000/docs

### Health Checks
```bash
# Verificar salud de la API
curl http://localhost:8000/health

# Verificar métricas
curl http://localhost:8000/metrics

# Verificar status de servicios
docker-compose ps
```

## 🛡️ Seguridad

### Variables de Entorno Sensibles
```bash
# NUNCA commitear archivos .env reales
# Usar siempre .env.example como template

# Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Validar configuración de seguridad
python scripts/validate-integrations.py
```

### Buenas Prácticas
- ✅ Usar HTTPS en producción
- ✅ Rotar tokens de acceso regularmente
- ✅ Mantener dependencias actualizadas
- ✅ Revisar logs de auditoría
- ✅ Backup regular de la base de datos

## 🤝 Contribución

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push y crear Pull Request

Ver [Roadmap.md](Roadmap.md) para ver qué funcionalidades están planificadas.

## 📊 Observabilidad

### Métricas Disponibles
- **Performance**: Tiempo de respuesta de endpoints
- **Errores**: Rate de errores 4xx/5xx
- **Recursos**: Uso de CPU, memoria, disco
- **Base de datos**: Conexiones activas, queries lentas
- **Cache**: Hit/miss ratio de Redis
- **Negocio**: Órdenes por minuto, ingresos, usuarios activos

### Alertas Configuradas
- 🚨 API response time > 1s
- 🚨 Error rate > 5%
- 🚨 Database connections > 80%
- 🚨 Disk space < 20%
- 🚨 Memory usage > 90%