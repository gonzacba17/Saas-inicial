# 📌 Roadmap del Proyecto Saas-inicial

## ✅ Ya logrado
- Scaffold inicial del proyecto SaaS (backend FastAPI + frontend React/TS + Vite + Tailwind).
- Estructura de carpetas organizada.
- Archivos base (`README.md`, `.gitignore`, `Changelog.md`, `Roadmap.md`).
- GitHub repo inicializado.

---

## 🚀 Sprint 1 — MVP funcional (local con PostgreSQL)

### Backend ✅ COMPLETADO
- [x] Configurar `.env` con conexión a PostgreSQL local.
- [x] Crear base de datos `saas_db` en PostgreSQL local.
- [x] Configurar Alembic (`alembic/` + `env.py`).
- [x] Crear modelos principales en `backend/app/db/models/`:
  - `User` (UUID, email, hashed password, role).
  - `Business` (equivalente a Cafe - id, nombre, dueño, dirección).
  - `Product` (id, nombre, precio, business_id).
  - `Order` (id, usuario, productos, estado, total).
- [x] Generar migraciones iniciales (`alembic revision --autogenerate` + `alembic upgrade head`).
- [x] Implementar endpoints Auth:
  - `/api/v1/auth/register`
  - `/api/v1/auth/login`
  - `/api/v1/auth/refresh`
  - `/api/v1/auth/me`
- [x] CRUD básico:
  - `/api/v1/businesses` (crear, listar, actualizar, eliminar)
  - `/api/v1/products` (crear, listar, actualizar, eliminar)
- [x] Orders:
  - `/api/v1/orders` (crear orden, ver estado, gestión completa)

### Frontend ✅ COMPLETADO
- [x] Conectar formularios **Login/Register** con backend real.
- [x] Crear vistas:
  - Listado de negocios (equivalente a cafés) ✅
  - Listado de productos ✅
  - Carrito (Zustand store) ✅
  - Checkout (funcional con backend real) ✅
- [x] Manejo de sesión (guardar JWT, refrescar token, logout).
- [x] Proteger rutas que requieran login.

---

## 💳 Sprint 2 — Pagos y Dashboard

- [ ] Integrar **MercadoPago sandbox** en backend:
  - `/api/v1/payments/create`
  - `/api/v1/payments/webhook`
- [ ] Configurar `MERCADOPAGO_KEY` en `.env`.
- [ ] Endpoint `/api/v1/analytics/sales` con métricas básicas.
- [ ] Frontend: `Dashboard.tsx` con KPIs (ventas, pedidos, top productos).
- [ ] Seguridad:
  - SECRET_KEY fuerte
  - CORS correcto
  - `.env` ignorado en git
- [ ] Tests básicos:
  - Backend (`tests/test_auth.py`, `tests/test_orders.py`)
  - Frontend (Vitest/RTL en `LoginForm`, `RegisterForm`, `Dashboard`)

---

## ⚙️ Sprint 3 — Calidad y CI/CD

- [ ] CI en GitHub Actions (`.github/workflows/ci.yml`):
  - Backend → lint (flake8/ruff), pytest
  - Frontend → eslint, build, vitest
- [ ] Agregar checks de seguridad (bandit, safety)
- [ ] Documentación actualizada (`README.md`, `CHANGELOG.md`, `ROADMAP.md`)

---

## 🤖 Sprint 4 — IA y features avanzadas

- [ ] Implementar `app/services/ai_service.py`
- [ ] Endpoint `/api/v1/analytics/insights` que use OpenAI (si configuras key)
- [ ] Guardar prompts y respuestas en DB
- [ ] Configurar Celery/RQ con Redis (opcional)
- [ ] Workers para notificaciones o análisis async

---

## 📑 Mantenimiento continuo
- Mantener **CHANGELOG.md** actualizado con cada feature.
- Actualizar **README.md** con nuevos comandos y configuraciones.
- Revisar dependencias y actualizar (`pip list --outdated`, `npm outdated`).

