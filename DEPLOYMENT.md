# 🚀 CAFETERIA IA - GUÍA DE DESPLIEGUE EN PRODUCCIÓN

## 📋 Requisitos Previos

### Infraestructura Mínima
- **CPU**: 2 vCPUs (4 vCPUs recomendado)
- **RAM**: 4GB (8GB recomendado)
- **Almacenamiento**: 20GB SSD
- **Red**: Conexión estable a internet

### Software Requerido
- Docker 24.0+
- Docker Compose 2.0+
- Nginx (si no se usa Docker)
- SSL/TLS Certificate (Let's Encrypt recomendado)

## 🔧 Configuración Rápida con Docker

### 1. Preparar Variables de Entorno

Crear archivo `.env.production`:

```env
# Dominio y SSL
DOMAIN=tu-dominio.com
SSL_EMAIL=admin@tu-dominio.com

# Base de datos
POSTGRES_DB=cafeteria_ia_prod
POSTGRES_USER=cafeteria_user
POSTGRES_PASSWORD=SECURE_RANDOM_PASSWORD_HERE

# Seguridad (GENERAR CLAVES ÚNICAS)
SECRET_KEY=GENERATE_64_CHAR_SECRET_KEY_FOR_PRODUCTION
JWT_SECRET_KEY=GENERATE_DIFFERENT_JWT_SECRET_KEY
REDIS_PASSWORD=GENERATE_REDIS_PASSWORD

# APIs Externas
MERCADOPAGO_ACCESS_TOKEN=PROD_MP_ACCESS_TOKEN
MERCADOPAGO_PUBLIC_KEY=PROD_MP_PUBLIC_KEY
OPENAI_API_KEY=sk-PRODUCTION_OPENAI_KEY

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

### 2. Generar Claves Seguras

```bash
# Generar SECRET_KEY
openssl rand -hex 32

# Generar JWT_SECRET_KEY
openssl rand -base64 64

# Generar REDIS_PASSWORD
openssl rand -base64 32
```

### 3. Configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot certonly --standalone -d tu-dominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ./ssl/
```

### 4. Desplegar con Docker Compose

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/cafeteria-ia.git
cd cafeteria-ia

# Configurar permisos
chmod +x scripts/deploy.sh

# Ejecutar deployment
./scripts/deploy.sh production
```

## 🐳 Deployment Manual con Docker

### 1. Build de Imágenes

```bash
# Backend
docker build -t cafeteria-ia-backend:latest ./backend

# Frontend
docker build -t cafeteria-ia-frontend:latest ./frontend
```

### 2. Configurar Red Docker

```bash
# Crear red personalizada
docker network create cafeteria-network
```

### 3. Iniciar Servicios Base

```bash
# PostgreSQL
docker run -d \
  --name cafeteria-postgres \
  --network cafeteria-network \
  -e POSTGRES_DB=cafeteria_ia_prod \
  -e POSTGRES_USER=cafeteria_user \
  -e POSTGRES_PASSWORD=SECURE_PASSWORD \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Redis
docker run -d \
  --name cafeteria-redis \
  --network cafeteria-network \
  -v redis_data:/data \
  redis:7-alpine redis-server --appendonly yes --requirepass REDIS_PASSWORD
```

### 4. Iniciar Aplicación

```bash
# Backend
docker run -d \
  --name cafeteria-backend \
  --network cafeteria-network \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://cafeteria_user:SECURE_PASSWORD@cafeteria-postgres:5432/cafeteria_ia_prod \
  -e REDIS_URL=redis://:REDIS_PASSWORD@cafeteria-redis:6379/0 \
  cafeteria-ia-backend:latest

# Frontend
docker run -d \
  --name cafeteria-frontend \
  --network cafeteria-network \
  -p 3000:3000 \
  cafeteria-ia-frontend:latest
```

## 🏗️ Deployment sin Docker

### 1. Configurar Servidor

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv nginx postgresql-15 redis-server nodejs npm

# CentOS/RHEL
sudo yum install python3.11 nginx postgresql15-server redis nodejs npm
```

### 2. Configurar PostgreSQL

```bash
# Inicializar BD
sudo -u postgres createuser --interactive
sudo -u postgres createdb cafeteria_ia_prod

# Configurar usuario
sudo -u postgres psql
CREATE USER cafeteria_user WITH PASSWORD 'SECURE_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE cafeteria_ia_prod TO cafeteria_user;
```

### 3. Configurar Backend

```bash
# Clonar y configurar
git clone https://github.com/tu-usuario/cafeteria-ia.git
cd cafeteria-ia/backend

# Entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Dependencias
pip install -r requirements.txt

# Variables de entorno
cp .env.example .env.production
# Editar .env.production con valores reales

# Migraciones
alembic upgrade head

# Crear usuario admin
python create_admin.py
```

### 4. Configurar Nginx

```bash
# Configuración del sitio
sudo nano /etc/nginx/sites-available/cafeteria-ia
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 5. Configurar Servicios Systemd

**Backend Service** (`/etc/systemd/system/cafeteria-backend.service`):

```ini
[Unit]
Description=Cafeteria IA Backend
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/cafeteria-ia/backend
Environment=PATH=/path/to/cafeteria-ia/backend/venv/bin
ExecStart=/path/to/cafeteria-ia/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoreo y Logging

### 1. Configurar Logs

```bash
# Crear directorios de logs
sudo mkdir -p /var/log/cafeteria-ia
sudo chown www-data:www-data /var/log/cafeteria-ia
```

### 2. Configurar Prometheus (Opcional)

```bash
# Usar docker-compose.monitoring.yml
docker-compose -f docker-compose.monitoring.yml up -d
```

### 3. Health Checks

```bash
# Script de monitoreo
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
```

## 🔒 Seguridad en Producción

### 1. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Bloquear puertos internos
sudo ufw deny 5432
sudo ufw deny 6379
sudo ufw deny 8000
```

### 2. SSL/TLS

```bash
# Configurar renovación automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 3. Base de Datos

```bash
# PostgreSQL - deshabilitar conexiones remotas
sudo nano /etc/postgresql/15/main/postgresql.conf
# listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# local   all             all                                     md5
```

## 🚀 Scripts de Deployment

### Deploy Script (`scripts/deploy.sh`)

```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-production}

echo "🚀 Deploying Cafeteria IA - $ENVIRONMENT"

# Backup base de datos
if [ "$ENVIRONMENT" = "production" ]; then
    echo "📦 Creating database backup..."
    docker exec cafeteria-postgres pg_dump -U postgres cafeteria_ia_prod > backup_$(date +%Y%m%d_%H%M%S).sql
fi

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build nuevas imágenes
echo "🔨 Building images..."
docker-compose -f docker-compose.production.yml build

# Update servicios
echo "🔄 Updating services..."
docker-compose -f docker-compose.production.yml up -d

# Run migrations
echo "📊 Running migrations..."
docker exec cafeteria-backend alembic upgrade head

# Health check
echo "🏥 Health check..."
sleep 10
curl -f http://localhost/api/v1/health || exit 1

echo "✅ Deployment completed successfully!"
```

## 📋 Checklist de Producción

### Pre-deployment
- [ ] Claves de seguridad generadas y configuradas
- [ ] Base de datos configurada y respaldada
- [ ] SSL/TLS certificados instalados
- [ ] DNS configurado correctamente
- [ ] Firewall configurado
- [ ] Monitoreo configurado

### Post-deployment
- [ ] Health checks pasando
- [ ] Logs funcionando correctamente
- [ ] SSL/TLS funcionando
- [ ] APIs externas configuradas
- [ ] Backup automatizado configurado
- [ ] Alerts de monitoreo funcionando

## 🆘 Troubleshooting

### Backend no inicia
```bash
# Verificar logs
docker logs cafeteria-backend

# Verificar configuración
docker exec cafeteria-backend env | grep DATABASE_URL
```

### Base de datos no conecta
```bash
# Verificar servicio PostgreSQL
docker ps | grep postgres
docker logs cafeteria-postgres

# Test de conexión
docker exec cafeteria-postgres pg_isready -U postgres
```

### SSL no funciona
```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew
```

## 📞 Soporte

Para problemas de deployment:
1. Revisar logs en `/var/log/cafeteria-ia/`
2. Verificar health checks: `curl http://tu-dominio.com/health`
3. Comprobar configuración de DNS
4. Validar certificados SSL