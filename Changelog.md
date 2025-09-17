# Changelog

Todos los cambios notables de **ModularBiz SaaS** serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - v0.3.0

### 🎯 Próxima Release: MVP Core
- [ ] **Added**: CRUD completo de productos con validaciones
- [ ] **Added**: Sistema de órdenes con estados y pagos
- [ ] **Added**: Integración MercadoPago (sandbox + producción)
- [ ] **Added**: Dashboard administrativo con métricas
- [ ] **Added**: Carrito de compras funcional
- [ ] **Changed**: Modelos extendidos para e-commerce completo
- [ ] **Changed**: Frontend mejorado con UX profesional

---

## [0.2.1] - 2025-09-17

### 🚀 Transformación a SaaS Modular

### Added
- ✅ **Branding**: Evolución de "Cafetería IA" a "ModularBiz SaaS"
- ✅ **Documentation**: README actualizado con enfoque SaaS modular
- ✅ **Roadmap**: Plan de desarrollo estructurado por fases con MVP claro
- ✅ **Versioning**: Changelog con versionado semántico implementado

### Changed  
- ✅ **Architecture**: Transición hacia plataforma multi-rubro
- ✅ **Naming**: Nomenclatura de archivos y variables hacia contexto SaaS
- ✅ **Strategy**: Enfoque en MVP real (Auth + CRUD + Payments)

---

## [0.2.0] - 2025-09-16

### 🏗️ Scaffold Completo - Base Sólida

### Added
- Backend:
  - Modelos: User, Cafe, Product, Order, OrderItem
  - Endpoints auth: register, login, refresh, me
  - AI Service con OpenAIAdapter
  - Workers (Celery/Redis) configurados
  - Tests básicos con pytest
- Frontend:
  - Páginas: Login, Register, Cafes, CafeDetail, Checkout
  - Zustand stores: authStore y cartStore
  - Navegación completa con React Router
  - Tests básicos con Vitest
- Infraestructura:
  - Docker Compose con PostgreSQL, Redis, backend y frontend
  - GitHub Actions con lint + tests + build
  - Archivos `.env.example` (backend + frontend)

### Changed
- README.md ampliado con instrucciones para Windows PowerShell y Docker
- `.gitignore` optimizado

### Fixed
- Configuración inicial de autenticación funcionando
- Ajustes menores en dependencias

### Removed
- Archivos temporales previos al scaffold final
