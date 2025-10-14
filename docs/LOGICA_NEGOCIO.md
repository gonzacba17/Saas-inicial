# 🏪 Lógica de Negocio - SaaS Cafeterías

> **Documentación completa del modelo de negocio, entidades, flujos y reglas**  
> **Última actualización:** Octubre 2025

---

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Entidades del Sistema](#-entidades-del-sistema)
- [Roles y Permisos](#-roles-y-permisos)
- [Flujos de Trabajo](#-flujos-de-trabajo)
- [Reglas de Negocio](#-reglas-de-negocio)
- [Estados y Transiciones](#-estados-y-transiciones)
- [Integraciones](#-integraciones)

---

## 🎯 Visión General

### ¿Qué es SaaS Cafeterías?

Sistema multi-tenant para gestión integral de cafeterías que permite a dueños de negocios administrar su operación completa: productos, pedidos, pagos y análisis de negocio con inteligencia artificial.

### Modelo de Negocio

**Multi-tenant SaaS** donde:
- Cada cafetería es un **Business** independiente
- Los usuarios pueden tener múltiples roles según el negocio
- Sistema centralizado con datos aislados por tenant
- Monetización por subscripción (futuro)

### Casos de Uso Principales

1. **Dueño de cafetería** crea cuenta → registra su negocio → configura menú → recibe pedidos
2. **Cliente** navega cafeterías → selecciona productos → realiza pedido → paga con MercadoPago
3. **Administrador** gestiona plataforma → da soporte → monitorea sistema
4. **Asistente IA** ayuda al dueño con análisis de ventas, sugerencias de productos, insights

---

## 📦 Entidades del Sistema

### 1. User (Usuario)

**Definición:** Persona con cuenta en el sistema

**Atributos principales:**
- `email` - Identificador único, usado para login
- `hashed_password` - Password encriptado con bcrypt
- `full_name` - Nombre completo
- `role` - Rol global (user, business_owner, admin)
- `is_active` - Estado de la cuenta
- `is_verified` - Email verificado (futuro)

**Tipos de usuarios:**
- **User (cliente)** - Puede hacer pedidos, ver historial
- **Business Owner** - Puede crear/gestionar negocios
- **Admin** - Control total del sistema

**Relaciones:**
- Un usuario puede tener **múltiples businesses** (como owner)
- Un usuario puede hacer **múltiples orders**
- Un usuario puede tener **múltiples conversaciones con IA**

**Ciclo de vida:**
```
Registro → Verificación email (futuro) → Activo → [Suspendido] → [Eliminado]
```

---

### 2. Business (Negocio/Cafetería)

**Definición:** Cafetería registrada en la plataforma

**Atributos principales:**
- `name` - Nombre del negocio (ej: "Café del Centro")
- `description` - Descripción marketing
- `address` - Dirección física
- `phone` - Teléfono contacto
- `email` - Email del negocio
- `owner_id` - Usuario dueño (FK a User)
- `is_active` - Si acepta pedidos
- `opening_hours` - Horarios JSON (futuro)
- `logo_url` - Logo (futuro)

**Modelo de tenancy:**
- **Un business = una cafetería independiente**
- Datos aislados: Los productos y pedidos de un business no se mezclan con otros
- Owner tiene control completo sobre su business

**Relaciones:**
- Un business pertenece a **un owner** (User)
- Un business tiene **múltiples products**
- Un business recibe **múltiples orders**
- Un business tiene **múltiples payments**

**Reglas:**
- Solo el owner puede modificar el business
- Un user puede crear hasta 5 businesses (límite configurable)
- Admin puede ver/modificar cualquier business

**Estados:**
- `is_active=true` - Acepta pedidos, visible en listados
- `is_active=false` - No acepta pedidos, no visible para clientes

---

### 3. Product (Producto)

**Definición:** Item del menú de una cafetería

**Atributos principales:**
- `name` - Nombre del producto (ej: "Cappuccino Grande")
- `description` - Descripción detallada
- `price` - Precio en la moneda local
- `category` - Categoría (bebidas, comidas, postres)
- `business_id` - Cafetería a la que pertenece (FK)
- `is_available` - Disponibilidad actual
- `image_url` - Foto del producto (futuro)
- `preparation_time` - Minutos estimados (futuro)

**Categorías:**
- Bebidas calientes (café, té, chocolate)
- Bebidas frías (jugos, smoothies, frappés)
- Comidas (sandwiches, ensaladas)
- Postres (tortas, galletas)
- Otros

**Relaciones:**
- Un producto pertenece a **un business**
- Un producto aparece en **múltiples order items**

**Reglas:**
- Solo el owner del business puede crear/modificar productos
- Precio debe ser > 0
- No se pueden eliminar productos con pedidos históricos (soft delete)
- `is_available` controla si aparece en el catálogo

**Inventario (futuro):**
- Stock management
- Alertas de bajo inventario
- Auto-disable cuando stock=0

---

### 4. Order (Pedido)

**Definición:** Solicitud de compra de un cliente

**Atributos principales:**
- `user_id` - Cliente que hace el pedido (FK)
- `business_id` - Cafetería donde se hace el pedido (FK)
- `status` - Estado actual (pending, confirmed, preparing, ready, delivered, cancelled)
- `total_amount` - Monto total calculado
- `notes` - Notas especiales del cliente
- `created_at` - Timestamp del pedido
- `updated_at` - Última actualización

**Relaciones:**
- Un order pertenece a **un user** (cliente)
- Un order pertenece a **un business**
- Un order contiene **múltiples order items**
- Un order tiene **un payment**

**Ciclo de vida completo:**
```
CREACIÓN
   ↓
pending (recién creado, esperando pago)
   ↓
confirmed (pago confirmado, business notificado)
   ↓
preparing (business comenzó preparación)
   ↓
ready (pedido listo para retirar/entregar)
   ↓
delivered (pedido completado)

En cualquier momento antes de "preparing":
   → cancelled (cancelado por user o business)
```

**Reglas de negocio:**
- Total mínimo: $0.01 (configurable por business)
- Solo el cliente puede crear su order
- Solo el business owner puede cambiar estado
- No se puede modificar order después de "confirmed"
- Cancelación permitida solo en estados "pending" o "confirmed"

---

### 5. OrderItem (Item del Pedido)

**Definición:** Línea individual dentro de un pedido

**Atributos principales:**
- `order_id` - Pedido al que pertenece (FK)
- `product_id` - Producto solicitado (FK)
- `quantity` - Cantidad
- `unit_price` - Precio unitario al momento del pedido
- `subtotal` - quantity × unit_price (calculado)
- `notes` - Personalizaciones (ej: "sin azúcar")

**Propósito:**
- Snapshot del producto en el momento del pedido
- Si el precio del producto cambia después, el order mantiene el precio original
- Permite múltiples productos en un solo pedido

**Reglas:**
- `unit_price` se copia del Product.price al crear
- `quantity` debe ser > 0
- `subtotal` se calcula automáticamente
- Productos deben pertenecer al mismo business del order

**Ejemplo:**
```json
Order #123:
  OrderItem 1: 2x Cappuccino Grande @ $3.50 = $7.00
  OrderItem 2: 1x Croissant @ $2.50 = $2.50
  Total: $9.50
```

---

### 6. Payment (Pago)

**Definición:** Transacción de pago asociada a un pedido

**Atributos principales:**
- `order_id` - Pedido asociado (FK)
- `amount` - Monto cobrado
- `status` - Estado (pending, approved, rejected, refunded)
- `payment_method` - Método (mercadopago, cash, card)
- `transaction_id` - ID externo de MercadoPago
- `payment_metadata` - JSON con datos del procesador
- `paid_at` - Timestamp de pago exitoso

**Estados de pago:**
- `pending` - Esperando confirmación
- `approved` - Pago confirmado
- `rejected` - Pago rechazado
- `refunded` - Pago reembolsado

**Integración MercadoPago:**
- Webhook recibe notificaciones de pago
- Validación de firma HMAC para seguridad
- Actualización automática de Order.status cuando payment=approved

**Relaciones:**
- Un payment pertenece a **un order**
- Un order tiene **un payment** (relación 1:1)

**Reglas:**
- Amount debe coincidir con Order.total_amount
- Solo Admin o Business Owner pueden ver payments
- Webhooks validan firma antes de procesar
- Refunds requieren aprobación manual (futuro)

---

### 7. AIConversation (Conversación IA)

**Definición:** Interacción con asistentes de inteligencia artificial

**Atributos principales:**
- `user_id` - Usuario que consulta (FK)
- `business_id` - Contexto del negocio (FK, nullable)
- `conversation_type` - Tipo de asistente
- `messages` - Historial JSON de mensajes
- `created_at` - Inicio de conversación

**Tipos de asistentes (conversation_type):**

1. **product_suggestion**
   - Sugiere productos según temporada, tendencias
   - Input: Tipo de negocio, ubicación
   - Output: Lista de productos recomendados

2. **sales_analysis**
   - Analiza ventas del business
   - Input: business_id, periodo
   - Output: Insights, gráficos, recomendaciones

3. **business_insights**
   - Consejos para mejorar operación
   - Input: Métricas del business
   - Output: Recomendaciones estratégicas

4. **general_query**
   - Asistente general
   - Input: Cualquier pregunta
   - Output: Respuesta contextual

**Estructura de messages:**
```json
[
  {"role": "user", "content": "¿Cuáles son mis productos más vendidos?"},
  {"role": "assistant", "content": "Tus top 3 productos son..."}
]
```

**Reglas:**
- Solo el owner del business puede consultar sobre su business
- Conversaciones se guardan para historial
- Costo de API OpenAI se trackea (futuro: billing)

---

## 👥 Roles y Permisos

### Matriz de Permisos

| Recurso | User (Cliente) | Business Owner | Admin |
|---------|----------------|----------------|-------|
| **Users** |
| Ver propio perfil | ✅ | ✅ | ✅ |
| Ver otros usuarios | ❌ | ❌ | ✅ |
| Editar propio perfil | ✅ | ✅ | ✅ |
| Eliminar usuarios | ❌ | ❌ | ✅ |
| Cambiar roles | ❌ | ❌ | ✅ |
| **Businesses** |
| Listar todos | ✅ (activos) | ✅ (propios + activos) | ✅ (todos) |
| Ver detalles | ✅ (activos) | ✅ (propios) | ✅ |
| Crear business | ❌ | ✅ | ✅ |
| Editar business | ❌ | ✅ (solo propios) | ✅ |
| Eliminar business | ❌ | ✅ (solo propios) | ✅ |
| **Products** |
| Listar productos | ✅ | ✅ | ✅ |
| Ver producto | ✅ | ✅ | ✅ |
| Crear producto | ❌ | ✅ (en su business) | ✅ |
| Editar producto | ❌ | ✅ (en su business) | ✅ |
| Eliminar producto | ❌ | ✅ (en su business) | ✅ |
| **Orders** |
| Listar propios | ✅ | ✅ | ✅ |
| Listar del business | ❌ | ✅ (solo su business) | ✅ |
| Crear order | ✅ | ✅ | ✅ |
| Ver order | ✅ (propios) | ✅ (de su business) | ✅ |
| Cambiar estado | ❌ | ✅ (de su business) | ✅ |
| Cancelar order | ✅ (propios) | ✅ (de su business) | ✅ |
| **Payments** |
| Ver propios | ✅ | ✅ | ✅ |
| Ver del business | ❌ | ✅ (solo su business) | ✅ |
| Procesar webhook | Sistema | Sistema | Sistema |
| Refund | ❌ | ❌ | ✅ |
| **Analytics** |
| Ver propias métricas | ❌ | ✅ (solo su business) | ✅ |
| Ver todas métricas | ❌ | ❌ | ✅ |
| **AI Assistants** |
| Consultar general | ✅ | ✅ | ✅ |
| Consultar business | ❌ | ✅ (solo su business) | ✅ |

### Asignación de Roles

**Cómo se asignan:**
- `user` - Rol por defecto al registrarse
- `business_owner` - Se asigna automáticamente al crear primer business
- `admin` - Solo asignable por otro admin (script create_admin.py)

**Cambio de roles:**
```python
# Solo admin puede cambiar roles
PUT /api/v1/users/{user_id}/role
Body: {"role": "business_owner"}
Auth: Admin JWT required
```

---

## 🔄 Flujos de Trabajo

### Flujo 1: Registro y Creación de Negocio

```
1. Usuario se registra
   POST /api/v1/auth/register
   Body: {email, password, full_name}
   → User creado con role="user"

2. Usuario login
   POST /api/v1/auth/login
   Body: {email, password}
   → Recibe JWT access_token

3. Usuario crea su cafetería
   POST /api/v1/businesses
   Headers: Authorization: Bearer {token}
   Body: {name, description, address, phone}
   → Business creado
   → User.role automáticamente cambia a "business_owner"

4. Dueño agrega productos
   POST /api/v1/products
   Body: {name, description, price, category, business_id}
   → Products creados y disponibles

5. Cafetería está lista para recibir pedidos
```

---

### Flujo 2: Cliente Realiza Pedido

```
1. Cliente busca cafeterías
   GET /api/v1/businesses
   → Lista de businesses activos

2. Cliente ve menú
   GET /api/v1/products?business_id={id}
   → Lista de productos disponibles

3. Cliente crea pedido
   POST /api/v1/orders
   Body: {
     business_id: "uuid",
     items: [
       {product_id: "uuid", quantity: 2},
       {product_id: "uuid", quantity: 1}
     ],
     notes: "Sin azúcar"
   }
   → Order creado con status="pending"
   → total_amount calculado automáticamente

4. Sistema crea payment
   → Payment creado con status="pending"
   → Genera link de pago MercadoPago

5. Cliente paga
   → Redirigido a MercadoPago
   → Completa pago

6. MercadoPago envía webhook
   POST /api/v1/payments/webhook
   → Valida firma HMAC
   → Actualiza Payment.status = "approved"
   → Actualiza Order.status = "confirmed"
   → Notifica al business owner (email/push - futuro)

7. Business owner ve pedido
   GET /api/v1/orders/business/{business_id}
   → Ve nuevo order confirmado

8. Business prepara pedido
   PUT /api/v1/orders/{id}/status
   Body: {status: "preparing"}
   → Order.status = "preparing"

9. Business marca listo
   PUT /api/v1/orders/{id}/status
   Body: {status: "ready"}
   → Order.status = "ready"
   → Notifica cliente (futuro)

10. Cliente retira/recibe
    PUT /api/v1/orders/{id}/status
    Body: {status: "delivered"}
    → Order.status = "delivered"
    → Flujo completo
```

---

### Flujo 3: Consulta IA para Análisis

```
1. Business owner solicita análisis
   POST /api/v1/ai/chat
   Body: {
     conversation_type: "sales_analysis",
     business_id: "uuid",
     message: "¿Cuáles son mis productos más vendidos este mes?"
   }

2. Sistema consulta OpenAI
   → Obtiene datos de ventas del business
   → Envía contexto + pregunta a GPT-4
   → Recibe análisis

3. Respuesta al owner
   Response: {
     conversation_id: "uuid",
     response: "Tus top 3 productos son: 1) Cappuccino (45 ventas)..."
   }
   → AIConversation guardada en BD

4. Owner puede continuar conversación
   POST /api/v1/ai/chat
   Body: {
     conversation_id: "uuid",
     message: "¿Cómo puedo aumentar ventas del producto #2?"
   }
   → Contexto mantenido
```

---

### Flujo 4: Admin Gestiona Plataforma

```
1. Admin login
   POST /api/v1/auth/login
   Body: {email: "admin@saas.test", password}
   → Recibe JWT con role="admin"

2. Admin lista todos los usuarios
   GET /api/v1/users
   → Ve todos los usuarios del sistema

3. Admin revisa business sospechoso
   GET /api/v1/businesses/{id}
   → Ve detalles completos

4. Admin suspende business
   PUT /api/v1/businesses/{id}
   Body: {is_active: false}
   → Business desactivado, no acepta más pedidos

5. Admin revisa pagos
   GET /api/v1/payments
   → Ve todos los payments del sistema

6. Admin crea nuevo admin
   python create_admin.py
   → Nuevo usuario con role="admin"
```

---

## ⚖️ Reglas de Negocio

### Reglas Generales

1. **Multi-tenancy estricto**
   - Un product solo pertenece a un business
   - Un order solo puede tener products de un business
   - No se permiten orders multi-business

2. **Consistencia de precios**
   - OrderItem.unit_price se copia de Product.price al crear
   - Si Product.price cambia después, orders antiguos mantienen precio original
   - Order.total_amount debe ser suma exacta de OrderItem.subtotal

3. **Validación de ownership**
   - Solo el owner puede modificar su business
   - Solo el owner puede cambiar estados de orders de su business
   - Users no pueden modificar businesses ajenos

### Reglas de Validación

**User:**
- Email único en el sistema
- Password mínimo 8 caracteres, 1 mayúscula, 1 número
- full_name no vacío

**Business:**
- Name único por owner (un owner no puede tener 2 businesses con mismo nombre)
- Phone formato válido
- Email formato válido

**Product:**
- Name no vacío
- Price > 0
- business_id debe existir y pertenecer al owner

**Order:**
- Debe tener al menos 1 OrderItem
- Todos los products deben pertenecer al mismo business
- total_amount > 0
- Solo se puede crear si Business.is_active = true

**OrderItem:**
- quantity > 0
- product_id debe existir y estar disponible
- unit_price debe coincidir con Product.price actual

**Payment:**
- amount debe coincidir con Order.total_amount
- transaction_id único (no duplicar pagos)

### Reglas de Estado

**Order Status Transitions:**
```
pending → confirmed ✅
pending → cancelled ✅
confirmed → preparing ✅
confirmed → cancelled ✅
preparing → ready ✅
preparing → cancelled ❌ (no permitido)
ready → delivered ✅
ready → cancelled ❌ (no permitido)
delivered → [final state] ❌
cancelled → [final state] ❌
```

**Payment Status Transitions:**
```
pending → approved ✅
pending → rejected ✅
approved → refunded ✅ (solo admin)
rejected → [final state] ❌
refunded → [final state] ❌
```

**Business is_active:**
- `true → false` - Business se desactiva, orders existentes se mantienen
- `false → true` - Business se reactiva, puede recibir nuevos orders

---

## 📊 Estados y Transiciones

### Diagrama de Estados: Order

```
    ┌─────────┐
    │ PENDING │ (recién creado, esperando pago)
    └────┬────┘
         │
         ├─────────────┐
         │             │
         v             v
   ┌──────────┐   ┌──────────┐
   │CONFIRMED │   │CANCELLED │ (cancelado antes de pago)
   └────┬─────┘   └──────────┘
        │
        ├─────────┐
        │         │
        v         v
   ┌──────────┐ ┌──────────┐
   │PREPARING │ │CANCELLED │ (cancelado después de pago - requiere refund)
   └────┬─────┘ └──────────┘
        │
        v
   ┌──────────┐
   │  READY   │ (listo para entregar)
   └────┬─────┘
        │
        v
   ┌──────────┐
   │DELIVERED │ (completado)
   └──────────┘
```

### Quién puede cambiar estados

| Transición | User | Business Owner | Admin |
|------------|------|----------------|-------|
| pending → confirmed | Sistema (webhook) | Sistema (webhook) | ✅ Manual |
| pending → cancelled | ✅ | ✅ | ✅ |
| confirmed → preparing | ❌ | ✅ | ✅ |
| confirmed → cancelled | ✅ (con refund) | ✅ (con refund) | ✅ |
| preparing → ready | ❌ | ✅ | ✅ |
| ready → delivered | ❌ | ✅ | ✅ |

---

## 🔌 Integraciones

### MercadoPago

**Propósito:** Procesamiento de pagos online

**Flujo de integración:**
1. Backend crea preferencia de pago
2. Frontend recibe init_point (link de pago)
3. Cliente redirigido a MercadoPago
4. Cliente completa pago
5. MercadoPago envía webhook a `/api/v1/payments/webhook`
6. Backend valida firma HMAC
7. Backend actualiza Payment y Order

**Seguridad:**
- Webhook signature validation con HMAC-SHA256
- Secret key almacenado en variable de entorno
- Rate limiting en endpoint de webhook

**Estados mapeados:**
```
MercadoPago "approved" → Payment.status = "approved" → Order.status = "confirmed"
MercadoPago "rejected" → Payment.status = "rejected" → Order.status = "cancelled"
MercadoPago "refunded" → Payment.status = "refunded" → Order.status = "cancelled"
```

---

### OpenAI GPT-4

**Propósito:** Asistentes inteligentes para análisis y recomendaciones

**Tipos de consultas:**

1. **Product Suggestion**
   - Entrada: Tipo negocio, ubicación, temporada
   - Salida: Lista de productos recomendados con razones
   - Modelo: GPT-4 con prompt especializado

2. **Sales Analysis**
   - Entrada: business_id, periodo (última semana/mes)
   - Proceso: Sistema consulta DB → envía datos a GPT-4
   - Salida: Análisis de tendencias, productos top, recomendaciones

3. **Business Insights**
   - Entrada: Métricas del business (ventas, clientes, horarios)
   - Salida: Consejos estratégicos para mejorar operación

4. **General Query**
   - Entrada: Cualquier pregunta sobre gestión de cafetería
   - Salida: Respuesta contextual

**Gestión de costos:**
- Límite de tokens por consulta
- Caché de respuestas frecuentes (futuro)
- Tracking de uso por business (futuro billing)

---

### Redis (Caching)

**Propósito:** Cache de datos frecuentemente consultados

**Datos cacheados:**
- Lista de businesses activos (TTL: 5 minutos)
- Productos por business (TTL: 10 minutos)
- Métricas de analytics (TTL: 1 hora)

**Estrategia:**
- Cache-aside pattern
- Invalidación al modificar datos
- Fallback a memoria si Redis no disponible

---

## 📈 Métricas y Analytics

### Métricas por Business

**Ventas:**
- Total revenue por periodo
- Número de orders
- Ticket promedio
- Productos más vendidos
- Horarios pico de ventas

**Clientes:**
- Clientes únicos
- Clientes recurrentes
- Tasa de retención

**Productos:**
- Products más vendidos
- Products menos vendidos
- Revenue por categoría

**Operación:**
- Tiempo promedio de preparación
- Tasa de cancelación
- Tasa de reembolsos

### Métricas Globales (Admin)

- Total businesses activos
- Total users registrados
- Total revenue plataforma
- Comisión cobrada (futuro)
- Uptime del sistema
- Response time promedio

---

## 🚀 Roadmap de Funcionalidades

### Fase 1: MVP (Completado ✅)
- ✅ Autenticación JWT + RBAC
- ✅ CRUD de Businesses
- ✅ CRUD de Products
- ✅ Sistema de Orders
- ✅ Integración MercadoPago
- ✅ Asistentes IA básicos

### Fase 2: Mejoras Operativas (En progreso)
- 🔄 Notificaciones push/email
- 🔄 Gestión de horarios por business
- 🔄 Sistema de reviews y ratings
- 🔄 Dashboard analytics avanzado

### Fase 3: Escalabilidad (Planeado)
- 📋 Multi-currency support
- 📋 Programa de lealtad
- 📋 Inventario automático
- 📋 Integración con delivery (Uber Eats, Rappi)

### Fase 4: Monetización (Futuro)
- 📋 Planes de subscripción (Free, Pro, Enterprise)
- 📋 Comisión por transacción
- 📋 Marketplace de productos
- 📋 API pública para integraciones

---

## 🔍 Preguntas Frecuentes

### ¿Un usuario puede tener múltiples businesses?
Sí, un business_owner puede crear y gestionar múltiples cafeterías desde una sola cuenta.

### ¿Se pueden compartir productos entre businesses?
No, cada product pertenece a un único business. Si dos cafeterías venden el mismo ítem, deben crear productos separados.

### ¿Qué pasa si se elimina un producto que tiene orders históricos?
Soft delete: Product.is_available = false. El producto no aparece en catálogo pero mantiene histórico en OrderItems.

### ¿Cómo se manejan los refunds?
Actualmente requieren intervención manual del admin. Futuro: Interfaz para business owners con aprobación automática.

### ¿Los precios incluyen impuestos?
Los precios son los finales que paga el cliente. Gestión de impuestos es responsabilidad del business owner (futuro: calculadora de impuestos).

### ¿Se pueden editar orders después de crearlos?
No. Una vez creado un order, solo se puede cambiar su estado, no su contenido. Para cambios, cancelar y crear nuevo order.

### ¿Cuánto tiempo se guardan las conversaciones con IA?
Indefinidamente por ahora. Futuro: Política de retención de 90 días para optimizar costos.

---

## 📞 Soporte

Para dudas sobre la lógica de negocio:
- Revisar código en `backend/app/db/models.py` (modelos SQLAlchemy)
- Revisar schemas en `backend/app/schemas.py` (validaciones Pydantic)
- Consultar API docs: http://localhost:8000/docs

---

**Última actualización:** Octubre 2025  
**Versión del documento:** 1.0  
**Mantenedor:** Equipo SaaS Cafeterías
