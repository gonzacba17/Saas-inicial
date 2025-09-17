# 🚀 Roadmap — ModularBiz SaaS

**De Cafetería IA hacia una plataforma SaaS modular**

Este roadmap define la evolución del proyecto desde su base como "Cafetería IA" hacia una **plataforma SaaS escalable** que puede adaptarse a cualquier rubro de negocio. Cada fase está diseñada para ser **ejecutable, clara y mensurable**.

---

## 🔹 Fase 0 — Preparación ✅ COMPLETADA
1. ✅ Crear repositorio monorepo en GitHub con nombre `modularbiz-saas`.
2. ✅ Añadir archivos iniciales: `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `.gitignore`.
3. ✅ Configurar ramas: `main` (producción) para despliegues estables.
4. ✅ Migrar de "Cafetería IA" hacia arquitectura SaaS modular.

---

## 🔹 Fase 1 — Scaffold inicial ✅ COMPLETADA

### Backend ✅
- ✅ Estructura modular en `backend/app/` con separación clara de responsabilidades
- ✅ FastAPI con CORS y documentación automática 
- ✅ Endpoints de autenticación JWT completos:
  - `POST /api/v1/auth/register` - Registro de usuarios
  - `POST /api/v1/auth/login` - Login con JWT
  - `POST /api/v1/auth/refresh` - Renovación de tokens
  - `GET /api/v1/auth/me` - Perfil de usuario
- ✅ Modelos base: `User`, `Business`, `Product`, `Order`
- ✅ SQLAlchemy + Alembic para migraciones
- ✅ OpenAI service preparado para integración futura

### Frontend ✅  
- ✅ React + TypeScript + Vite + Tailwind CSS
- ✅ Arquitectura de componentes reutilizables
- ✅ Páginas base: Login, Register, Dashboard, Checkout
- ✅ Zustand para gestión de estado (auth + carrito)
- ✅ API client con interceptors para JWT

### Infrastructure ✅
- ✅ Docker Compose para desarrollo local
- ✅ PostgreSQL + Redis + Backend + Frontend
- ✅ GitHub Actions con lint, tests y build automatizado
- ✅ Testing setup (Pytest + Vitest)

---

## 🔹 Fase 2 — Configuración básica ✅ COMPLETADA
1. ✅ Archivos `.env.example` configurados (backend + frontend)
2. ✅ `.gitignore` optimizado para entornos de desarrollo
3. ✅ Tests base implementados:
   - Backend: `tests/test_health.py` con pytest
   - Frontend: setup con Vitest + testing-library
4. ✅ `README.md` completo con instrucciones detalladas
5. ✅ Documentación de API automática con FastAPI

---

## 🔹 Fase 3 — MVP Core (v0.3.0) 🚧 EN DESARROLLO

### 🎯 Objetivo: SaaS funcional con flujo completo de e-commerce

### Backend API
- [ ] **CRUD Productos completo**
  - `GET /api/v1/products/` - Lista paginada con filtros
  - `POST /api/v1/products/` - Crear producto
  - `PUT /api/v1/products/{id}` - Actualizar producto  
  - `DELETE /api/v1/products/{id}` - Eliminar producto
  - Validaciones, imágenes, categorías

- [ ] **Sistema de Órdenes**
  - `POST /api/v1/orders/` - Crear pedido
  - `GET /api/v1/orders/` - Historial de pedidos
  - `GET /api/v1/orders/{id}` - Detalle de pedido
  - Estados: pending, paid, processing, completed, cancelled

- [ ] **Integración MercadoPago**
  - `POST /api/v1/payments/create-preference` - Crear preferencia MP
  - `POST /api/v1/payments/webhook` - Webhook de notificaciones
  - `GET /api/v1/payments/{order_id}/status` - Estado de pago
  - Manejo de sandbox y producción

### Frontend Features
- [ ] **Dashboard de productos**
  - Lista con búsqueda y filtros
  - Formularios de creación/edición
  - Gestión de imágenes/categorías

- [ ] **Carrito y Checkout**
  - Agregar/quitar productos
  - Checkout con formulario de datos
  - Integración con MercadoPago Checkout Pro
  - Confirmación y seguimiento de pedidos

- [ ] **Panel de administración**
  - Dashboard con métricas básicas
  - Gestión de pedidos
  - Reportes de ventas

### Database & Models
- [ ] **Extend modelos existentes**
  - `Product`: añadir categorías, stock, imágenes
  - `Order`: estados, líneas de pedido, totales
  - `Payment`: integración con MP, webhooks
  - Migraciones Alembic

---

## 🔹 Fase 4 — Productización (v0.4.0)

### 🛡️ Seguridad & Performance
- [ ] **Rate Limiting** con Redis middleware
- [ ] **Input Validation** exhaustiva (Pydantic + sanitización)
- [ ] **CORS** configurado para producción
- [ ] **Logging** estructurado (JSON + rotación)
- [ ] **Health Checks** para monitoring

### 🚀 Deployment Ready
- [ ] **Environment configs** (dev/staging/prod)
- [ ] **Database connection pooling**
- [ ] **Static file serving** optimizado
- [ ] **Error handling** unificado
- [ ] **API versioning** strategy

---

## 🔹 Fase 5 — Multi-tenant & Scaling (v0.5.0)

### 🏢 Multi-tenant Architecture
- [ ] **Business/Tenant model** - Un SaaS, múltiples negocios
- [ ] **User-Business relationship** - Usuarios pueden tener múltiples negocios
- [ ] **Data isolation** por tenant
- [ ] **Onboarding flow** para nuevos negocios

### 🤖 AI Integration (Opcional)
- [ ] **Activar OpenAI service** con claves reales
- [ ] **Analytics endpoint** para insights de ventas
- [ ] **Product recommendations** basadas en histórico
- [ ] **Chat assistant** para soporte a clientes

---

## 🔹 Fase 6 — Advanced Features (v1.0.0+)

### 📊 Business Intelligence
- [ ] **Advanced analytics** - Métricas detalladas por negocio
- [ ] **Export capabilities** - PDF/Excel reports
- [ ] **Inventory management** - Control de stock automático
- [ ] **Customer management** - CRM básico integrado

### 🔄 Automation & Integrations  
- [ ] **Background workers** con Celery
- [ ] **Email notifications** - Confirmaciones, recordatorios
- [ ] **Webhook system** para integraciones externas
- [ ] **API rate limiting** por tier de suscripción

---

## ✅ Checklist Final para el desarrollador
1. Clonar repo y crear `.env` desde `.env.example`.
2. Levantar con `docker-compose up --build`.
3. Acceder a:  
   - Backend docs → [http://localhost:8000/docs](http://localhost:8000/docs)  
   - Frontend → [http://localhost:5173](http://localhost:5173)

---
