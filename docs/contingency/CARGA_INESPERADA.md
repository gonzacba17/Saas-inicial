# Plan de Contingencia: Carga Inesperada

## Síntomas
- Response time P95 > 2s (degradado)
- CPU usage > 80%
- Memory usage > 90%
- Request rate 5x-10x normal
- Usuarios reportan lentitud

## Diagnóstico Rápido
```bash
docker stats --no-stream

docker-compose -f docker-compose.production.yml logs backend | grep "response_time"

docker exec saas-postgres-prod psql -U prod_user -d saas_cafeterias_prod -c "
SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';
"
```

## Soluciones Inmediatas (< 15 min)

### 1. Escalar Workers Horizontalmente
```bash
docker-compose -f docker-compose.production.yml up -d --scale worker=3 --scale backend=2

docker-compose -f docker-compose.production.yml ps
```

### 2. Habilitar Cache Agresivo
```bash
docker exec saas-redis-prod redis-cli CONFIG SET maxmemory-policy allkeys-lru

docker-compose -f docker-compose.production.yml exec backend bash
export CACHE_TTL=300  # 5 min instead of 1 min
```

### 3. Aumentar Rate Limiting (Temporalmente)
Editar `nginx/nginx.prod.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=50r/m;  # era 100r/m
```
```bash
docker-compose -f docker-compose.production.yml restart nginx
```

### 4. Deshabilitar Features No Esenciales
```bash
export FEATURE_CHATBOT_ENABLED=false
export FEATURE_OCR_ENABLED=false
export FEATURE_EMAIL_NOTIFICATIONS=false
```

## Prevención
- [ ] Implementar auto-scaling
- [ ] Agregar CDN para assets estáticos
- [ ] Implementar caching más agresivo
- [ ] Load testing regular
