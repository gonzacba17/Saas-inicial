# Plan de Contingencia: Problemas con Pagos

## Síntomas
- Webhooks de MercadoPago fallando
- Alerta **HighPaymentFailureRate** disparada
- Payment success rate < 90%
- Usuarios reportan que no pueden pagar

## Diagnóstico
```bash
docker-compose -f docker-compose.production.yml logs backend | grep "payment\|webhook"

grep '"endpoint":"/api/v1/payments"' logs/app.log | grep ERROR | tail -20

grep '"endpoint":"/api/v1/webhooks/mercadopago"' logs/app.log | tail -50
```

## Causas Comunes
1. **Credenciales de MercadoPago expiradas/inválidas**
2. **Webhook signature validation fallando**
3. **MercadoPago API caída**
4. **Network issues**
5. **Database locks en tabla payments**

## Soluciones

### 1. Verificar Credenciales
```bash
grep MERCADOPAGO .env.production

curl -H "Authorization: Bearer $MERCADOPAGO_ACCESS_TOKEN" \
  https://api.mercadopago.com/v1/account/me
```

### 2. Verificar Status de MercadoPago
```
https://status.mercadopago.com/
https://www.mercadopago.com.ar/developers/es/support
```

### 3. Reenvío Manual de Webhooks
```bash
docker exec saas-postgres-prod psql -U prod_user -d saas_cafeterias_prod
```
```sql
SELECT id, mp_payment_id, status, created_at 
FROM payments 
WHERE status = 'pending' 
  AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

Para cada payment pendiente, forzar recheck:
```bash
curl -X POST https://api.tu-dominio.com/api/v1/payments/{id}/check-status \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 4. Contacto de Emergencia
**MercadoPago Support:**
- Email: developers@mercadopago.com
- Teléfono: +54 11 5984-2100
- Dashboard: https://www.mercadopago.com.ar/developers/panel

## Prevención
- [ ] Monitorear payment success rate
- [ ] Agregar retry logic para webhooks
- [ ] Implementar manual payment verification endpoint
- [ ] Documentar proceso de rotación de credentials
