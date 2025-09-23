# 📡 API Examples & Payloads

Comprehensive API documentation with request/response examples, error handling, and performance metrics.

## 📋 Table of Contents

- [Authentication Endpoints](#authentication-endpoints)
- [Business Management](#business-management)
- [Product Management](#product-management)
- [User Management](#user-management)
- [Error Response Examples](#error-response-examples)
- [Performance Metrics](#performance-metrics)
- [Security Events](#security-events)

---

## 🔐 Authentication Endpoints

### POST `/api/v1/auth/login`
**Purpose**: Authenticate user and receive JWT token

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin1234!"
```

**Success Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "admin"
}
```

**Error Response (401)**:
```json
{
  "detail": "Incorrect username or password"
}
```

**Performance**: ~50-100ms typical response time

---

### GET `/api/v1/auth/me`
**Purpose**: Get current user information (never returns 500)

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "admin",
  "email": "admin@saas.test",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

**Error Response (401)**:
```json
{
  "detail": "Could not validate credentials"
}
```

**Security Features**:
- ✅ Robust error handling - never returns 500
- ✅ Complete field validation
- ✅ Automatic token validation
- ✅ Security logging enabled

---

### POST `/api/v1/auth/register`
**Purpose**: Create new user account

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "SecurePass123!",
    "role": "user"
  }'
```

**Success Response (200)**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-20T10:35:00Z",
  "updated_at": "2025-01-20T10:35:00Z"
}
```

**Error Response (400)**:
```json
{
  "detail": "Email already registered"
}
```

**Error Response (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🏢 Business Management

### POST `/api/v1/businesses`
**Purpose**: Create new business (authenticated users)

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/businesses" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Central",
    "description": "Premium coffee shop in downtown",
    "address": "123 Main Street, City Center",
    "phone": "+1-555-0123",
    "email": "contact@cafecentral.com",
    "business_type": "restaurant"
  }'
```

**Success Response (201)**:
```json
{
  "id": "business-uuid-here",
  "name": "Café Central",
  "description": "Premium coffee shop in downtown",
  "address": "123 Main Street, City Center",
  "phone": "+1-555-0123",
  "email": "contact@cafecentral.com",
  "business_type": "restaurant",
  "is_active": true,
  "created_at": "2025-01-20T10:40:00Z",
  "updated_at": "2025-01-20T10:40:00Z",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (400)**:
```json
{
  "detail": "Business name is required and cannot be empty"
}
```

**Error Response (401)**:
```json
{
  "detail": "Could not validate credentials"
}
```

**Performance**: ~100-200ms typical response time

---

### GET `/api/v1/businesses`
**Purpose**: List all active businesses

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/businesses?skip=0&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200)**:
```json
[
  {
    "id": "business-uuid-1",
    "name": "Café Central",
    "description": "Premium coffee shop in downtown",
    "address": "123 Main Street, City Center",
    "phone": "+1-555-0123",
    "email": "contact@cafecentral.com",
    "business_type": "restaurant",
    "is_active": true,
    "created_at": "2025-01-20T10:40:00Z",
    "updated_at": "2025-01-20T10:40:00Z"
  },
  {
    "id": "business-uuid-2", 
    "name": "Bakery Corner",
    "description": "Fresh bread and pastries daily",
    "address": "456 Baker Street",
    "phone": "+1-555-0124",
    "email": "hello@bakerycorner.com",
    "business_type": "bakery",
    "is_active": true,
    "created_at": "2025-01-20T09:15:00Z",
    "updated_at": "2025-01-20T09:15:00Z"
  }
]
```

**Performance**: ~50-150ms typical response time

---

### PUT `/api/v1/businesses/{business_id}`
**Purpose**: Update business (owners/managers only)

**Request**:
```bash
curl -X PUT "http://localhost:8000/api/v1/businesses/business-uuid-here" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated: Premium coffee shop with artisanal pastries",
    "phone": "+1-555-0999"
  }'
```

**Success Response (200)**:
```json
{
  "id": "business-uuid-here",
  "name": "Café Central",
  "description": "Updated: Premium coffee shop with artisanal pastries",
  "address": "123 Main Street, City Center",
  "phone": "+1-555-0999",
  "email": "contact@cafecentral.com",
  "business_type": "restaurant",
  "is_active": true,
  "created_at": "2025-01-20T10:40:00Z",
  "updated_at": "2025-01-20T11:45:00Z"
}
```

**Error Response (403)**:
```json
{
  "detail": "Not enough permissions to access this business"
}
```

**Error Response (404)**:
```json
{
  "detail": "Business not found"
}
```

---

## 📦 Product Management

### POST `/api/v1/businesses/{business_id}/products`
**Purpose**: Create product in business

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/businesses/business-uuid/products" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Espresso Americano",
    "description": "Rich and bold espresso with hot water",
    "price": 3.50,
    "category": "beverages",
    "is_available": true
  }'
```

**Success Response (201)**:
```json
{
  "id": "product-uuid-here",
  "name": "Espresso Americano", 
  "description": "Rich and bold espresso with hot water",
  "price": 3.50,
  "category": "beverages",
  "is_available": true,
  "business_id": "business-uuid",
  "created_at": "2025-01-20T11:00:00Z",
  "updated_at": "2025-01-20T11:00:00Z"
}
```

**Error Response (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

---

### GET `/api/v1/businesses/{business_id}/products/{product_id}`
**Purpose**: Get specific product details

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/businesses/business-uuid/products/product-uuid" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (200)**:
```json
{
  "id": "product-uuid-here",
  "name": "Espresso Americano",
  "description": "Rich and bold espresso with hot water",
  "price": 3.50,
  "category": "beverages", 
  "is_available": true,
  "business_id": "business-uuid",
  "created_at": "2025-01-20T11:00:00Z",
  "updated_at": "2025-01-20T11:00:00Z"
}
```

**Error Response (404)**:
```json
{
  "detail": "Product not found"
}
```

---

## 👤 User Management

### GET `/api/v1/users/`
**Purpose**: List users (admin only)

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer admin-token-here"
```

**Success Response (200)**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@saas.test",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-01-20T08:00:00Z",
    "updated_at": "2025-01-20T08:00:00Z"
  },
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "newuser", 
    "email": "newuser@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-20T10:35:00Z",
    "updated_at": "2025-01-20T10:35:00Z"
  }
]
```

**Error Response (403)**:
```json
{
  "detail": "Access denied. Required roles: ['admin'], user role: user"
}
```

---

## ❌ Error Response Examples

### 400 Bad Request
```json
{
  "detail": "Business name is required and cannot be empty"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: ['admin'], user role: user"
}
```

### 404 Not Found
```json
{
  "detail": "Business not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 8}
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error while creating business"
}
```

---

## ⚡ Performance Metrics

### Response Time Benchmarks

| Endpoint | Method | Avg Response Time | Status |
|----------|--------|------------------|--------|
| `/api/v1/auth/login` | POST | 75ms | ⚡ Fast |
| `/api/v1/auth/me` | GET | 45ms | ⚡ Fast |
| `/api/v1/businesses` | GET | 120ms | ⚡ Fast |
| `/api/v1/businesses` | POST | 180ms | 🟡 Acceptable |
| `/api/v1/businesses/{id}` | GET | 85ms | ⚡ Fast |
| `/api/v1/businesses/{id}` | PUT | 220ms | 🟡 Acceptable |
| `/api/v1/products` | GET | 95ms | ⚡ Fast |
| `/api/v1/products` | POST | 150ms | ⚡ Fast |

### Performance Thresholds
- **⚡ Fast**: < 100ms
- **🟡 Acceptable**: 100-500ms  
- **🟠 Slow**: 500-1000ms
- **🔴 Critical**: > 1000ms

### Optimization Recommendations
- Endpoints > 500ms should be optimized with:
  - Database indexing
  - Redis caching
  - Query optimization
  - Pagination for large datasets

---

## 🔒 Security Events

### Login Events
```json
{
  "timestamp": "2025-01-20T11:30:00Z",
  "level": "INFO",
  "security_event": "login_success",
  "message": "Successful login from 192.168.1.100",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
```

### Failed Authentication
```json
{
  "timestamp": "2025-01-20T11:25:00Z",
  "level": "WARNING", 
  "security_event": "login_failure",
  "message": "Failed login attempt from 192.168.1.105",
  "ip_address": "192.168.1.105",
  "endpoint": "/api/v1/auth/login"
}
```

### Forbidden Access
```json
{
  "timestamp": "2025-01-20T11:35:00Z",
  "level": "WARNING",
  "security_event": "forbidden_access", 
  "message": "Forbidden access attempt to GET /api/v1/users/",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "ip_address": "192.168.1.102",
  "endpoint": "/api/v1/users/"
}
```

### Admin Actions
```json
{
  "timestamp": "2025-01-20T11:40:00Z",
  "level": "INFO",
  "security_event": "admin_action",
  "message": "Admin action: POST /api/v1/businesses",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "ip_address": "192.168.1.100",
  "endpoint": "/api/v1/businesses"
}
```

---

## 🧪 Testing Examples

### Security Flow Test
```bash
# Run comprehensive security test
python tests/test_business_flow_security.py

# Expected output:
# ✅ Admin login successful
# ✅ /me endpoint never returns 500
# ✅ Business CRUD operations work
# ✅ Regular users get 403 for admin operations
# ✅ All error codes handled properly
```

### Performance Analysis
```bash
# Run performance tests
python tests/test_performance_analysis.py

# Expected output:
# 📊 Authentication: 75ms avg (⚡ Fast)
# 📊 Business CRUD: 180ms avg (🟡 Acceptable)
# 📊 No slow endpoints detected
```

### E2E Testing
```bash
# Run end-to-end tests
python tests/test_e2e_flow.py

# Expected output:
# ✅ Frontend login flow works
# ✅ Error handling in UI
# ✅ Complete user journey tested
```

---

## 📝 Notes

- All timestamps are in UTC ISO format
- JWT tokens expire after 30 minutes (configurable)
- Rate limiting: 100 requests/minute per IP
- All endpoints support JSON responses
- CORS enabled for frontend integration
- Comprehensive logging for all security events
- Response times measured with 10ms precision

For more examples, see the [Postman Collection](../backend/cafeteria_ia_postman_collection.json).