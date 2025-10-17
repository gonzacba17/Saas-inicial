# AI Integration - Sistema de Inteligencia Artificial

> **Documentación completa de la integración de IA en el SaaS**  
> **Última actualización:** Octubre 2025

---

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Arquitectura AI](#-arquitectura-ai)
- [Endpoints AI](#-endpoints-ai)
- [Características ML](#-características-ml)
- [Monitoreo y Auditoría](#-monitoreo-y-auditoría)
- [Workers Asíncronos](#-workers-asíncronos)
- [Integración con Vector Store](#-integración-con-vector-store)

---

## 🎯 Visión General

### ¿Qué incluye nuestra integración AI?

Sistema completo de inteligencia artificial que proporciona:
- **Asistente conversacional** para consultas de negocio
- **Análisis de ventas** automático con insights
- **Recomendaciones de productos** basadas en contexto
- **Búsqueda semántica** con ChromaDB
- **Procesamiento asíncrono** con Celery
- **Auditoría completa** de inferencias

### Tecnologías Utilizadas

- **OpenAI GPT-3.5-turbo**: Modelo de lenguaje principal
- **ChromaDB**: Base de datos vectorial para embeddings
- **Celery**: Cola de tareas asíncronas
- **PostgreSQL**: Almacenamiento de conversaciones y logs
- **Prometheus**: Métricas de inferencia

---

## 🏗️ Arquitectura AI

### Componentes Principales

```
┌─────────────────────────────────────────────────────┐
│                  Frontend (React)                   │
│              Chatbot + AI Features UI               │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────┐
│              Backend API (FastAPI)                  │
│  ┌─────────────────────────────────────────────┐   │
│  │  AI Endpoints (/api/v1/ai/*)               │   │
│  │  - /query, /recommend, /sales-analysis     │   │
│  └────────┬────────────────────────────────────┘   │
│           │                                         │
│  ┌────────▼─────────┐  ┌──────────────────────┐   │
│  │  ai_service.py   │  │  vector_store.py     │   │
│  │  (OpenAI API)    │  │  (ChromaDB)          │   │
│  └────────┬─────────┘  └──────────────────────┘   │
└───────────┼──────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────┐
│           Celery Workers (tasks_ai.py)           │
│  - generate_sales_report()                       │
│  - generate_product_recommendations()            │
│  - analyze_customer_behavior()                   │
└──────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────┐
│          PostgreSQL Database                     │
│  - ai_conversations                              │
│  - ai_audit_logs                                 │
└──────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Usuario hace consulta** → Frontend envía request a `/api/v1/ai/query`
2. **Backend procesa** → Valida permisos y extrae contexto del negocio
3. **Vector Store** → Busca documentos similares (embeddings)
4. **OpenAI API** → Genera respuesta contextualizada
5. **Auditoría** → Log en `ai_audit_logs` con métricas
6. **Response** → Guarda conversación y retorna al usuario

---

## 🔌 Endpoints AI

### 1. POST `/api/v1/ai/query`

Procesar consultas generales de IA.

**Request:**
```json
{
  "query": "¿Cuáles fueron las ventas del último mes?",
  "business_id": "uuid",
  "assistant_type": "SALES_ANALYSIS"
}
```

**Response:**
```json
{
  "response": "Análisis de ventas...",
  "assistant_type": "SALES_ANALYSIS",
  "conversation_id": "uuid",
  "tokens_used": 450,
  "response_time_ms": 1250
}
```

**Tipos de asistente:**
- `GENERAL_QUERY`: Consultas generales
- `SALES_ANALYSIS`: Análisis de ventas
- `PRODUCT_SUGGESTION`: Sugerencias de productos
- `CUSTOMER_INSIGHT`: Insights de clientes

---

### 2. POST `/api/v1/ai/recommend`

Generar recomendaciones de productos basadas en búsqueda semántica.

**Request:**
```bash
POST /api/v1/ai/recommend?business_id={uuid}&query_text=productos para retail&limit=5
```

**Response:**
```json
{
  "business_id": "uuid",
  "query": "productos para retail",
  "recommendations": "Basado en tu inventario, te recomiendo...",
  "similar_products": [
    {"id": "1", "name": "Café Espresso", "score": 0.95},
    {"id": "2", "name": "Café Americano", "score": 0.87}
  ],
  "conversation_id": "uuid",
  "response_time_ms": 890
}
```

**Características:**
- Búsqueda semántica con ChromaDB
- Context-aware recommendations
- Auditoría automática de inferencias
- Aislamiento multi-tenant

---

### 3. POST `/api/v1/ai/sales-analysis`

Análisis completo de ventas con insights automáticos.

**Request:**
```bash
POST /api/v1/ai/sales-analysis?business_id={uuid}&async_mode=true
```

**Response (modo async):**
```json
{
  "job_id": "celery-task-id",
  "status": "pending",
  "message": "Sales analysis is being generated. Use GET /api/v1/ai/jobs/{job_id} to check status."
}
```

**Response (modo sync):**
```json
{
  "business_id": "uuid",
  "analysis": {...},
  "insights": ["Ventas aumentaron 15%", "Producto X es el más vendido"],
  "recommendations": ["Incrementar stock de X", "Promoción en producto Y"],
  "conversation_id": "uuid"
}
```

---

### 4. POST `/api/v1/ai/product-suggestions`

Sugerencias de nuevos productos basadas en el tipo de negocio.

**Request:**
```bash
POST /api/v1/ai/product-suggestions?business_id={uuid}
```

**Response:**
```json
{
  "business_id": "uuid",
  "suggestions": [
    "Café helado de temporada",
    "Pastelería artesanal",
    "Bebidas veganas"
  ],
  "explanation": "Basado en tu tipo de negocio (cafetería)...",
  "conversation_id": "uuid"
}
```

---

### 5. GET `/api/v1/ai/jobs/{job_id}`

Verificar estado de trabajos asíncronos.

**Response:**
```json
{
  "job_id": "task-id",
  "status": "completed",
  "result": {
    "analysis": {...},
    "insights": [...],
    "timestamp": "2025-10-17T10:30:00Z"
  }
}
```

**Estados posibles:**
- `pending`: En cola
- `processing`: Ejecutándose
- `completed`: Finalizado exitosamente
- `failed`: Error durante ejecución

---

### 6. GET `/api/v1/ai/conversations`

Listar conversaciones AI del usuario.

**Query params:**
- `skip`: Offset (default: 0)
- `limit`: Límite (default: 100)
- `assistant_type`: Filtrar por tipo

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "business_id": "uuid",
    "assistant_type": "SALES_ANALYSIS",
    "prompt": "¿Cuáles fueron las ventas?",
    "response": "Análisis completo...",
    "tokens_used": 450,
    "response_time_ms": 1250,
    "created_at": "2025-10-17T10:00:00Z"
  }
]
```

---

### 7. GET `/api/v1/ai/usage-stats`

Estadísticas de uso de IA.

**Response:**
```json
{
  "total_conversations": 150,
  "total_tokens_used": 125000,
  "average_response_time_ms": 980,
  "conversations_by_type": {
    "GENERAL_QUERY": 50,
    "SALES_ANALYSIS": 60,
    "PRODUCT_SUGGESTION": 40
  },
  "total_cost_usd": 2.50
}
```

---

## 🧠 Características ML

### Estructura del Directorio `/ml/`

```
ml/
├── __init__.py
├── models/              # Modelos entrenados (futuro)
│   └── __init__.py
├── pipelines/           # Feature extraction
│   ├── __init__.py
│   └── extract_features.py
├── notebooks/           # Jupyter notebooks para análisis
│   └── __init__.py
├── serving/             # Model serving (futuro)
│   └── __init__.py
└── monitoring/          # Métricas de inferencia
    ├── __init__.py
    └── collect_ai_metrics.py
```

### Feature Extraction (`ml/pipelines/extract_features.py`)

Sistema de extracción de características para análisis ML.

**Funciones principales:**

```python
# Extraer features de órdenes
extract_order_features(order_data) -> Dict
# Returns: order_id, total_amount, item_count, avg_item_price, etc.

# Extraer features de clientes
extract_customer_features(customer_data, orders) -> Dict
# Returns: total_orders, total_spent, avg_order_value, etc.

# Extraer features de productos
extract_product_features(product_data, sales_data) -> Dict
# Returns: total_sold, revenue, stock_velocity, etc.

# Procesamiento batch
batch_extract_features(data_list, feature_extractor_fn) -> DataFrame
```

**Ejemplo de uso:**
```python
from ml.pipelines.extract_features import extract_order_features

order = {
    'id': 'uuid',
    'total': 45.50,
    'items': [{'category': 'coffee', 'price': 15.50}]
}

features = extract_order_features(order)
# {'order_id': 'uuid', 'total_amount': 45.50, 'item_count': 1, ...}
```

---

## 📊 Monitoreo y Auditoría

### Tabla `ai_audit_logs`

Registro completo de todas las inferencias AI.

**Campos:**
- `id`: UUID único
- `user_id`: Usuario que hizo la consulta
- `business_id`: Negocio asociado
- `model_name`: Modelo usado (ej: "gpt-3.5-turbo")
- `prompt`: Texto del prompt (max 5000 chars)
- `response`: Respuesta generada (max 10000 chars)
- `tokens_used`: Tokens consumidos
- `response_time_ms`: Tiempo de respuesta
- `endpoint`: Endpoint que generó la inferencia
- `status`: "success" | "error"
- `error_message`: Mensaje de error si aplica
- `timestamp`: Timestamp UTC

### Script de Métricas (`ml/monitoring/collect_ai_metrics.py`)

Recolecta y exporta métricas de inferencia AI.

**Uso:**
```python
from ml.monitoring import AIMetricsCollector

collector = AIMetricsCollector()

# Resumen general
summary = collector.get_metrics_summary()
# {
#   'total_requests': 150,
#   'success_rate': 98.5,
#   'avg_response_time_ms': 890,
#   'total_tokens': 125000
# }

# Por endpoint
by_endpoint = collector.get_metrics_by_endpoint()
# [{'endpoint': '/api/v1/ai/recommend', 'total_requests': 50, ...}]

# Por modelo
by_model = collector.get_metrics_by_model()

# Rate de errores
error_rate = collector.get_error_rate()

# Errores recientes
recent_errors = collector.get_recent_errors(limit=10)
```

**Exportar a Prometheus:**
```python
from ml.monitoring import export_metrics_to_prometheus_format

metrics = export_metrics_to_prometheus_format()
print(metrics)
# # HELP ai_requests_total Total AI requests
# # TYPE ai_requests_total counter
# ai_requests_total 150
# ...
```

**Ejecutar script:**
```bash
cd ml/monitoring
python collect_ai_metrics.py
```

---

## ⚙️ Workers Asíncronos

### Tareas Celery (`backend/app/workers/tasks_ai.py`)

**1. generate_sales_report**
```python
from app.workers.tasks_ai import generate_sales_report

task = generate_sales_report.delay(business_id="uuid", period="monthly")
result = task.get()  # Esperar resultado
```

**2. generate_product_recommendations**
```python
task = generate_product_recommendations.delay(
    business_id="uuid",
    business_type="cafeteria",
    business_name="Café Central"
)
```

**3. analyze_customer_behavior**
```python
task = analyze_customer_behavior.delay(
    business_id="uuid",
    customer_id="uuid"  # Optional
)
```

**4. generate_inventory_forecast**
```python
task = generate_inventory_forecast.delay(
    business_id="uuid",
    product_ids=["uuid1", "uuid2"]
)
```

**5. cleanup_old_ai_jobs**
```python
# Limpiar conversaciones antiguas (30 días)
task = cleanup_old_ai_jobs.delay(days_old=30)
```

### Configuración de Colas

En `backend/app/core/celery_app.py`:
```python
task_routes = {
    'app.workers.tasks_ai.*': {'queue': 'ai'},
    'app.tasks.notification_tasks.*': {'queue': 'notifications'},
}
```

**Iniciar workers:**
```bash
celery -A app.core.celery_app worker -Q ai --loglevel=info
```

---

## 🗄️ Integración con Vector Store

### ChromaDB para Embeddings

**Servicio:** `backend/app/services_directory/vector_store.py`

**Operaciones principales:**

```python
from app.services_directory.vector_store import vector_store

# Indexar documento
vector_store.add_document(
    business_id="uuid",
    document_id="product-1",
    content="Café Espresso Premium - 100% arábica",
    metadata={"category": "coffee", "price": 15.50}
)

# Búsqueda semántica
results = vector_store.similarity_search(
    query_text="café fuerte",
    business_id="uuid",
    limit=5
)
# Returns: [{'id': 'product-1', 'content': '...', 'score': 0.95}, ...]

# Eliminar documentos
vector_store.delete_document(business_id="uuid", document_id="product-1")
```

**Uso en recomendaciones:**
El endpoint `/api/v1/ai/recommend` utiliza búsqueda semántica para encontrar productos relevantes y luego genera recomendaciones contextualizadas con GPT-3.5.

---

## 🔐 Seguridad y Multi-tenancy

### Aislamiento de Datos

- **Vector Store**: Filtrado por `business_id` en todas las búsquedas
- **Auditoría**: Logs asociados a `user_id` y `business_id`
- **Permisos**: Validación de permisos antes de cada inferencia

### Auditoría de Inferencias

Función helper en `backend/app/utils/ai_audit.py`:

```python
from app.utils.ai_audit import log_ai_inference

log_ai_inference(
    user_id="uuid",
    business_id="uuid",
    model_name="gpt-3.5-turbo",
    prompt="Mi consulta...",
    response="Respuesta generada...",
    tokens_used=450,
    response_time_ms=890,
    endpoint="/api/v1/ai/recommend",
    status="success"
)
```

**Context Manager:**
```python
from app.utils.ai_audit import AIAuditContext

with AIAuditContext(user_id="uuid", business_id="uuid") as ctx:
    ctx.prompt = "Consulta..."
    # Procesar
    ctx.response = "Respuesta..."
    ctx.tokens_used = 450
    # Auditoría automática al salir
```

---

## 📈 Métricas de Rendimiento

### KPIs de IA

- **Throughput**: ~10-20 requests/segundo
- **Latencia promedio**: 800-1200ms (dependiendo del modelo)
- **Success rate**: >98%
- **Tokens por request**: ~400-600 tokens
- **Costo estimado**: $0.01-0.02 por request (GPT-3.5-turbo)

### Límites y Quotas

- **Rate limiting**: 100 requests/minuto por usuario
- **Timeout**: 30 segundos por inferencia
- **Max tokens**: 2000 tokens por respuesta
- **Retry policy**: 3 reintentos con backoff exponencial

---

## 🧪 Testing

### Tests Implementados

**File:** `backend/tests/test_ai_recommend.py`

```bash
pytest backend/tests/test_ai_recommend.py -v
```

**Casos de prueba:**
- ✅ Recomendación exitosa con autenticación
- ✅ Recomendación con query personalizada
- ✅ Rechazo sin autenticación (401)
- ✅ Negocio no encontrado (404)
- ✅ Sin permisos en negocio (403)

---

## 🚀 Próximos Pasos

### Funcionalidades Futuras

1. **Fine-tuning de modelos** específicos por tipo de negocio
2. **Análisis predictivo** de demanda con ML
3. **Chatbot multimodal** con imágenes de productos
4. **Sentiment analysis** de reviews de clientes
5. **A/B testing** de prompts para optimizar respuestas

### Mejoras de Infraestructura

- **Caching de embeddings** en Redis
- **Model serving** con TensorFlow Serving
- **Feature store** para ML features reutilizables
- **Distributed tracing** con OpenTelemetry

---

## 📚 Referencias

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html)
- [LangChain Integration Guide](https://python.langchain.com/docs/integrations/vectorstores/chroma)

---

**Última actualización:** Octubre 2025  
**Versión:** 1.0.0  
**Autor:** SaaS Cafeterías Team
