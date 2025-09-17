# 🗺️ Roadmap - Cafetería IA (ModularBiz SaaS)

Este roadmap guía la evolución del proyecto paso a paso.  
Cada fase debe ejecutarse en orden, dejando registro en `CHANGELOG.md`.

---

## ✅ Fase 1 — Autenticación y Usuarios (completado en gran parte)
- [x] Registro, login y refresh token.
- [x] Perfil de usuario (`/me`).
- [x] CRUD básico de usuarios.

---

## ✅ Fase 2 — Negocios y Productos (completado)
- [x] CRUD de negocios (crear, listar, editar, eliminar).
- [x] CRUD de productos (crear, listar, editar, eliminar).
- [x] Relación usuarios ↔ negocios (dueños de negocio).
- [x] Validaciones y permisos: sólo dueños pueden modificar su negocio/productos.

---

## ✅ Fase 3 — Carrito y Checkout (completado)
- [x] Implementar carrito en frontend.
- [x] API de checkout en backend.
- [ ] Integrar **MercadoPago** (sandbox primero).
- [x] Manejo de estados de pedido (pendiente, pagado, entregado).

---

## ✅ Fase 4 — Dashboard de Analytics (completado)
- [x] Endpoint para estadísticas (ventas totales, productos más vendidos).
- [x] Interfaz en frontend para dueños de negocio.
- [x] Visualizaciones con gráficas simples (ej: ventas por día).

---

## ✅ Fase 5 — Integración de IA (completado)
- [x] Configurar asistente básico (ej: sugerencias de productos, análisis de ventas).
- [x] Integración con API externa (ej: OpenAI).
- [x] Guardar prompts/respuestas en base de datos.

---

## ✅ Fase 6 — Producción y Optimización (completado)
- [x] Migraciones de base de datos con **Alembic**.
- [x] Configuración de PostgreSQL en producción.
- [x] Seguridad (CORS, rate limiting, HTTPS).
- [x] CI/CD con tests automáticos.
- [x] Despliegue en servidor (ej: Railway, Render, VPS).

---

### Notas
- Cada fase completada debe registrarse en `CHANGELOG.md`.
- Si se reestructura el proyecto (archivos, carpetas), anotarlo también en `CHANGELOG.md`.
