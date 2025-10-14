# 📅 SEMANA 2 - PLAN DE ACCIÓN COMPLETO
## Testing + Backups + Deploy Staging

**Fecha de inicio**: Semana del [TU_FECHA]  
**Objetivo**: Sistema production-ready con 85% coverage

---

## 🎯 OBJETIVOS DE LA SEMANA

- ✅ Elevar coverage de 65% → 85%+
- ✅ Crear 33 tests nuevos (18 unitarios + 5 integración + 10 smoke)
- ✅ Validar sistema de backups
- ✅ Deploy a staging environment
- ✅ Sistema production-ready

---

## 📆 DÍA 6 (LUNES) - TESTS DE ORDERS

### Objetivo
Crear tests completos para `app/api/v1/orders.py` y elevar coverage de 25% a 75%+

### Archivo a Crear: `tests/unit/api/v1/test_orders.py`

```python
"""
Tests unitarios para el módulo de órdenes
Coverage objetivo: 75%+
Total de tests: 10
"""

import pytest
from decimal import Decimal
from app.db.models.order import OrderStatus

class TestCreateOrder:
    """Tests para creación de órdenes"""
    
    def test_create_order_success(self, client, customer_token, sample_business, sample_product):
        """Test: Cliente puede crear una orden con productos válidos"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [
                {
                    "product_id": sample_product.id,
                    "quantity": 2
                }
            ],
            "notes": "Sin azúcar"
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["business_id"] == sample_business.id
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["status"] == "pending"
        assert data["notes"] == "Sin azúcar"
    
    def test_create_order_invalid_product_fails(self, client, customer_token, sample_business):
        """Test: Orden con producto inexistente falla"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": 99999, "quantity": 1}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        assert response.status_code == 404
    
    def test_create_order_out_of_stock_fails(self, client, customer_token, sample_business, db):
        """Test: Orden con producto sin stock falla"""
        from app.db.models.product import Product
        
        product = Product(
            name="Sin Stock",
            price=Decimal("100.00"),
            stock=0,
            business_id=sample_business.id
        )
        db.add(product)
        db.commit()
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": product.id, "quantity": 1}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        assert response.status_code == 400
        assert "stock" in response.json()["detail"].lower()
    
    def test_create_order_negative_quantity_fails(self, client, customer_token, sample_business, sample_product):
        """Test: Cantidad negativa es rechazada"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": -1}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        assert response.status_code == 422


class TestOrderStatusTransitions:
    """Tests para transiciones de estado de órdenes"""
    
    def test_order_status_pending_to_confirmed(self, client, owner_token, sample_order):
        """Test: Owner puede confirmar orden pendiente"""
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        response = client.patch(
            f"/api/v1/orders/{sample_order.id}/status",
            json={"status": "confirmed"},
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
    
    def test_order_status_confirmed_to_completed(self, client, owner_token, db, sample_order):
        """Test: Owner puede completar orden confirmada"""
        sample_order.status = OrderStatus.CONFIRMED
        db.commit()
        
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = client.patch(
            f"/api/v1/orders/{sample_order.id}/status",
            json={"status": "completed"},
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
    
    def test_order_status_invalid_transition_fails(self, client, owner_token, sample_order):
        """Test: Transición inválida (pending → completed) falla"""
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        response = client.patch(
            f"/api/v1/orders/{sample_order.id}/status",
            json={"status": "completed"},
            headers=headers
        )
        
        assert response.status_code == 400
        assert "invalid transition" in response.json()["detail"].lower()


class TestOrderCalculations:
    """Tests para cálculos de órdenes"""
    
    def test_calculate_order_total_single_item(self, client, customer_token, sample_business, sample_product):
        """Test: Total calculado correctamente para un item"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": 3}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        expected_total = sample_product.price * 3
        assert Decimal(str(data["total"])) == expected_total
    
    def test_calculate_order_total_multiple_items(self, client, customer_token, sample_business, db):
        """Test: Total calculado correctamente para múltiples items"""
        from app.db.models.product import Product
        
        product1 = Product(name="Producto 1", price=Decimal("100.00"), stock=50, business_id=sample_business.id)
        product2 = Product(name="Producto 2", price=Decimal("150.00"), stock=50, business_id=sample_business.id)
        db.add_all([product1, product2])
        db.commit()
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [
                {"product_id": product1.id, "quantity": 2},
                {"product_id": product2.id, "quantity": 1}
            ]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["total"])) == Decimal("350.00")


class TestCancelOrder:
    """Tests para cancelación de órdenes"""
    
    def test_cancel_pending_order_success(self, client, customer_token, sample_order):
        """Test: Cliente puede cancelar orden pendiente"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        
        response = client.delete(f"/api/v1/orders/{sample_order.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
    
    def test_cancel_completed_order_fails(self, client, customer_token, db, sample_order):
        """Test: No se puede cancelar orden completada"""
        sample_order.status = OrderStatus.COMPLETED
        db.commit()
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.delete(f"/api/v1/orders/{sample_order.id}", headers=headers)
        
        assert response.status_code == 400
        assert "cannot cancel" in response.json()["detail"].lower()
```

### Comandos para Ejecutar

```bash
# Ejecutar tests del día 6
pytest tests/unit/api/v1/test_orders.py -v

# Verificar coverage
pytest --cov=app.api.v1.orders tests/unit/api/v1/test_orders.py --cov-report=term

# Ejecutar todos los tests
pytest tests/unit/api/v1/ -v
```

### Entregables Día 6
- ✅ Archivo `test_orders.py` con 10 tests
- ✅ Coverage de `orders.py`: 25% → 75%
- ✅ Todos los tests pasando

---

## 📆 DÍA 7 (MARTES) - TESTS DE PAYMENTS

### Objetivo
Crear tests completos para `app/api/v1/payments.py` incluyendo mocking de MercadoPago

### Archivo a Crear: `tests/unit/api/v1/test_payments.py`

```python
"""
Tests unitarios para el módulo de pagos
Coverage objetivo: 70%+
Total de tests: 8
"""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

class TestCreatePayment:
    """Tests para creación de pagos"""
    
    @patch('app.services.payment_service.PaymentService.create_preference')
    def test_create_payment_mercadopago_success(self, mock_create, client, customer_token, sample_order):
        """Test: Creación de preferencia de pago exitosa"""
        mock_create.return_value = {
            "preference_id": "123456-abc-def",
            "init_point": "https://mercadopago.com/checkout/...",
            "sandbox_init_point": "https://sandbox.mercadopago.com/..."
        }
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post(
            f"/api/v1/payments/create-preference",
            json={
                "order_id": sample_order.id,
                "amount": float(sample_order.total)
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "preference_id" in data
        assert "init_point" in data
    
    def test_create_payment_invalid_amount_fails(self, client, customer_token, sample_order):
        """Test: Monto negativo es rechazado"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post(
            f"/api/v1/payments/create-preference",
            json={
                "order_id": sample_order.id,
                "amount": -100.0
            },
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_create_payment_nonexistent_order_fails(self, client, customer_token):
        """Test: Orden inexistente falla"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post(
            f"/api/v1/payments/create-preference",
            json={
                "order_id": 99999,
                "amount": 100.0
            },
            headers=headers
        )
        
        assert response.status_code == 404


class TestPaymentWebhook:
    """Tests para webhooks de MercadoPago"""
    
    @patch('app.services.payment_service.PaymentService.verify_payment')
    def test_webhook_approved_updates_order(self, mock_verify, client, db, sample_order):
        """Test: Webhook con pago aprobado actualiza orden"""
        from app.db.models.payment import PaymentStatus
        
        mock_verify.return_value = {
            "status": "approved",
            "payment_id": "123456789"
        }
        
        webhook_data = {
            "type": "payment",
            "data": {"id": "123456789"}
        }
        
        response = client.post("/api/v1/payments/webhook", json=webhook_data)
        
        assert response.status_code == 200
        db.refresh(sample_order)
        assert sample_order.payment_status == PaymentStatus.PAID
    
    @patch('app.services.payment_service.PaymentService.verify_payment')
    def test_webhook_rejected_updates_order(self, mock_verify, client, db, sample_order):
        """Test: Webhook con pago rechazado actualiza orden"""
        from app.db.models.payment import PaymentStatus
        
        mock_verify.return_value = {
            "status": "rejected",
            "payment_id": "123456789"
        }
        
        webhook_data = {
            "type": "payment",
            "data": {"id": "123456789"}
        }
        
        response = client.post("/api/v1/payments/webhook", json=webhook_data)
        
        assert response.status_code == 200
        db.refresh(sample_order)
        assert sample_order.payment_status == PaymentStatus.FAILED
    
    def test_webhook_invalid_signature_fails(self, client):
        """Test: Webhook con firma inválida es rechazado"""
        webhook_data = {
            "type": "payment",
            "data": {"id": "fake"}
        }
        
        response = client.post(
            "/api/v1/payments/webhook",
            json=webhook_data,
            headers={"X-Signature": "invalid_signature"}
        )
        
        assert response.status_code in [401, 403, 400]


class TestRefundPayment:
    """Tests para reembolsos"""
    
    @patch('app.services.payment_service.PaymentService.refund_payment')
    def test_refund_payment_success(self, mock_refund, client, owner_token, db, sample_order):
        """Test: Owner puede reembolsar pago"""
        from app.db.models.payment import Payment, PaymentStatus
        
        payment = Payment(
            order_id=sample_order.id,
            amount=sample_order.total,
            payment_method="mercadopago",
            payment_id="123456",
            status=PaymentStatus.PAID
        )
        db.add(payment)
        db.commit()
        
        mock_refund.return_value = {"status": "refunded"}
        
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = client.post(f"/api/v1/payments/{payment.id}/refund", headers=headers)
        
        assert response.status_code == 200
        db.refresh(payment)
        assert payment.status == PaymentStatus.REFUNDED
    
    def test_refund_already_refunded_fails(self, client, owner_token, db, sample_order):
        """Test: No se puede reembolsar dos veces"""
        from app.db.models.payment import Payment, PaymentStatus
        
        payment = Payment(
            order_id=sample_order.id,
            amount=sample_order.total,
            payment_method="mercadopago",
            payment_id="123456",
            status=PaymentStatus.REFUNDED
        )
        db.add(payment)
        db.commit()
        
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = client.post(f"/api/v1/payments/{payment.id}/refund", headers=headers)
        
        assert response.status_code == 400
        assert "already refunded" in response.json()["detail"].lower()
```

### Comandos para Ejecutar

```bash
# Ejecutar tests del día 7
pytest tests/unit/api/v1/test_payments.py -v

# Verificar coverage
pytest --cov=app.api.v1.payments tests/unit/api/v1/test_payments.py --cov-report=term

# Coverage total hasta ahora
pytest --cov=app.api.v1 tests/unit/api/v1/ --cov-report=html
```

### Entregables Día 7
- ✅ Archivo `test_payments.py` con 8 tests
- ✅ Mocking de MercadoPago funcionando
- ✅ Coverage de `payments.py`: 25% → 70%

---

## 📆 DÍA 8 (MIÉRCOLES) - TESTS DE INTEGRACIÓN

### Objetivo
Crear tests de integración que validen flujos completos del sistema

### Archivo a Crear: `tests/integration/test_complete_flows.py`

```python
"""
Tests de integración para flujos completos del sistema
Valida interacciones entre múltiples componentes
Total de tests: 5
"""

import pytest
from decimal import Decimal
from unittest.mock import patch

class TestCompleteUserJourney:
    """Test del journey completo de un usuario"""
    
    def test_complete_user_flow(self, client, db):
        """
        Test: Usuario completo desde registro hasta compra
        
        Flujo:
        1. Registro de usuario
        2. Login
        3. Ver negocios disponibles
        4. Ver productos de un negocio
        5. Crear orden
        6. Simular pago
        7. Verificar orden pagada
        """
        # 1. Registro
        register_data = {
            "email": "customer@test.com",
            "password": "Test1234!",
            "full_name": "Test Customer"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # 2. Login
        login_data = {
            "username": "customer@test.com",
            "password": "Test1234!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Ver negocios
        response = client.get("/api/v1/businesses", headers=headers)
        assert response.status_code == 200
        businesses = response.json()
        assert len(businesses) > 0
        business_id = businesses[0]["id"]
        
        # 4. Ver productos
        response = client.get(f"/api/v1/businesses/{business_id}/products", headers=headers)
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        product_id = products[0]["id"]
        
        # 5. Crear orden
        order_data = {
            "business_id": business_id,
            "items": [{"product_id": product_id, "quantity": 2}]
        }
        response = client.post("/api/v1/orders", json=order_data, headers=headers)
        assert response.status_code == 201
        order = response.json()
        order_id = order["id"]
        assert order["status"] == "pending"
        
        # 6. Crear preferencia de pago (mock)
        with patch('app.services.payment_service.PaymentService.create_preference') as mock:
            mock.return_value = {
                "preference_id": "test-123",
                "init_point": "https://test.com"
            }
            
            payment_data = {
                "order_id": order_id,
                "amount": float(order["total"])
            }
            response = client.post(
                "/api/v1/payments/create-preference",
                json=payment_data,
                headers=headers
            )
            assert response.status_code == 200
        
        # 7. Simular webhook de pago aprobado
        with patch('app.services.payment_service.PaymentService.verify_payment') as mock:
            mock.return_value = {"status": "approved", "payment_id": "123"}
            
            webhook_data = {
                "type": "payment",
                "data": {"id": "123"}
            }
            response = client.post("/api/v1/payments/webhook", json=webhook_data)
            assert response.status_code == 200
        
        # 8. Verificar que orden está pagada
        response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        order_updated = response.json()
        assert order_updated["payment_status"] == "paid"


class TestBusinessOwnerFlow:
    """Test del flujo de un business owner"""
    
    def test_business_owner_complete_flow(self, client, db):
        """
        Test: Owner gestiona su negocio completo
        
        Flujo:
        1. Registro como owner
        2. Login
        3. Crear negocio
        4. Agregar productos
        5. Recibir orden de cliente
        6. Confirmar orden
        7. Completar orden
        """
        # 1-2. Registro y login de owner
        register_data = {
            "email": "owner@test.com",
            "password": "Owner1234!",
            "full_name": "Business Owner",
            "role": "owner"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        login_data = {
            "username": "owner@test.com",
            "password": "Owner1234!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Crear negocio
        business_data = {
            "name": "Mi Cafetería",
            "description": "La mejor del barrio",
            "address": "Calle 123"
        }
        response = client.post("/api/v1/businesses", json=business_data, headers=headers)
        assert response.status_code == 201
        business_id = response.json()["id"]
        
        # 4. Agregar productos
        product_data = {
            "name": "Café Americano",
            "description": "Café negro",
            "price": 350.00,
            "stock": 100
        }
        response = client.post(
            f"/api/v1/businesses/{business_id}/products",
            json=product_data,
            headers=headers
        )
        assert response.status_code == 201
        product_id = response.json()["id"]
        
        # 5. Simular orden de cliente
        from app.db.models.user import User
        from app.db.models.order import Order, OrderItem
        
        customer = User(
            email="customer2@test.com",
            hashed_password="hash",
            role="customer"
        )
        db.add(customer)
        db.commit()
        
        order = Order(
            user_id=customer.id,
            business_id=business_id,
            total=Decimal("700.00"),
            status="pending"
        )
        db.add(order)
        db.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=2,
            unit_price=Decimal("350.00"),
            subtotal=Decimal("700.00")
        )
        db.add(order_item)
        db.commit()
        
        # 6. Owner confirma orden
        response = client.patch(
            f"/api/v1/orders/{order.id}/status",
            json={"status": "confirmed"},
            headers=headers
        )
        assert response.status_code == 200
        
        # 7. Owner completa orden
        response = client.patch(
            f"/api/v1/orders/{order.id}/status",
            json={"status": "completed"},
            headers=headers
        )
        assert response.status_code == 200


class TestAdminPermissionsFlow:
    """Test de permisos de administrador"""
    
    def test_admin_can_manage_all_businesses(self, client, admin_token, db):
        """Test: Admin puede gestionar cualquier negocio"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Crear negocio de otro usuario
        from app.db.models.user import User
        from app.db.models.business import Business
        
        owner = User(
            email="owner2@test.com",
            hashed_password="hash",
            role="owner"
        )
        db.add(owner)
        db.commit()
        
        business = Business(
            name="Negocio Ajeno",
            owner_id=owner.id
        )
        db.add(business)
        db.commit()
        
        # Admin puede ver
        response = client.get(f"/api/v1/businesses/{business.id}", headers=headers)
        assert response.status_code == 200
        
        # Admin puede editar
        response = client.put(
            f"/api/v1/businesses/{business.id}",
            json={"name": "Editado por Admin"},
            headers=headers
        )
        assert response.status_code == 200
        
        # Admin puede eliminar
        response = client.delete(f"/api/v1/businesses/{business.id}", headers=headers)
        assert response.status_code == 204


class TestConcurrentOrders:
    """Test de concurrencia en creación de órdenes"""
    
    def test_concurrent_order_creation(self, client, customer_token, sample_business, sample_product, db):
        """Test: Múltiples órdenes simultáneas no causan problemas"""
        import concurrent.futures
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        order_data = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": 1}]
        }
        
        # Crear 10 órdenes concurrentemente
        def create_order():
            return client.post("/api/v1/orders", json=order_data, headers=headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_order) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # Verificar que todas las órdenes se crearon exitosamente
        success_count = sum(1 for r in results if r.status_code == 201)
        assert success_count == 10
        
        # Verificar que el stock se redujo correctamente
        db.refresh(sample_product)
        assert sample_product.stock >= 0


class TestPaymentFlow:
    """Test de flujo completo de pago"""
    
    def test_payment_flow_with_webhook(self, client, customer_token, sample_business, sample_product, db):
        """Test: Flujo completo desde orden hasta pago confirmado"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        
        # 1. Crear orden
        order_data = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": 1}]
        }
        response = client.post("/api/v1/orders", json=order_data, headers=headers)
        assert response.status_code == 201
        order_id = response.json()["id"]
        
        # 2. Crear preferencia de pago
        with patch('app.services.payment_service.PaymentService.create_preference') as mock:
            mock.return_value = {
                "preference_id": "pref-123",
                "init_point": "https://mp.com/checkout/pref-123"
            }
            
            response = client.post(
                "/api/v1/payments/create-preference",
                json={"order_id": order_id, "amount": 350.0},
                headers=headers
            )
            assert response.status_code == 200
            preference_id = response.json()["preference_id"]
        
        # 3. Simular pago en MercadoPago (webhook)
        with patch('app.services.payment_service.PaymentService.verify_payment') as mock:
            mock.return_value = {
                "status": "approved",
                "payment_id": "pay-456",
                "preference_id": preference_id
            }
            
            webhook_data = {
                "type": "payment",
                "data": {"id": "pay-456"}
            }
            response = client.post("/api/v1/payments/webhook", json=webhook_data)
            assert response.status_code == 200
        
        # 4. Verificar orden actualizada
        response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        order = response.json()
        assert order["payment_status"] == "paid"
```

### Comandos para Ejecutar

```bash
# Ejecutar tests de integración
pytest tests/integration/test_complete_flows.py -v

# Coverage total
pytest --cov=app --cov-report=html tests/

# Ver reporte HTML
python -m http.server 8080 -d htmlcov/
```

### Entregables Día 8
- ✅ 5 tests de integración E2E
- ✅ Flujos críticos validados
- ✅ Coverage total del sistema: 85%+

---

## 📆 DÍA 9 (JUEVES) - SISTEMA DE BACKUPS

### Objetivo
Crear sistema completo de backups automatizado con validación

### Archivo 1: `scripts/backup.sh`

```bash
#!/bin/bash
# scripts/backup.sh
# Script completo de backup con validación

set -e  # Salir si hay error
set -u  # Error si variable no definida

# ============================================
# CONFIGURACIÓN
# ============================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)
BACKUP_DIR="${BACKUP_DIR:-/backups}"
S3_BUCKET="${S3_BUCKET
S3_BUCKET="${S3_BUCKET:-saas-cafeterias-backups}"
RETENTION_DAYS=7
LOG_FILE="/var/log/backup.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================
# FUNCIONES
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Verificando prerrequisitos..."
    
    if [ -z "${DATABASE_URL:-}" ]; then
        error "DATABASE_URL no está configurado"
    fi
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log "Creando directorio de backup: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
    
    command -v pg_dump >/dev/null 2>&1 || error "pg_dump no está instalado"
    command -v gzip >/dev/null 2>&1 || error "gzip no está instalado"
    
    if [ -n "${S3_BUCKET:-}" ]; then
        command -v aws >/dev/null 2>&1 || warning "AWS CLI no disponible, backups solo locales"
    fi
    
    success "Prerrequisitos verificados"
}

backup_database() {
    log "Iniciando backup de base de datos..."
    
    local db_file="$BACKUP_DIR/db_${TIMESTAMP}.sql"
    local db_file_gz="${db_file}.gz"
    
    if pg_dump "$DATABASE_URL" > "$db_file"; then
        success "Dump de base de datos creado: $db_file"
    else
        error "Falló el dump de base de datos"
    fi
    
    if gzip "$db_file"; then
        success "Base de datos comprimida: $db_file_gz"
        echo "$db_file_gz"
    else
        error "Falló la compresión"
    fi
}

backup_files() {
    log "Iniciando backup de archivos estáticos..."
    
    local files_dir="${FILES_DIR:-/app/uploads}"
    local files_file="$BACKUP_DIR/files_${TIMESTAMP}.tar.gz"
    
    if [ ! -d "$files_dir" ]; then
        warning "Directorio de archivos no existe: $files_dir"
        return 0
    fi
    
    if tar -czf "$files_file" -C "$(dirname "$files_dir")" "$(basename "$files_dir")"; then
        success "Archivos comprimidos: $files_file"
        echo "$files_file"
    else
        error "Falló el backup de archivos"
    fi
}

upload_to_s3() {
    local file=$1
    
    if [ -z "${S3_BUCKET:-}" ]; then
        warning "S3_BUCKET no configurado, saltando upload"
        return 0
    fi
    
    if ! command -v aws >/dev/null 2>&1; then
        warning "AWS CLI no disponible, saltando upload"
        return 0
    fi
    
    log "Subiendo a S3: $file"
    
    local s3_path="s3://${S3_BUCKET}/${DATE_ONLY}/$(basename "$file")"
    
    if aws s3 cp "$file" "$s3_path"; then
        success "Subido a S3: $s3_path"
    else
        error "Falló el upload a S3"
    fi
}

verify_backup() {
    local file=$1
    
    log "Verificando integridad del backup: $file"
    
    if [ ! -f "$file" ]; then
        error "Archivo de backup no existe: $file"
    fi
    
    if [ ! -s "$file" ]; then
        error "Archivo de backup está vacío: $file"
    fi
    
    if [[ "$file" == *.gz ]]; then
        if gzip -t "$file" 2>/dev/null; then
            success "Compresión válida: $file"
        else
            error "Archivo comprimido corrupto: $file"
        fi
    fi
    
    local size=$(du -h "$file" | cut -f1)
    log "Tamaño del backup: $size"
}

cleanup_old_backups() {
    log "Limpiando backups antiguos (> $RETENTION_DAYS días)..."
    
    local count_before=$(find "$BACKUP_DIR" -type f | wc -l)
    
    find "$BACKUP_DIR" -type f -mtime "+$RETENTION_DAYS" -delete
    
    local count_after=$(find "$BACKUP_DIR" -type f | wc -l)
    local deleted=$((count_before - count_after))
    
    if [ $deleted -gt 0 ]; then
        log "Eliminados $deleted backups antiguos"
    else
        log "No hay backups antiguos para eliminar"
    fi
}

send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"Backup ${status}: ${message}\"}" \
            2>/dev/null || true
    fi
    
    if [ -n "${NOTIFY_EMAIL:-}" ]; then
        echo "$message" | mail -s "Backup ${status}" "$NOTIFY_EMAIL" 2>/dev/null || true
    fi
}

# ============================================
# MAIN
# ============================================

main() {
    log "========================================="
    log "Iniciando proceso de backup"
    log "Timestamp: $TIMESTAMP"
    log "========================================="
    
    check_prerequisites
    
    db_backup=$(backup_database)
    verify_backup "$db_backup"
    upload_to_s3 "$db_backup"
    
    files_backup=$(backup_files)
    if [ -n "$files_backup" ]; then
        verify_backup "$files_backup"
        upload_to_s3 "$files_backup"
    fi
    
    cleanup_old_backups
    
    success "========================================="
    success "Backup completado exitosamente"
    success "Database: $db_backup"
    success "Files: ${files_backup:-N/A}"
    success "========================================="
    
    send_notification "SUCCESS" "Backup completado: $TIMESTAMP"
}

trap 'error "Backup falló en línea $LINENO"; send_notification "FAILED" "Error en línea $LINENO"' ERR

main "$@"
```

### Archivo 2: `scripts/restore.sh`

```bash
#!/bin/bash
# scripts/restore.sh
# Script de restauración desde backup

set -e
set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_usage() {
    cat << EOF
Uso: $0 <backup_file> [OPTIONS]

Restaura la base de datos desde un archivo de backup.

Opciones:
  -h, --help              Mostrar esta ayuda
  -f, --force             No pedir confirmación
  --db-only               Solo restaurar base de datos
  --files-only            Solo restaurar archivos
  --from-s3 <path>        Descargar desde S3

Ejemplos:
  $0 /backups/db_20241013_140000.sql.gz
  $0 --from-s3 s3://bucket/db_20241013_140000.sql.gz
  $0 /backups/db_latest.sql.gz --force
EOF
}

confirm_restore() {
    if [ "${FORCE:-false}" = "true" ]; then
        return 0
    fi
    
    warning "⚠️  ADVERTENCIA: Esta operación sobrescribirá la base de datos actual"
    read -p "¿Estás seguro de continuar? (escribir 'yes' para confirmar): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        log "Restauración cancelada por el usuario"
        exit 0
    fi
}

download_from_s3() {
    local s3_path=$1
    local local_file="/tmp/$(basename "$s3_path")"
    
    log "Descargando desde S3: $s3_path"
    
    if aws s3 cp "$s3_path" "$local_file"; then
        success "Descargado: $local_file"
        echo "$local_file"
    else
        error "Falló la descarga desde S3"
    fi
}

restore_database() {
    local backup_file=$1
    
    log "Iniciando restauración de base de datos..."
    log "Archivo: $backup_file"
    
    if [ ! -f "$backup_file" ]; then
        error "Archivo no encontrado: $backup_file"
    fi
    
    local sql_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        log "Descomprimiendo archivo..."
        sql_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$sql_file"
    fi
    
    log "Creando backup de seguridad de DB actual..."
    local safety_backup="/tmp/safety_backup_$(date +%Y%m%d_%H%M%S).sql"
    pg_dump "$DATABASE_URL" > "$safety_backup" || warning "No se pudo crear backup de seguridad"
    
    log "Cerrando conexiones activas..."
    psql "$DATABASE_URL" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();" || true
    
    log "Eliminando base de datos actual..."
    local db_name=$(echo "$DATABASE_URL" | sed 's/.*\///')
    dropdb --if-exists "$db_name" || error "No se pudo eliminar la base de datos"
    
    log "Creando base de datos limpia..."
    createdb "$db_name" || error "No se pudo crear la base de datos"
    
    log "Restaurando desde backup..."
    if psql "$DATABASE_URL" < "$sql_file"; then
        success "Base de datos restaurada exitosamente"
    else
        error "Falló la restauración. Restaurando desde safety backup..."
        createdb "$db_name"
        psql "$DATABASE_URL" < "$safety_backup"
        error "Restauración falló pero DB fue recuperada desde safety backup"
    fi
    
    rm -f "$sql_file" "$safety_backup"
}

restore_files() {
    local backup_file=$1
    local files_dir="${FILES_DIR:-/app/uploads}"
    
    log "Iniciando restauración de archivos..."
    log "Archivo: $backup_file"
    log "Destino: $files_dir"
    
    if [ ! -f "$backup_file" ]; then
        error "Archivo no encontrado: $backup_file"
    fi
    
    if [ -d "$files_dir" ]; then
        log "Creando backup de archivos actuales..."
        local safety_backup="/tmp/files_safety_$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf "$safety_backup" -C "$(dirname "$files_dir")" "$(basename "$files_dir")"
    fi
    
    log "Eliminando archivos actuales..."
    rm -rf "$files_dir"
    
    log "Restaurando archivos desde backup..."
    if tar -xzf "$backup_file" -C "$(dirname "$files_dir")"; then
        success "Archivos restaurados exitosamente"
    else
        error "Falló la restauración de archivos"
    fi
}

verify_restoration() {
    log "Verificando restauración..."
    
    if psql "$DATABASE_URL" -c "SELECT 1;" >/dev/null 2>&1; then
        success "Conexión a base de datos: OK"
    else
        error "No se puede conectar a la base de datos"
    fi
    
    log "Conteo de registros:"
    psql "$DATABASE_URL" -c "SELECT 'users' as table, COUNT(*) FROM users UNION ALL SELECT 'businesses', COUNT(*) FROM businesses UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'orders', COUNT(*) FROM orders;"
}

main() {
    local backup_file=""
    local from_s3=""
    local db_only=false
    local files_only=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            --db-only)
                db_only=true
                shift
                ;;
            --files-only)
                files_only=true
                shift
                ;;
            --from-s3)
                from_s3=$2
                shift 2
                ;;
            *)
                backup_file=$1
                shift
                ;;
        esac
    done
    
    if [ -n "$from_s3" ]; then
        backup_file=$(download_from_s3 "$from_s3")
    fi
    
    if [ -z "$backup_file" ]; then
        error "Debe especificar un archivo de backup"
    fi
    
    confirm_restore
    
    log "========================================="
    log "Iniciando restauración"
    log "Archivo: $backup_file"
    log "========================================="
    
    if [ "$files_only" = "false" ]; then
        restore_database "$backup_file"
        verify_restoration
    fi
    
    if [ "$db_only" = "false" ] && [[ "$backup_file" == *"files"* ]]; then
        restore_files "$backup_file"
    fi
    
    success "========================================="
    success "Restauración completada exitosamente"
    success "========================================="
}

trap 'error "Restauración falló en línea $LINENO"' ERR

main "$@"
```

### Archivo 3: `scripts/check_backup_status.sh`

```bash
#!/bin/bash
# scripts/check_backup_status.sh
# Verifica que los backups estén funcionando

BACKUP_DIR="/backups"
MAX_AGE_HOURS=24
ALERT_EMAIL="${NOTIFY_EMAIL:-admin@example.com}"

latest_backup=$(find "$BACKUP_DIR" -name "db_*.sql.gz" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2)

if [ -z "$latest_backup" ]; then
    echo "⚠️  ALERTA: No se encontraron backups"
    echo "No hay backups en $BACKUP_DIR" | mail -s "ALERTA: Sin backups" "$ALERT_EMAIL"
    exit 1
fi

backup_age=$(find "$latest_backup" -mmin +$((MAX_AGE_HOURS * 60)))

if [ -n "$backup_age" ]; then
    echo "⚠️  ALERTA: Último backup es muy antiguo"
    echo "Último backup: $latest_backup (más de $MAX_AGE_HOURS horas)" | mail -s "ALERTA: Backup antiguo" "$ALERT_EMAIL"
    exit 1
fi

echo "✅ Backups OK - Último: $latest_backup"
```

### Configurar Cronjobs

```bash
# Editar crontab
# crontab -e

# Backup diario a las 2 AM
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1

# Backup semanal completo (domingos a las 3 AM)
0 3 * * 0 /app/scripts/backup_full.sh >> /var/log/backup.log 2>&1

# Verificar último backup cada hora
0 * * * * /app/scripts/check_backup_status.sh >> /var/log/backup_check.log 2>&1
```

### Comandos para Ejecutar

```bash
# Dar permisos de ejecución
chmod +x scripts/backup.sh
chmod +x scripts/restore.sh
chmod +x scripts/check_backup_status.sh

# Probar backup
./scripts/backup.sh

# Verificar que se creó
ls -lh /backups/

# Probar restauración (CUIDADO: borra DB)
./scripts/restore.sh /backups/db_TIMESTAMP.sql.gz --force
```

### Entregables Día 9
- ✅ Script `backup.sh` completo (200+ líneas)
- ✅ Script `restore.sh` completo (150+ líneas)
- ✅ Script de monitoreo
- ✅ Cronjobs configurados
- ✅ Sistema de backups automatizado

---

## 📆 DÍA 10 (VIERNES) - DEPLOY STAGING

### Objetivo
Validar backups, configurar staging y hacer deploy

### Archivo 1: `docker-compose.staging.yml`

```yaml
version: '3.9'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    image: saas-backend:staging
    container_name: saas-backend-staging
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://staging_user:${DB_PASSWORD}@db:5432/saas_staging
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=false
      - ALLOWED_ORIGINS=https://staging.domain.com
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - saas-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    image: saas-frontend:staging
    container_name: saas-frontend-staging
    environment:
      - VITE_API_URL=https://staging-api.domain.com
      - VITE_ENVIRONMENT=staging
    ports:
      - "8080:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - saas-network

  db:
    image: postgres:15-alpine
    container_name: saas-db-staging
    environment:
      - POSTGRES_DB=saas_staging
      - POSTGRES_USER=staging_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - staging_db_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U staging_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - saas-network

  redis:
    image: redis:7-alpine
    container_name: saas-redis-staging
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - staging_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - saas-network

  prometheus:
    image: prom/prometheus:latest
    container_name: saas-prometheus-staging
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - staging_prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    networks:
      - saas-network

  grafana:
    image: grafana/grafana:latest
    container_name: saas-grafana-staging
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - staging_grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - saas-network

volumes:
  staging_db_data:
  staging_redis_data:
  staging_prometheus_data:
  staging_grafana_data:

networks:
  saas-network:
    driver: bridge
```

### Archivo 2: `scripts/deploy_staging.sh`

```bash
#!/bin/bash
# scripts/deploy_staging.sh
# Deploy automatizado a staging

set -e

echo "🚀 Deploying to staging..."

# Variables
ENVIRONMENT="staging"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# 1. Verificar variables de entorno
log "Verificando variables de entorno..."
if [ -z "${DB_PASSWORD:-}" ]; then
    error "DB_PASSWORD no configurado"
fi
if [ -z "${SECRET_KEY:-}" ]; then
    error "SECRET_KEY no configurado"
fi
success "Variables de entorno OK"

# 2. Pull latest code
log "Pulling latest code from staging branch..."
git fetch origin
git checkout staging
git pull origin staging
success "Code updated"

# 3. Build images
log "Building Docker images..."
docker-compose -f docker-compose.staging.yml build --no-cache
success "Images built"

# 4. Stop current containers
log "Stopping current containers..."
docker-compose -f docker-compose.staging.yml down
success "Containers stopped"

# 5. Start database first
log "Starting database..."
docker-compose -f docker-compose.staging.yml up -d db redis
sleep 10
success "Database started"

# 6. Run migrations
log "Running database migrations..."
docker-compose -f docker-compose.staging.yml run --rm backend alembic upgrade head
success "Migrations completed"

# 7. Start all services
log "Starting all services..."
docker-compose -f docker-compose.staging.yml up -d
success "Services started"

# 8. Wait for health checks
log "Waiting for services to be healthy..."
sleep 15

# 9. Health check
log "Performing health check..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        success "Health check passed"
        break
    fi
    if [ $i -eq 5 ]; then
        error "Health check failed after 5 attempts"
    fi
    sleep 5
done

# 10. Run smoke tests
log "Running smoke tests..."
if [ -f "tests/smoke/test_staging_smoke.py" ]; then
    docker-compose -f docker-compose.staging.yml run --rm backend pytest tests/smoke/ -v
    success "Smoke tests passed"
fi

# 11. Show services status
log "Services status:"
docker-compose -f docker-compose.staging.yml ps

success "========================================="
success "Deploy to staging completed!"
success "Timestamp: $TIMESTAMP"
success "Backend: http://localhost:8000"
success "Frontend: http://localhost:8080"
success "Grafana: http://localhost:3000"
success "========================================="
```

### Archivo 3: `tests/smoke/test_staging_smoke.py`

```python
"""
Smoke tests para validar deployment en staging
Estos tests validan que los servicios básicos funcionen
"""

import requests
import pytest

STAGING_API_URL = "http://localhost:8000"
STAGING_FRONTEND_URL = "http://localhost:8080"

class TestStagingAPI:
    """Smoke tests para API en staging"""
    
    def test_health_endpoint(self):
        """Test: Health endpoint responde"""
        response = requests.get(f"{STAGING_API_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]
    
    def test_docs_available(self):
        """Test: Documentación API disponible"""
        response = requests.get(f"{STAGING_API_URL}/docs", timeout=5)
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_cors_headers(self):
        """Test: CORS configurado correctamente"""
        response = requests.options(
            f"{STAGING_API_URL}/api/v1/businesses",
            headers={"Origin": STAGING_FRONTEND_URL},
            timeout=5
        )
        assert "access-control-allow-origin" in response.headers
    
    def test_api_returns_json(self):
        """Test: API retorna JSON"""
        response = requests.get(f"{STAGING_API_URL}/health", timeout=5)
        assert response.headers["content-type"] == "application/json"


class TestStagingFrontend:
    """Smoke tests para frontend en staging"""
    
    def test_frontend_loads(self):
        """Test: Frontend carga correctamente"""
        response = requests.get(STAGING_FRONTEND_URL, timeout=5)
        assert response.status_code == 200
        assert "<!DOCTYPE html>" in response.text or "<!doctype html>" in response.text
    
    def test_static_assets_load(self):
        """Test: Assets estáticos cargan"""
        response = requests.get(STAGING_FRONTEND_URL, timeout=5)
        # Verificar que hay referencias a JS/CSS
        assert ".js" in response.text or ".css" in response.text


class TestStagingAuth:
    """Smoke tests para autenticación"""
    
    def test_login_endpoint_exists(self):
        """Test: Login endpoint existe"""
        response = requests.post(
            f"{STAGING_API_URL}/api/v1/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "wrong"
            },
            timeout=5
        )
        # Puede ser 200, 401, o 422 pero no 404
        assert response.status_code != 404
    
    def test_protected_endpoint_requires_auth(self):
        """Test: Endpoints protegidos requieren autenticación"""
        response = requests.get(
            f"{STAGING_API_URL}/api/v1/auth/me",
            timeout=5
        )
        assert response.status_code in [401, 403]


class TestStagingDatabase:
    """Smoke tests para base de datos"""
    
    def test_database_connection(self):
        """Test: Base de datos conectada (indirectamente via health)"""
        response = requests.get(f"{STAGING_API_URL}/health", timeout=5)
        assert response.status_code == 200
        # Si health responde OK, la DB está conectada


class TestStagingPerformance:
    """Smoke tests de performance básico"""
    
    def test_api_response_time(self):
        """Test: API responde en menos de 1 segundo"""
        import time
        start = time.time()
        response = requests.get(f"{STAGING_API_URL}/health", timeout=5)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0, f"API tardó {duration}s (debe ser < 1s)"
```

### Archivo 4: `docs/DISASTER_RECOVERY.md`

```markdown
# Plan de Disaster Recovery - SaaS Cafeterías

## Definiciones

**RTO (Recovery Time Objective)**: Tiempo máximo aceptable de inactividad  
**RPO (Recovery Point Objective)**: Pérdida máxima de datos aceptable  
**MTTR (Mean Time To Repair)**: Tiempo promedio para reparar

---

## Métricas del Sistema

| Métrica | Valor | Justificación |
|---------|-------|---------------|
| RTO | 2 horas | Tiempo para restaurar desde backup |
| RPO | 1 hora | Frecuencia de backups automáticos |
| MTTR | < 30 min | Para errores menores |
| Uptime objetivo | 99.9% | ~8 horas de downtime/año permitido |

---

## Escenarios de Disaster

### 1. Pérdida de Base de Datos

**Síntomas**:
- Aplicación no puede conectar a DB
- Errores de conexión en logs
- Health check falló

**Procedimiento**:
1. Verificar último backup (debe ser < 1 hora)
   ```bash
   ls -lh /backups/ | tail -5
   ```

2. Descargar desde S3 si es necesario
   ```bash
   aws s3 cp s3://saas-backups/$(date +%Y%m%d)/latest.sql.gz /tmp/
   ```

3. Provisionar nueva instancia PostgreSQL (si necesario)

4. Restaurar desde backup
   ```bash
   ./scripts/restore.sh /backups/db_TIMESTAMP.sql.gz --force
   ```

5. Actualizar connection string en variables de entorno

6. Reiniciar servicios
   ```bash
   docker-compose restart backend
   ```

7. Verificar integridad
   ```bash
   psql $DATABASE# 📅 SEMANA 2 - PLAN DE ACCIÓN COMPLETO
## Testing + Backups + Deploy Staging

**Fecha de inicio**: Semana del [TU_FECHA]  
**Objetivo**: Sistema production-ready con 85% coverage

---

## 🎯 OBJETIVOS DE LA SEMANA

- ✅ Elevar coverage de 65% → 85%+
- ✅ Crear 33 tests nuevos (18 unitarios + 5 integración + 10 smoke)
- ✅ Validar sistema de backups
- ✅ Deploy a staging environment
- ✅ Sistema production-ready

---

## 📆 DÍA 6 (LUNES) - TESTS DE ORDERS

### Objetivo
Crear tests completos para `app/api/v1/orders.py` y elevar coverage de 25% a 75%+

### Archivo a Crear: `tests/unit/api/v1/test_orders.py`

```python
"""
Tests unitarios para el módulo de órdenes
Coverage objetivo: 75%+
Total de tests: 10
"""

import pytest
from decimal import Decimal
from app.db.models.order import OrderStatus

class TestCreateOrder:
    """Tests para creación de órdenes"""
    
    def test_create_order_success(self, client, customer_token, sample_business, sample_product):
        """Test: Cliente puede crear una orden con productos válidos"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [
                {
                    "product_id": sample_product.id,
                    "quantity": 2
                }
            ],
            "notes": "Sin azúcar"
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["business_id"] == sample_business.id
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["status"] == "pending"
        assert data["notes"] == "Sin azúcar"
    
    def test_create_order_invalid_product_fails(self, client, customer_token, sample_business):
        """Test: Orden con producto inexistente falla"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": 99999, "quantity": 1}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        assert response.status_code == 404
    
    def test_create_order_out_of_stock_fails(self, client, customer_token, sample_business, db):
        """Test: Orden con producto sin stock falla"""
        from app.db.models.product import Product
        
        product = Product(
            name="Sin Stock",
            price=Decimal("100.00"),
            stock=0,
            business_id=sample_business.id
        )
        db.add(product)
        db.commit()
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": product.id, "quantity": 1}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        assert response.status_code == 400
        assert "stock" in response.json()["detail"].lower()
    
    def test_create_order_negative_quantity_fails(self, client, customer_token, sample_business, sample_product):
        """Test: Cantidad negativa es rechazada"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": -1}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        assert response.status_code == 422


class TestOrderStatusTransitions:
    """Tests para transiciones de estado de órdenes"""
    
    def test_order_status_pending_to_confirmed(self, client, owner_token, sample_order):
        """Test: Owner puede confirmar orden pendiente"""
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        response = client.patch(
            f"/api/v1/orders/{sample_order.id}/status",
            json={"status": "confirmed"},
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
    
    def test_order_status_confirmed_to_completed(self, client, owner_token, db, sample_order):
        """Test: Owner puede completar orden confirmada"""
        sample_order.status = OrderStatus.CONFIRMED
        db.commit()
        
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = client.patch(
            f"/api/v1/orders/{sample_order.id}/status",
            json={"status": "completed"},
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
    
    def test_order_status_invalid_transition_fails(self, client, owner_token, sample_order):
        """Test: Transición inválida (pending → completed) falla"""
        headers = {"Authorization": f"Bearer {owner_token}"}
        
        response = client.patch(
            f"/api/v1/orders/{sample_order.id}/status",
            json={"status": "completed"},
            headers=headers
        )
        
        assert response.status_code == 400
        assert "invalid transition" in response.json()["detail"].lower()


class TestOrderCalculations:
    """Tests para cálculos de órdenes"""
    
    def test_calculate_order_total_single_item(self, client, customer_token, sample_business, sample_product):
        """Test: Total calculado correctamente para un item"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": 3}]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        expected_total = sample_product.price * 3
        assert Decimal(str(data["total"])) == expected_total
    
    def test_calculate_order_total_multiple_items(self, client, customer_token, sample_business, db):
        """Test: Total calculado correctamente para múltiples items"""
        from app.db.models.product import Product
        
        product1 = Product(name="Producto 1", price=Decimal("100.00"), stock=50, business_id=sample_business.id)
        product2 = Product(name="Producto 2", price=Decimal("150.00"), stock=50, business_id=sample_business.id)
        db.add_all([product1, product2])
        db.commit()
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        payload = {
            "business_id": sample_business.id,
            "items": [
                {"product_id": product1.id, "quantity": 2},
                {"product_id": product2.id, "quantity": 1}
            ]
        }
        
        response = client.post("/api/v1/orders", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["total"])) == Decimal("350.00")


class TestCancelOrder:
    """Tests para cancelación de órdenes"""
    
    def test_cancel_pending_order_success(self, client, customer_token, sample_order):
        """Test: Cliente puede cancelar orden pendiente"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        
        response = client.delete(f"/api/v1/orders/{sample_order.id}", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
    
    def test_cancel_completed_order_fails(self, client, customer_token, db, sample_order):
        """Test: No se puede cancelar orden completada"""
        sample_order.status = OrderStatus.COMPLETED
        db.commit()
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.delete(f"/api/v1/orders/{sample_order.id}", headers=headers)
        
        assert response.status_code == 400
        assert "cannot cancel" in response.json()["detail"].lower()
```

### Comandos para Ejecutar

```bash
# Ejecutar tests del día 6
pytest tests/unit/api/v1/test_orders.py -v

# Verificar coverage
pytest --cov=app.api.v1.orders tests/unit/api/v1/test_orders.py --cov-report=term

# Ejecutar todos los tests
pytest tests/unit/api/v1/ -v
```

### Entregables Día 6
- ✅ Archivo `test_orders.py` con 10 tests
- ✅ Coverage de `orders.py`: 25% → 75%
- ✅ Todos los tests pasando

---

## 📆 DÍA 7 (MARTES) - TESTS DE PAYMENTS

### Objetivo
Crear tests completos para `app/api/v1/payments.py` incluyendo mocking de MercadoPago

### Archivo a Crear: `tests/unit/api/v1/test_payments.py`

```python
"""
Tests unitarios para el módulo de pagos
Coverage objetivo: 70%+
Total de tests: 8
"""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

class TestCreatePayment:
    """Tests para creación de pagos"""
    
    @patch('app.services.payment_service.PaymentService.create_preference')
    def test_create_payment_mercadopago_success(self, mock_create, client, customer_token, sample_order):
        """Test: Creación de preferencia de pago exitosa"""
        mock_create.return_value = {
            "preference_id": "123456-abc-def",
            "init_point": "https://mercadopago.com/checkout/...",
            "sandbox_init_point": "https://sandbox.mercadopago.com/..."
        }
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post(
            f"/api/v1/payments/create-preference",
            json={
                "order_id": sample_order.id,
                "amount": float(sample_order.total)
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "preference_id" in data
        assert "init_point" in data
    
    def test_create_payment_invalid_amount_fails(self, client, customer_token, sample_order):
        """Test: Monto negativo es rechazado"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post(
            f"/api/v1/payments/create-preference",
            json={
                "order_id": sample_order.id,
                "amount": -100.0
            },
            headers=headers
        )
        
        assert response.status_code == 422
    
    def test_create_payment_nonexistent_order_fails(self, client, customer_token):
        """Test: Orden inexistente falla"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = client.post(
            f"/api/v1/payments/create-preference",
            json={
                "order_id": 99999,
                "amount": 100.0
            },
            headers=headers
        )
        
        assert response.status_code == 404


class TestPaymentWebhook:
    """Tests para webhooks de MercadoPago"""
    
    @patch('app.services.payment_service.PaymentService.verify_payment')
    def test_webhook_approved_updates_order(self, mock_verify, client, db, sample_order):
        """Test: Webhook con pago aprobado actualiza orden"""
        from app.db.models.payment import PaymentStatus
        
        mock_verify.return_value = {
            "status": "approved",
            "payment_id": "123456789"
        }
        
        webhook_data = {
            "type": "payment",
            "data": {"id": "123456789"}
        }
        
        response = client.post("/api/v1/payments/webhook", json=webhook_data)
        
        assert response.status_code == 200
        db.refresh(sample_order)
        assert sample_order.payment_status == PaymentStatus.PAID
    
    @patch('app.services.payment_service.PaymentService.verify_payment')
    def test_webhook_rejected_updates_order(self, mock_verify, client, db, sample_order):
        """Test: Webhook con pago rechazado actualiza orden"""
        from app.db.models.payment import PaymentStatus
        
        mock_verify.return_value = {
            "status": "rejected",
            "payment_id": "123456789"
        }
        
        webhook_data = {
            "type": "payment",
            "data": {"id": "123456789"}
        }
        
        response = client.post("/api/v1/payments/webhook", json=webhook_data)
        
        assert response.status_code == 200
        db.refresh(sample_order)
        assert sample_order.payment_status == PaymentStatus.FAILED
    
    def test_webhook_invalid_signature_fails(self, client):
        """Test: Webhook con firma inválida es rechazado"""
        webhook_data = {
            "type": "payment",
            "data": {"id": "fake"}
        }
        
        response = client.post(
            "/api/v1/payments/webhook",
            json=webhook_data,
            headers={"X-Signature": "invalid_signature"}
        )
        
        assert response.status_code in [401, 403, 400]


class TestRefundPayment:
    """Tests para reembolsos"""
    
    @patch('app.services.payment_service.PaymentService.refund_payment')
    def test_refund_payment_success(self, mock_refund, client, owner_token, db, sample_order):
        """Test: Owner puede reembolsar pago"""
        from app.db.models.payment import Payment, PaymentStatus
        
        payment = Payment(
            order_id=sample_order.id,
            amount=sample_order.total,
            payment_method="mercadopago",
            payment_id="123456",
            status=PaymentStatus.PAID
        )
        db.add(payment)
        db.commit()
        
        mock_refund.return_value = {"status": "refunded"}
        
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = client.post(f"/api/v1/payments/{payment.id}/refund", headers=headers)
        
        assert response.status_code == 200
        db.refresh(payment)
        assert payment.status == PaymentStatus.REFUNDED
    
    def test_refund_already_refunded_fails(self, client, owner_token, db, sample_order):
        """Test: No se puede reembolsar dos veces"""
        from app.db.models.payment import Payment, PaymentStatus
        
        payment = Payment(
            order_id=sample_order.id,
            amount=sample_order.total,
            payment_method="mercadopago",
            payment_id="123456",
            status=PaymentStatus.REFUNDED
        )
        db.add(payment)
        db.commit()
        
        headers = {"Authorization": f"Bearer {owner_token}"}
        response = client.post(f"/api/v1/payments/{payment.id}/refund", headers=headers)
        
        assert response.status_code == 400
        assert "already refunded" in response.json()["detail"].lower()
```

### Comandos para Ejecutar

```bash
# Ejecutar tests del día 7
pytest tests/unit/api/v1/test_payments.py -v

# Verificar coverage
pytest --cov=app.api.v1.payments tests/unit/api/v1/test_payments.py --cov-report=term

# Coverage total hasta ahora
pytest --cov=app.api.v1 tests/unit/api/v1/ --cov-report=html
```

### Entregables Día 7
- ✅ Archivo `test_payments.py` con 8 tests
- ✅ Mocking de MercadoPago funcionando
- ✅ Coverage de `payments.py`: 25% → 70%

---

## 📆 DÍA 8 (MIÉRCOLES) - TESTS DE INTEGRACIÓN

### Objetivo
Crear tests de integración que validen flujos completos del sistema

### Archivo a Crear: `tests/integration/test_complete_flows.py`

```python
"""
Tests de integración para flujos completos del sistema
Valida interacciones entre múltiples componentes
Total de tests: 5
"""

import pytest
from decimal import Decimal
from unittest.mock import patch

class TestCompleteUserJourney:
    """Test del journey completo de un usuario"""
    
    def test_complete_user_flow(self, client, db):
        """
        Test: Usuario completo desde registro hasta compra
        
        Flujo:
        1. Registro de usuario
        2. Login
        3. Ver negocios disponibles
        4. Ver productos de un negocio
        5. Crear orden
        6. Simular pago
        7. Verificar orden pagada
        """
        # 1. Registro
        register_data = {
            "email": "customer@test.com",
            "password": "Test1234!",
            "full_name": "Test Customer"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        # 2. Login
        login_data = {
            "username": "customer@test.com",
            "password": "Test1234!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Ver negocios
        response = client.get("/api/v1/businesses", headers=headers)
        assert response.status_code == 200
        businesses = response.json()
        assert len(businesses) > 0
        business_id = businesses[0]["id"]
        
        # 4. Ver productos
        response = client.get(f"/api/v1/businesses/{business_id}/products", headers=headers)
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        product_id = products[0]["id"]
        
        # 5. Crear orden
        order_data = {
            "business_id": business_id,
            "items": [{"product_id": product_id, "quantity": 2}]
        }
        response = client.post("/api/v1/orders", json=order_data, headers=headers)
        assert response.status_code == 201
        order = response.json()
        order_id = order["id"]
        assert order["status"] == "pending"
        
        # 6. Crear preferencia de pago (mock)
        with patch('app.services.payment_service.PaymentService.create_preference') as mock:
            mock.return_value = {
                "preference_id": "test-123",
                "init_point": "https://test.com"
            }
            
            payment_data = {
                "order_id": order_id,
                "amount": float(order["total"])
            }
            response = client.post(
                "/api/v1/payments/create-preference",
                json=payment_data,
                headers=headers
            )
            assert response.status_code == 200
        
        # 7. Simular webhook de pago aprobado
        with patch('app.services.payment_service.PaymentService.verify_payment') as mock:
            mock.return_value = {"status": "approved", "payment_id": "123"}
            
            webhook_data = {
                "type": "payment",
                "data": {"id": "123"}
            }
            response = client.post("/api/v1/payments/webhook", json=webhook_data)
            assert response.status_code == 200
        
        # 8. Verificar que orden está pagada
        response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        order_updated = response.json()
        assert order_updated["payment_status"] == "paid"


class TestBusinessOwnerFlow:
    """Test del flujo de un business owner"""
    
    def test_business_owner_complete_flow(self, client, db):
        """
        Test: Owner gestiona su negocio completo
        
        Flujo:
        1. Registro como owner
        2. Login
        3. Crear negocio
        4. Agregar productos
        5. Recibir orden de cliente
        6. Confirmar orden
        7. Completar orden
        """
        # 1-2. Registro y login de owner
        register_data = {
            "email": "owner@test.com",
            "password": "Owner1234!",
            "full_name": "Business Owner",
            "role": "owner"
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        
        login_data = {
            "username": "owner@test.com",
            "password": "Owner1234!"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Crear negocio
        business_data = {
            "name": "Mi Cafetería",
            "description": "La mejor del barrio",
            "address": "Calle 123"
        }
        response = client.post("/api/v1/businesses", json=business_data, headers=headers)
        assert response.status_code == 201
        business_id = response.json()["id"]
        
        # 4. Agregar productos
        product_data = {
            "name": "Café Americano",
            "description": "Café negro",
            "price": 350.00,
            "stock": 100
        }
        response = client.post(
            f"/api/v1/businesses/{business_id}/products",
            json=product_data,
            headers=headers
        )
        assert response.status_code == 201
        product_id = response.json()["id"]
        
        # 5. Simular orden de cliente
        from app.db.models.user import User
        from app.db.models.order import Order, OrderItem
        
        customer = User(
            email="customer2@test.com",
            hashed_password="hash",
            role="customer"
        )
        db.add(customer)
        db.commit()
        
        order = Order(
            user_id=customer.id,
            business_id=business_id,
            total=Decimal("700.00"),
            status="pending"
        )
        db.add(order)
        db.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=2,
            unit_price=Decimal("350.00"),
            subtotal=Decimal("700.00")
        )
        db.add(order_item)
        db.commit()
        
        # 6. Owner confirma orden
        response = client.patch(
            f"/api/v1/orders/{order.id}/status",
            json={"status": "confirmed"},
            headers=headers
        )
        assert response.status_code == 200
        
        # 7. Owner completa orden
        response = client.patch(
            f"/api/v1/orders/{order.id}/status",
            json={"status": "completed"},
            headers=headers
        )
        assert response.status_code == 200


class TestAdminPermissionsFlow:
    """Test de permisos de administrador"""
    
    def test_admin_can_manage_all_businesses(self, client, admin_token, db):
        """Test: Admin puede gestionar cualquier negocio"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Crear negocio de otro usuario
        from app.db.models.user import User
        from app.db.models.business import Business
        
        owner = User(
            email="owner2@test.com",
            hashed_password="hash",
            role="owner"
        )
        db.add(owner)
        db.commit()
        
        business = Business(
            name="Negocio Ajeno",
            owner_id=owner.id
        )
        db.add(business)
        db.commit()
        
        # Admin puede ver
        response = client.get(f"/api/v1/businesses/{business.id}", headers=headers)
        assert response.status_code == 200
        
        # Admin puede editar
        response = client.put(
            f"/api/v1/businesses/{business.id}",
            json={"name": "Editado por Admin"},
            headers=headers
        )
        assert response.status_code == 200
        
        # Admin puede eliminar
        response = client.delete(f"/api/v1/businesses/{business.id}", headers=headers)
        assert response.status_code == 204


class TestConcurrentOrders:
    """Test de concurrencia en creación de órdenes"""
    
    def test_concurrent_order_creation(self, client, customer_token, sample_business, sample_product, db):
        """Test: Múltiples órdenes simultáneas no causan problemas"""
        import concurrent.futures
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        order_data = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": 1}]
        }
        
        # Crear 10 órdenes concurrentemente
        def create_order():
            return client.post("/api/v1/orders", json=order_data, headers=headers)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_order) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # Verificar que todas las órdenes se crearon exitosamente
        success_count = sum(1 for r in results if r.status_code == 201)
        assert success_count == 10
        
        # Verificar que el stock se redujo correctamente
        db.refresh(sample_product)
        assert sample_product.stock >= 0


class TestPaymentFlow:
    """Test de flujo completo de pago"""
    
    def test_payment_flow_with_webhook(self, client, customer_token, sample_business, sample_product, db):
        """Test: Flujo completo desde orden hasta pago confirmado"""
        headers = {"Authorization": f"Bearer {customer_token}"}
        
        # 1. Crear orden
        order_data = {
            "business_id": sample_business.id,
            "items": [{"product_id": sample_product.id, "quantity": 1}]
        }
        response = client.post("/api/v1/orders", json=order_data, headers=headers)
        assert response.status_code == 201
        order_id = response.json()["id"]
        
        # 2. Crear preferencia de pago
        with patch('app.services.payment_service.PaymentService.create_preference') as mock:
            mock.return_value = {
                "preference_id": "pref-123",
                "init_point": "https://mp.com/checkout/pref-123"
            }
            
            response = client.post(
                "/api/v1/payments/create-preference",
                json={"order_id": order_id, "amount": 350.0},
                headers=headers
            )
            assert response.status_code == 200
            preference_id = response.json()["preference_id"]
        
        # 3. Simular pago en MercadoPago (webhook)
        with patch('app.services.payment_service.PaymentService.verify_payment') as mock:
            mock.return_value = {
                "status": "approved",
                "payment_id": "pay-456",
                "preference_id": preference_id
            }
            
            webhook_data = {
                "type": "payment",
                "data": {"id": "pay-456"}
            }
            response = client.post("/api/v1/payments/webhook", json=webhook_data)
            assert response.status_code == 200
        
        # 4. Verificar orden actualizada
        response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        order = response.json()
        assert order["payment_status"] == "paid"
```

### Comandos para Ejecutar

```bash
# Ejecutar tests de integración
pytest tests/integration/test_complete_flows.py -v

# Coverage total
pytest --cov=app --cov-report=html tests/

# Ver reporte HTML
python -m http.server 8080 -d htmlcov/
```

### Entregables Día 8
- ✅ 5 tests de integración E2E
- ✅ Flujos críticos validados
- ✅ Coverage total del sistema: 85%+

---

## 📆 DÍA 9 (JUEVES) - SISTEMA DE BACKUPS

### Objetivo
Crear sistema completo de backups automatizado con validación

### Archivo 1: `scripts/backup.sh`

```bash
#!/bin/bash
# scripts/backup.sh
# Script completo de backup con validación

set -e  # Salir si hay error
set -u  # Error si variable no definida

# ============================================
# CONFIGURACIÓN
# ============================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)
BACKUP_DIR="${BACKUP_DIR:-/backups}"
S3_BUCKET="${S3_BUCKET