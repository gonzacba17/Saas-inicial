# 🚀 Guía de Despliegue - ModularBiz SaaS

Esta guía describe cómo desplegar ModularBiz SaaS en producción.

## 📋 Requisitos Previos

### Sistema Operativo
- Ubuntu 20.04+ / CentOS 8+ / Rocky Linux 8+
- Al menos 2GB RAM
- 20GB de espacio en disco

### Software Requerido
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Nginx
- Certbot (para SSL)

## 🔧 Instalación del Sistema

### 1. Actualizar el sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Python y dependencias
```bash
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y
```

### 3. Instalar PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4. Instalar Redis
```bash
sudo apt install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis
```

### 5. Instalar Nginx
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🗄️ Configuración de Base de Datos

### 1. Crear usuario y base de datos PostgreSQL
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE modularbiz_saas;
CREATE USER modularbiz_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE modularbiz_saas TO modularbiz_user;
ALTER USER modularbiz_user CREATEDB;
\q
```

### 2. Configurar PostgreSQL para conexiones remotas (si es necesario)
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
# Cambiar: listen_addresses = 'localhost'

sudo nano /etc/postgresql/14/main/pg_hba.conf
# Agregar: host all all 0.0.0.0/0 md5

sudo systemctl restart postgresql
```

## 📦 Despliegue de la Aplicación

### 1. Crear usuario del sistema
```bash
sudo useradd -m -s /bin/bash modularbiz
sudo su - modularbiz
```

### 2. Clonar o transferir el código
```bash
# Si usas Git
git clone https://github.com/tu-usuario/modularbiz-saas.git
cd modularbiz-saas/backend

# O transferir archivos manualmente
scp -r ./backend modularbiz@your-server:/home/modularbiz/
```

### 3. Crear entorno virtual
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
cp .env.production.example .env
nano .env
```

Configurar las siguientes variables:
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=tu-clave-super-secreta-de-produccion
POSTGRES_USER=modularbiz_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=localhost
POSTGRES_DB=modularbiz_saas
```

### 6. Ejecutar migraciones
```bash
python deploy.py production
```

## 🔧 Configuración de Nginx

### 1. Crear configuración del sitio
```bash
sudo nano /etc/nginx/sites-available/modularbiz
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/modularbiz/modularbiz-saas/backend/static/;
    }

    client_max_body_size 10M;
}
```

### 2. Habilitar el sitio
```bash
sudo ln -s /etc/nginx/sites-available/modularbiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Configuración SSL con Let's Encrypt

### 1. Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtener certificado SSL
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔄 Configuración de Systemd Service

### 1. Crear archivo de servicio
```bash
sudo nano /etc/systemd/system/modularbiz.service
```

```ini
[Unit]
Description=ModularBiz SaaS FastAPI app
After=network.target

[Service]
Type=notify
User=modularbiz
Group=modularbiz
RuntimeDirectory=modularbiz
WorkingDirectory=/home/modularbiz/modularbiz-saas/backend
Environment=PATH=/home/modularbiz/modularbiz-saas/backend/venv/bin
ExecStart=/home/modularbiz/modularbiz-saas/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. Habilitar y iniciar el servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable modularbiz
sudo systemctl start modularbiz
sudo systemctl status modularbiz
```

## 📊 Monitoreo y Logs

### 1. Ver logs de la aplicación
```bash
sudo journalctl -u modularbiz -f
```

### 2. Ver logs de Nginx
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. Monitoreo de recursos
```bash
# CPU y memoria
htop

# Espacio en disco
df -h

# Estado de servicios
sudo systemctl status nginx postgresql redis modularbiz
```

## 🔒 Configuraciones de Seguridad Adicionales

### 1. Configurar firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 5432  # PostgreSQL (solo si es necesario acceso remoto)
```

### 2. Configurar fail2ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Actualizar regularmente
```bash
# Crear cron job para actualizaciones automáticas
sudo crontab -e
# Agregar: 0 2 * * 0 apt update && apt upgrade -y
```

## 🔄 Actualizaciones y Mantenimiento

### 1. Actualizar la aplicación
```bash
sudo su - modularbiz
cd modularbiz-saas/backend
git pull  # Si usas Git
source venv/bin/activate
pip install -r requirements.txt
python deploy.py production --skip-deps
sudo systemctl restart modularbiz
```

### 2. Backup de la base de datos
```bash
# Crear backup
sudo -u postgres pg_dump modularbiz_saas > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
sudo -u postgres psql modularbiz_saas < backup_20241201_120000.sql
```

### 3. Backup de archivos subidos
```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

## 🏥 Solución de Problemas

### Problema: La aplicación no inicia
```bash
# Revisar logs
sudo journalctl -u modularbiz -n 50

# Verificar configuración
source venv/bin/activate
python -c "from app.core.config import settings; print(settings.database_url)"
```

### Problema: Error de conexión a la base de datos
```bash
# Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql

# Probar conexión
psql -h localhost -U modularbiz_user -d modularbiz_saas
```

### Problema: Certificado SSL expira
```bash
# Renovar certificados
sudo certbot renew --dry-run
sudo certbot renew
```

## 📞 Soporte

Para soporte adicional:
1. Revisar los logs detalladamente
2. Verificar la configuración de variables de entorno
3. Comprobar que todos los servicios estén ejecutándose
4. Verificar conectividad de red y DNS

---

¡Tu aplicación ModularBiz SaaS está lista para producción! 🎉