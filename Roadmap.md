# 📍 Roadmap — Cafeteria IA

Este roadmap define **el orden de ejecución recomendado** para construir el scaffold inicial y avanzar con el producto.  
La idea es que cada fase sea **lineal, clara y ejecutable** para que un asistente de desarrollo (Claude, GPT, etc.) pueda trabajar sin ambigüedades.

---

## 🔹 Fase 0 — Preparación
1. Crear repositorio monorepo en GitHub con nombre `cafeteria-ia`.
2. Añadir archivos iniciales vacíos: `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `.gitignore`.
3. Configurar ramas: `main` (producción) y `dev` (desarrollo).

---

## 🔹 Fase 1 — Scaffold inicial (prioridad)
### Backend
- Crear estructura en `backend/app/` con carpetas: `api/v1/endpoints`, `core`, `db/{models,repositories}`, `schemas`, `services`, `workers`.
- Implementar `main.py` con FastAPI + CORS habilitado.
- Endpoints mínimos en `auth.py`:  
  - `POST /auth/register`  
  - `POST /auth/login`  
  - `POST /auth/refresh`  
  - `GET /auth/me`
- Modelos: `User`, `Cafe`, `Product`, `Order`.
- Configuración DB: `session.py` con SQLAlchemy y Alembic inicial.
- Servicio AI: `ai_service.py` con clase `OpenAIAdapter` (sin claves).
- `requirements.txt` con dependencias listadas.

### Frontend
- Estructura `cafe-frontend/src/{pages,components,services,store,types}`.
- Configuración Vite + Tailwind + TS.
- Servicios API (`services/api.ts`) usando `VITE_API_URL`.
- Pages mínimas: Login, Register, Cafes, CafeDetail, Checkout.
- Stores Zustand: `authStore`, `cartStore`.

### Docker & Compose
- `Dockerfile` backend (Python + uvicorn).
- `Dockerfile` frontend (Node + npm build).
- `docker-compose.yml` con servicios: postgres, redis, backend, frontend.

### CI/CD
- Workflow `.github/workflows/ci.yml` con:  
  - Lint + Tests backend.  
  - Build frontend.  
  - Seguridad básica (bandit/safety opcional).

---

## 🔹 Fase 2 — Configuración básica
1. Crear `.env.example` en backend y frontend.
2. Configurar `.gitignore` para excluir `.env` reales.
3. Añadir tests mínimos:  
   - Backend: `tests/test_health.py`  
   - Frontend: placeholder test con Vitest.
4. Completar `README.md` con instrucciones para levantar:  
   - Local (venv + uvicorn / npm dev).  
   - Docker Compose.

---

## 🔹 Fase 3 — MVP funcional
- Registro/login funcionando contra DB.
- CRUD básico de Cafés, Productos y Menús.
- Carrito + Checkout (sandbox MercadoPago).
- Órdenes con estados + historial.
- Dashboard inicial (ventas/pedidos).
- API documentada con Swagger (OpenAPI).

---

## 🔹 Fase 4 — Seguridad mínima
- JWT secreto largo + rotación.
- HTTPS en producción.
- Rate limiting (Redis o middleware).
- Validar webhooks de MercadoPago.
- CSRF solo si se usan cookies.

---

## 🔹 Fase 5 — IA inicial
- Activar capa AI en `ai_service.py`.
- Logs y cacheo de prompts.
- Endpoints:  
  - `POST /api/v1/assistant/`  
  - `GET /api/v1/analytics/sales`
- Guardar prompts en DB para iteración futura.

---

## 🔹 Fase 6 — Siguientes versiones (v2.0.0 → v3.2.0)
- v2.0: Multi-tenant inicial (tenant_id en modelos).
- v2.5: Automatizaciones (Celery/RQ + workers).
- v2.8: Integración CI/CD completa (Terraform/K8s opcional).
- v3.0: RLS en PostgreSQL para multi-tenant real.
- v3.2: Chatbot + predicción de demanda + notificaciones automáticas.

---

## ✅ Checklist Final para el desarrollador
1. Clonar repo y crear `.env` desde `.env.example`.
2. Levantar con `docker-compose up --build`.
3. Acceder a:  
   - Backend docs → [http://localhost:8000/docs](http://localhost:8000/docs)  
   - Frontend → [http://localhost:5173](http://localhost:5173)

---
