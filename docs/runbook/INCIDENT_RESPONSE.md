# Incident Response Plan

## Clasificación de Severidad

| Severidad | Descripción | Tiempo de Respuesta | Escalamiento |
|-----------|-------------|---------------------|--------------|
| **SEV-1 Crítico** | Sistema completamente caído, pérdida de datos, brecha de seguridad | 15 min | Inmediato a CTO |
| **SEV-2 Alto** | Funcionalidad crítica afectada, degradación severa | 1 hora | DevOps Lead |
| **SEV-3 Medio** | Funcionalidad secundaria afectada, workaround disponible | 4 horas | Team asignado |
| **SEV-4 Bajo** | Cosmético, mejora, documentación | Best effort | Backlog |

## Procedimiento de Respuesta

### 1. Detección (0-5 min)
- [ ] Alerta recibida (Prometheus/Grafana/Sentry/Usuario)
- [ ] Verificar en monitoring que el problema es real
- [ ] Determinar severidad inicial
- [ ] Crear incident ticket

### 2. Respuesta Inicial (5-15 min)
- [ ] Notificar a on-call engineer
- [ ] Crear canal de comunicación (#incident-YYYYMMDD)
- [ ] Asignar Incident Commander
- [ ] Iniciar logging de acciones en ticket

### 3. Investigación (15-45 min)
- [ ] Revisar dashboards de Grafana
- [ ] Revisar logs (errors.log, backend logs)
- [ ] Verificar cambios recientes (deploys, configs)
- [ ] Reproducir el problema si es posible
- [ ] Documentar findings en ticket

### 4. Mitigación (45 min - 2 hrs)
- [ ] Implementar fix o workaround
- [ ] Ejecutar rollback si es necesario
- [ ] Verificar que el problema se resolvió
- [ ] Comunicar status a stakeholders

### 5. Resolución
- [ ] Confirmar que todas las métricas están normales
- [ ] Cerrar alerta en AlertManager
- [ ] Actualizar ticket con resolución
- [ ] Comunicar cierre del incidente

### 6. Post-Mortem (24-48 hrs después)
- [ ] Programar sesión de post-mortem
- [ ] Documentar timeline completo
- [ ] Identificar causa raíz
- [ ] Crear action items preventivos
- [ ] Publicar post-mortem doc

## Templates de Comunicación

### Notificación Inicial (SEV-1/SEV-2)
```
🚨 INCIDENT ALERT - SEV-[1/2]

Título: [Descripción breve]
Inicio: [HH:MM UTC]
Impacto: [Qué está afectado]
Status: Investigando

Incident Commander: @[nombre]
Canal: #incident-YYYYMMDD
Ticket: INC-[número]

Updates cada 30 minutos.
```

### Update de Progreso
```
📊 UPDATE - [HH:MM UTC]

Findings: [Qué se encontró]
Acción: [Qué se está haciendo]
ETA: [Tiempo estimado de resolución]
Next update: [HH:MM UTC]
```

### Resolución
```
✅ RESOLVED - [HH:MM UTC]

Duración: [XX min]
Causa: [Descripción]
Fix: [Qué se hizo]
Preventivo: [Qué haremos para evitarlo]

Post-mortem: [Link cuando esté listo]
```

## Post-Mortem Template

```markdown
# Post-Mortem: [Título del Incidente]

**Fecha:** YYYY-MM-DD  
**Severity:** SEV-X  
**Duración:** XX minutos  
**Incident Commander:** [Nombre]

## Resumen Ejecutivo
[2-3 líneas describiendo qué pasó]

## Impacto
- **Usuarios afectados:** [número/porcentaje]
- **Revenue impactado:** $[cantidad]
- **Duración:** [HH:MM]

## Timeline

| Hora (UTC) | Evento |
|------------|--------|
| 14:32 | Alerta disparada: HighErrorRate |
| 14:35 | On-call engineer notificado |
| 14:40 | Investigación iniciada |
| 14:55 | Causa raíz identificada |
| 15:10 | Fix desplegado |
| 15:15 | Verificación completada |
| 15:20 | Incidente cerrado |

## Causa Raíz
[Descripción técnica detallada]

## Resolución
[Qué se hizo para resolver]

## Qué Funcionó Bien
- [Item 1]
- [Item 2]

## Qué Podemos Mejorar
- [Item 1]
- [Item 2]

## Action Items
- [ ] [Acción preventiva 1] - @owner - [fecha]
- [ ] [Acción preventiva 2] - @owner - [fecha]
- [ ] [Mejora de monitoreo] - @owner - [fecha]

## Lessons Learned
[Conclusiones y aprendizajes]
```
