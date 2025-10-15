# Pre-Deploy Checklist - Production v1.0

**Fecha de verificación:** _________  
**Responsable:** _________  
**Versión a desplegar:** _________

---

## ✅ FASE 1: VALIDACIÓN TÉCNICA

### Tests y Calidad de Código
- [ ] **Tests pasando:** `pytest tests/ -v` ✅ 23+ tests passing
- [ ] **Coverage aceptable:** `pytest --cov=app` ≥ 40%
- [ ] **Linting:** `flake8 backend/app` sin errores críticos
- [ ] **Type hints:** `mypy backend/app` sin errores
- [ ] **Security scan:** `bandit -r backend/app` sin HIGH/MEDIUM
- [ ] **Dependencies check:** `pip-audit` sin vulnerabilidades críticas

### Database
- [ ] **Migraciones aplicadas:** `alembic current` muestra última migración
- [ ] **Migraciones testeadas:** Aplicadas en staging sin errores
- [ ] **Rollback plan:** Migraciones reversibles o backup disponible
- [ ] **Indexes creados:** Verificar en migration 004

### Docker & Build
- [ ] **Docker build exitoso:** `docker-compose -f docker-compose.production.yml build`
- [ ] **No hay secretos en imágenes:** Verificar que .env no está en imagen
- [ ] **Health checks configurados:** Todos los servicios tienen healthcheck
- [ ] **Resource limits:** CPU y memory limits configurados

---

## ✅ FASE 2: INFRAESTRUCTURA

### Configuración de Producción
- [ ] **`.env.production` existe** y está completo
- [ ] **Secrets generados:** SECRET_KEY y JWT_SECRET_KEY únicos de 64 chars
- [ ] **Database credentials:** Credenciales de producción configuradas
- [ ] **Redis password:** Configurado y distinto a default
- [ ] **ALLOWED_ORIGINS:** Dominio de producción configurado
- [ ] **DEBUG=false** ✅ CRÍTICO

### SSL/TLS & DNS
- [ ] **Certificados SSL generados:** Verificar `/nginx/ssl/`
- [ ] **DNS configurado:** `nslookup api.tu-dominio.com`
- [ ] **DNS configurado:** `nslookup tu-dominio.com`
- [ ] **Certificados válidos:** `openssl x509 -in fullchain.pem -noout -dates`
- [ ] **Auto-renewal configurado:** Certbot cron job activo

### Backups
- [ ] **Backup script funciona:** `bash scripts/backup.sh`
- [ ] **Último backup verificado:** Menos de 24h antiguo
- [ ] **Backup automático configurado:** Cron job o scheduler
- [ ] **Restauración testeada:** Backup puede restaurarse exitosamente
- [ ] **Retención configurada:** Backups de 30 días

---

## ✅ FASE 3: MONITORING & OBSERVABILITY

### Prometheus & Alertas
- [ ] **Prometheus corriendo:** `curl http://localhost:9090/-/healthy`
- [ ] **Alertas cargadas:** Verificar `/monitoring/alerts/production.yml`
- [ ] **Reglas válidas:** `promtool check rules production.yml`
- [ ] **Targets configurados:** Backend, DB, Redis visibles en Prometheus
- [ ] **AlertManager configurado:** Notificaciones funcionando

### Grafana
- [ ] **Grafana accesible:** `curl http://localhost:3000/api/health`
- [ ] **Dashboards importados:** API Health, Database, Business Metrics
- [ ] **Datasource Prometheus:** Conectado y funcionando
- [ ] **Credenciales cambiadas:** No usar admin/admin default

### Sentry
- [ ] **SENTRY_DSN configurado** en .env.production
- [ ] **Environment=production** configurado
- [ ] **Test error enviado:** Verificar que llega a Sentry
- [ ] **Alertas configuradas:** Email/Slack para errores críticos

### Logs
- [ ] **Directorio de logs:** `/app/logs` o equivalente existe
- [ ] **Rotation configurada:** Logs no llenarán disco
- [ ] **Structured logging:** JSON format activado
- [ ] **Log levels correctos:** INFO en prod, no DEBUG

---

## ✅ FASE 4: SEGURIDAD

### Secrets & Credentials
- [ ] **.env.production en .gitignore** ✅ CRÍTICO
- [ ] **Secrets únicos:** No reutilizar de staging/dev
- [ ] **API keys válidas:** MercadoPago PRODUCTION keys
- [ ] **OpenAI key válida:** Testeada y con créditos
- [ ] **No hay secrets en código:** Scan completo
- [ ] **Vault/Secrets Manager:** Configurado si aplica

### Network & Access
- [ ] **Firewall configurado:** Solo puertos 80, 443 expuestos
- [ ] **SSH keys only:** Password auth deshabilitado
- [ ] **Database no expuesta:** Solo accesible internamente
- [ ] **Redis no expuesta:** Solo accesible internamente
- [ ] **Rate limiting activo:** Nginx configurado
- [ ] **CORS configurado:** Solo dominios permitidos

### Headers de Seguridad
- [ ] **HSTS habilitado** en nginx
- [ ] **X-Frame-Options:** DENY
- [ ] **X-Content-Type-Options:** nosniff
- [ ] **Referrer-Policy** configurado
- [ ] **CSP headers:** Configurados si aplica

---

## ✅ FASE 5: SMOKE TESTS

### Staging Verification
- [ ] **Staging health check:** `curl https://staging-api/health`
- [ ] **Staging uptime:** > 24 horas
- [ ] **Staging logs limpios:** Sin errores recurrentes
- [ ] **Staging smoke tests:** `bash scripts/smoke_tests.sh staging` ✅

### Pre-Production Tests
- [ ] **Build en staging exitoso:** Docker compose up -d funciona
- [ ] **Migrations en staging:** Aplicadas sin errores
- [ ] **Performance aceptable:** P95 < 1s en staging

---

## ✅ FASE 6: DOCUMENTACIÓN

### Runbooks
- [ ] **Production Runbook** creado y revisado
- [ ] **Incident Response** plan documentado
- [ ] **Contactos de emergencia** actualizados
- [ ] **Procedimientos de rollback** documentados

### Planes de Contingencia
- [ ] **Plan para Error Crítico** documentado
- [ ] **Plan para Carga Inesperada** documentado
- [ ] **Plan para Problemas de Pagos** documentado

### Knowledge Base
- [ ] **Comandos comunes** documentados
- [ ] **Troubleshooting** guide actualizado
- [ ] **Escalation path** definido

---

## ✅ FASE 7: TEAM READINESS

### On-Call
- [ ] **Schedule definido:** Quién está on-call
- [ ] **Contactos compartidos:** Teléfonos, Slack, emails
- [ ] **Alertas configuradas:** Notifications llegando
- [ ] **Runbook revisado:** On-call engineer lo leyó

### Communication
- [ ] **Stakeholders notificados:** Deploy window comunicado
- [ ] **Maintenance window:** Usuario saben que habrá deploy
- [ ] **Rollback plan comunicado:** Team sabe cómo hacer rollback
- [ ] **Post-deploy monitoring:** Alguien monitoreará 2h post-deploy

---

## ✅ FASE 8: GO/NO-GO DECISION

### Critical Blockers (Must be ✅)
- [ ] **No hay bugs críticos abiertos** (SEV-1)
- [ ] **Staging está estable** (> 24h uptime)
- [ ] **Tests críticos pasando** (auth, orders, payments)
- [ ] **Backup funciona** y está verificado
- [ ] **Rollback plan listo** y testeado

### Risk Assessment
**¿Es viernes o fin de semana?** → ❌ NO DEPLOY (esperar lunes)  
**¿Hay alguien on-call disponible?** → ⚠️ REQUIRED  
**¿Hay cambios de DB schema?** → ⚠️ Mayor riesgo, backup crítico  
**¿Es primer deploy a prod?** → ⚠️ Monitoreo extra intensivo  

### Final Checks
- [ ] **Tiempo asignado suficiente:** 2-3 horas disponibles
- [ ] **Window de deploy adecuada:** Horario laboral, lunes-jueves
- [ ] **Team disponible:** DevOps + Backend + DBA disponibles
- [ ] **Plan B listo:** Rollback script testeado

---

## 🚀 DEPLOYMENT EXECUTION

### Pre-Deploy
```bash
cd /mnt/c/wamp64/www/Saas-inicial
git pull origin main
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

### Deploy
```bash
export DEPLOY_TAG=v1.0.0
bash scripts/deploy_production.sh
```

### Post-Deploy Monitoring (First 2 hours)
- [ ] **T+5min:** Health check OK
- [ ] **T+5min:** Smoke tests passing
- [ ] **T+15min:** No errors en logs
- [ ] **T+30min:** Métricas normales (CPU, memory, response time)
- [ ] **T+1h:** Error rate < 1%
- [ ] **T+2h:** No alerts disparadas
- [ ] **T+2h:** Usuarios no reportan problemas

---

## 📊 SUCCESS CRITERIA (First Week)

- **Uptime:** > 99% (máximo 1.68h downtime en 7 días)
- **Error Rate:** < 1% de requests
- **Response Time:** P95 < 500ms
- **Zero Data Loss:** Todos los backups OK
- **Monitoring:** Dashboards visibles, alertas sin falsos positivos

---

## 🔴 ROLLBACK TRIGGERS

Ejecutar rollback inmediato si:
- Error rate > 10% por más de 5 minutos
- API completamente caída por > 5 minutos
- Data corruption detectada
- Brecha de seguridad crítica
- Performance degradada > 5x (P95 > 5s)

```bash
bash scripts/rollback.sh
```

---

**APROBACIÓN FINAL:**

- [ ] **DevOps Lead:** _________________ Fecha: _______
- [ ] **Backend Lead:** _________________ Fecha: _______
- [ ] **Product Owner:** _________________ Fecha: _______

**Estado:** ⬜ GO / ⬜ NO-GO

**Razón si NO-GO:** _________________________________

---

**Notas adicionales:**

_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
