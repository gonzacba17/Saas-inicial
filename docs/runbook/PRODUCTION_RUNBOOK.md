# Production Runbook - SaaS Cafeterías

**Última actualización:** 2025-10-15  
**Versión:** 1.0.0  
**Ambiente:** Production

---

## 1. Contactos de Emergencia

### On-Call Schedule
| Rol | Nombre | Teléfono | Email | Horario |
|-----|--------|----------|-------|---------|
| DevOps Lead | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | 24/7 |
| Backend Lead | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | Business hours |
| DBA | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | On-call weekends |
| Security | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | On-call |

### Escalation Path
1. **Severity 1 (Crítico)** → DevOps Lead → CTO
2. **Severity 2 (Alto)** → Backend Lead → DevOps Lead
3. **Severity 3 (Medio)** → Team asignado
4. **Severity 4 (Bajo)** → Backlog

---

## 2. URLs Críticas

### Production
- **Frontend:** https://tu-dominio.com
- **API:** https://api.tu-dominio.com
- **API Docs:** https://api.tu-dominio.com/docs (DESHABILITADO en prod)
- **Health Check:** https://api.tu-dominio.com/health

### Monitoring & Observability
- **Grafana:** http://localhost:3000 (puerto expuesto solo en VPN)
- **Prometheus:** http://localhost:9090
- **AlertManager:** http://localhost:9093
- **Sentry:** https://sentry.io/organizations/[ORG]/projects/[PROJECT]

### Infrastructure
- **Server SSH:** `ssh user@production-server.com`
- **Database:** `prod-db.internal:5432`
- **Redis:** `prod-redis.internal:6379`

---

## 3. Comandos Comunes de Operación

### Ver Estado del Sistema
```bash
cd /mnt/c/wamp64/www/Saas-inicial
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs -f --tail=100
```

### Revisar Logs Específicos
```bash
docker-compose -f docker-compose.production.yml logs backend --tail=500
docker-compose -f docker-compose.production.yml logs worker --tail=200
docker-compose -f docker-compose.production.yml logs postgres --tail=100
```

### Reiniciar Servicios
```bash
docker-compose -f docker-compose.production.yml restart backend
docker-compose -f docker-compose.production.yml restart worker
docker-compose -f docker-compose.production.yml restart nginx
```

### Ver Métricas de Contenedores
```bash
docker stats --no-stream
docker inspect saas-backend-prod | grep -A 5 "Memory"
```

### Acceder a Contenedor
```bash
docker exec -it saas-backend-prod /bin/bash
docker exec -it saas-postgres-prod psql -U prod_user -d saas_cafeterias_prod
docker exec -it saas-redis-prod redis-cli
```

---

## 4. Procedimientos de Deploy

### Deploy Normal (Planificado)
```bash
cd /mnt/c/wamp64/www/Saas-inicial
bash scripts/deploy_production.sh
```

**Pasos automáticos del script:**
1. Backup de base de datos
2. Pull de código desde Git (tag o branch)
3. Build de imágenes Docker
4. Migraciones de DB
5. Deploy de servicios
6. Health checks
7. Smoke tests
8. Rollback automático si falla

**Tiempo estimado:** 10-15 minutos  
**Downtime:** ~60 segundos durante restart de servicios

### Deploy con Tag Específico
```bash
export DEPLOY_TAG=v1.2.3
bash scripts/deploy_production.sh
```

### Verificación Post-Deploy
```bash
curl https://api.tu-dominio.com/health
bash scripts/smoke_tests.sh production

docker-compose -f docker-compose.production.yml logs backend --tail=50
```

---

## 5. Procedimientos de Rollback

### Rollback a Versión Anterior
```bash
bash scripts/rollback.sh

bash scripts/rollback.sh v1.1.0
```

**El script te preguntará:**
1. Confirmación de rollback
2. ¿Restaurar base de datos? (y/N)
3. Selección de backup si aplica

**Tiempo estimado:** 5-10 minutos  
**Downtime:** ~60 segundos

### Rollback Manual de Emergencia
```bash
cd /mnt/c/wamp64/www/Saas-inicial
docker-compose -f docker-compose.production.yml down

git checkout v1.1.0

docker-compose -f docker-compose.production.yml up -d
```

---

## 6. Gestión de Base de Datos

### Backup Manual
```bash
docker exec saas-postgres-prod pg_dump -U prod_user saas_cafeterias_prod > backup_$(date +%Y%m%d_%H%M%S).sql
gzip backup_*.sql
```

### Restaurar Backup
```bash
gunzip -c backup_20251015_120000.sql.gz | docker exec -i saas-postgres-prod psql -U prod_user -d saas_cafeterias_prod
```

### Ver Backups Disponibles
```bash
ls -lht backups/
```

### Ejecutar Migración Manual
```bash
docker-compose -f docker-compose.production.yml run --rm backend alembic upgrade head
docker-compose -f docker-compose.production.yml run --rm backend alembic current
```

### Consultas de Diagnóstico
```sql
-- Conexiones activas
SELECT count(*) FROM pg_stat_activity;

-- Queries lentas actuales
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '1 seconds'
AND state = 'active';

-- Tamaño de tablas
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Locks activos
SELECT * FROM pg_locks WHERE NOT GRANTED;
```

---

## 7. Troubleshooting Común

### API Devuelve 502/503

**Síntomas:** Nginx retorna 502 Bad Gateway o 503 Service Unavailable

**Diagnóstico:**
```bash
docker ps | grep saas-backend-prod
docker-compose -f docker-compose.production.yml logs backend --tail=100
curl http://localhost:8000/health
```

**Soluciones:**
1. Backend caído → `docker-compose -f docker-compose.production.yml restart backend`
2. Timeout → Revisar logs de errores en backend
3. Health check fallando → Verificar conectividad con DB y Redis

---

### API Muy Lenta (Response Time > 2s)

**Síntomas:** P95 response time > 2s en Grafana

**Diagnóstico:**
```bash
docker exec saas-postgres-prod psql -U prod_user -d saas_cafeterias_prod
docker stats --no-stream

curl -w "@-" -o /dev/null -s https://api.tu-dominio.com/health << 'EOF'
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
EOF
```

**Soluciones:**
1. Queries lentas → Revisar slow query log
2. CPU/Memory alto → Escalar recursos
3. Connection pool lleno → Aumentar pool size

---

### Celery Worker No Procesa Tasks

**Síntomas:** Tasks quedan en estado pending en Redis

**Diagnóstico:**
```bash
docker-compose -f docker-compose.production.yml logs worker
docker exec -it saas-redis-prod redis-cli
> LLEN celery
> LRANGE celery 0 10
```

**Soluciones:**
1. Worker caído → `docker-compose -f docker-compose.production.yml restart worker`
2. Worker bloqueado → Reiniciar worker
3. Queue con backlog → Escalar workers

---

### Disco Lleno (Disk Space 100%)

**Síntomas:** Alerta "DiskSpaceCritical" disparada

**Diagnóstico:**
```bash
df -h
du -sh /var/lib/docker/volumes/* | sort -rh | head -10
du -sh /mnt/c/wamp64/www/Saas-inicial/logs/* | sort -rh | head -10
```

**Soluciones Inmediatas:**
```bash
find /mnt/c/wamp64/www/Saas-inicial/logs -name "*.log" -mtime +7 -delete

docker system prune -a --volumes -f

find /mnt/c/wamp64/www/Saas-inicial/backups -name "*.sql.gz" -mtime +30 -delete
```

---

### Error Rate > 5%

**Síntomas:** Alerta "HighErrorRate" disparada

**Diagnóstico:**
```bash
docker-compose -f docker-compose.production.yml logs backend | grep ERROR | tail -50

grep '"level":"ERROR"' /mnt/c/wamp64/www/Saas-inicial/logs/errors.log | tail -20
```

**Soluciones:**
1. Errores de DB → Verificar conectividad y migraciones
2. Errores de integración externa (MercadoPago, OpenAI) → Revisar credenciales y status
3. Errores de código → Considerar rollback

---

## 8. Mantenimiento Programado

### Reinicio Mensual de Servicios
```bash
docker-compose -f docker-compose.production.yml restart backend worker beat
```

### Limpieza de Logs Antiguos
```bash
find /mnt/c/wamp64/www/Saas-inicial/logs -name "*.log" -mtime +30 -exec gzip {} \;
find /mnt/c/wamp64/www/Saas-inicial/logs -name "*.log.gz" -mtime +90 -delete
```

### Vacuum de PostgreSQL
```bash
docker exec saas-postgres-prod psql -U prod_user -d saas_cafeterias_prod -c "VACUUM ANALYZE;"
```

### Actualización de Certificados SSL
```bash
certbot renew --nginx

docker-compose -f docker-compose.production.yml restart nginx
```

---

## 9. Monitoreo y Alertas

### Dashboards Clave en Grafana
1. **API Health** - Request rate, error rate, response time
2. **Database Performance** - Connections, queries, table sizes
3. **Business Metrics** - Users, orders, revenue

### Alertas Críticas (Requieren Acción Inmediata)
- **APIDown** - Backend caído por > 2min
- **HighErrorRate** - Error rate > 5% por 5min
- **DatabaseConnectionsFull** - Pool casi lleno
- **DiskSpaceCritical** - < 5% espacio disponible
- **SSLCertificateExpiring** - Certificado vence en < 7 días
- **BackupFailed** - No hay backup en 2 días

### Alertas de Warning (Revisar en Horario Laboral)
- **SlowResponseTime** - P95 > 1s
- **HighMemoryUsage** - > 90% memoria
- **CeleryQueueBacklog** - > 100 tasks pendientes

---

## 10. Seguridad

### Rotar Secrets
```bash
python3 -c "import secrets; print(f'NEW_SECRET_KEY={secrets.token_urlsafe(64)}')"

vim .env.production

docker-compose -f docker-compose.production.yml restart backend worker beat
```

### Revisar Logs de Seguridad
```bash
grep '"security_event"' /mnt/c/wamp64/www/Saas-inicial/logs/security.log | tail -50

grep '"event":"login_failure"' /mnt/c/wamp64/www/Saas-inicial/logs/security.log | jq -r '.ip_address' | sort | uniq -c | sort -rn
```

### Bloquear IP Maliciosa en Nginx
```nginx
# Agregar a nginx.prod.conf
deny 123.456.789.0;
```
```bash
docker-compose -f docker-compose.production.yml restart nginx
```

---

## 11. Escalamiento

### Escalar Workers Horizontalmente
```bash
docker-compose -f docker-compose.production.yml up -d --scale worker=3
```

### Escalar Backend (Requiere Load Balancer)
```bash
docker-compose -f docker-compose.production.yml up -d --scale backend=2
```

### Aumentar Recursos de Contenedor
Editar `docker-compose.production.yml`:
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```
```bash
docker-compose -f docker-compose.production.yml up -d backend
```

---

## 12. Respaldo de Configuración

### Backup de Configuración Crítica
```bash
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env.production \
  docker-compose.production.yml \
  nginx/nginx.prod.conf \
  monitoring/alerts/production.yml
```

### Backup de Secrets
```bash
gpg --symmetric --cipher-algo AES256 .env.production
mv .env.production.gpg /secure/backup/location/
```

---

**Fin del Runbook**
