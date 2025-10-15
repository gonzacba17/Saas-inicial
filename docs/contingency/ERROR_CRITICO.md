# Plan de Contingencia: Error Crítico (Error Rate > 10%)

## Síntomas

- Alerta **HighErrorRate** disparada
- Error rate > 10% en últimos 5 minutos
- Dashboard muestra pico de 5xx errors
- Usuarios reportan errores al usar la app

## Diagnóstico Rápido (5 min)

### 1. Verificar en Grafana
```
Dashboard: API Health > Error Rate Panel
Buscar: Qué endpoints tienen más errores
```

### 2. Revisar Logs de Errores
```bash
docker-compose -f docker-compose.production.yml logs backend | grep ERROR | tail -100

grep '"level":"ERROR"' logs/errors.log | tail -50 | jq
```

### 3. Verificar Cambios Recientes
```bash
cat .deploy_version

git log --oneline --since="1 hour ago"
```

### 4. Verificar Dependencias Externas
```bash
curl -I https://api.mercadopago.com/v1/payments
curl -I https://api.openai.com/v1/models

docker-compose -f docker-compose.production.yml logs postgres | grep ERROR
docker exec saas-redis-prod redis-cli ping
```

## Causas Comunes

| Causa | Indicadores | Solución |
|-------|------------|----------|
| **Deploy reciente con bugs** | Errores empezaron post-deploy | Rollback inmediato |
| **Database down/slow** | Logs muestran connection errors | Reiniciar PostgreSQL o escalar |
| **Servicio externo caído** | Timeout errors, 502 de external API | Habilitar circuit breaker/fallback |
| **OOM (Out of Memory)** | Container restart events | Escalar recursos |
| **Migration fallida** | DB schema errors | Rollback migration |

## Soluciones por Prioridad

### SOLUCIÓN 1: Rollback (Si deploy fue hace < 2 horas)
```bash
bash scripts/rollback.sh

grep '"level":"ERROR"' logs/errors.log | tail -10
```
**Tiempo:** 5-10 min  
**Downtime:** ~60 segundos  

---

### SOLUCIÓN 2: Reiniciar Servicios Afectados
```bash
docker-compose -f docker-compose.production.yml restart backend worker

curl https://api.tu-dominio.com/health

docker-compose -f docker-compose.production.yml logs backend --tail=50
```
**Tiempo:** 2-3 min  
**Downtime:** ~30 segundos

---

### SOLUCIÓN 3: Deshabilitar Feature Problemático
```bash
docker-compose -f docker-compose.production.yml exec backend bash

export FEATURE_CHATBOT_ENABLED=false
export FEATURE_OCR_ENABLED=false

exit

docker-compose -f docker-compose.production.yml restart backend
```
**Tiempo:** 2 min  
**Downtime:** ~30 segundos

---

### SOLUCIÓN 4: Escalar Recursos (Si es problema de carga)
```bash
vim docker-compose.production.yml
```
```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 4G  # era 2G
        cpus: '2'   # era '1'
```
```bash
docker-compose -f docker-compose.production.yml up -d backend

docker stats --no-stream
```
**Tiempo:** 5 min  
**Downtime:** ~60 segundos

---

## Prevención para el Futuro

### Mejoras de Monitoreo
- [ ] Agregar alerta para error rate > 3% (warning antes de critical)
- [ ] Crear dashboard de "Error Analysis" por tipo de error
- [ ] Configurar Sentry para notificaciones de nuevos tipos de error

### Mejoras de Testing
- [ ] Aumentar coverage de tests de integración
- [ ] Agregar smoke tests automáticos post-deploy
- [ ] Implementar canary deployments (deploy gradual)

### Mejoras de Código
- [ ] Implementar circuit breakers para servicios externos
- [ ] Mejorar manejo de errores y logging
- [ ] Agregar timeouts a todas las llamadas externas
- [ ] Implementar retries con exponential backoff

### Mejoras de Proceso
- [ ] Siempre hacer deploy en horario laboral (no viernes/noche)
- [ ] Mantener alguien monitoreando 30 min post-deploy
- [ ] Crear checklist de "deploy readiness"

## Checklist de Verificación Post-Fix

- [ ] Error rate < 1% en últimos 15 min
- [ ] No hay logs de ERROR en últimos 5 min
- [ ] Health check retorna 200 OK
- [ ] Smoke tests pasan
- [ ] Dashboards de Grafana normales
- [ ] Comunicar a usuarios si fue impacto significativo
- [ ] Programar post-mortem para mañana
