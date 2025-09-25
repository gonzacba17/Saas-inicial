"""
Tests for orders endpoints - Corregidos
"""
import pytest
import time


def test_get_user_orders(client, user_token):
    """Test getting user orders."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_orders_unauthorized(client):
    """Test getting orders without authentication."""
    response = client.get("/api/v1/orders")
    assert response.status_code == 401


def test_get_user_orders_with_pagination(client, user_token):
    """Test getting user orders with pagination."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/orders?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_order_requires_auth(client, test_business, test_product):
    """Test that creating an order requires authentication."""
    if not test_business or not test_product:
        pytest.skip("Could not set up test data")
    
    order_data = {
        "business_id": test_business["id"],
        "items": [
            {
                "product_id": test_product["id"],
                "quantity": 2,
                "unit_price": test_product["price"]
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data)
    assert response.status_code == 401


def test_create_order_with_valid_data(client, user_token, test_business, test_product):
    """Test creating an order with valid data."""
    if not user_token or not test_business or not test_product:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    order_data = {
        "business_id": test_business["id"],
        "items": [
            {
                "product_id": test_product["id"],
                "quantity": 2,
                "unit_price": test_product["price"]
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data, headers=headers)
    assert response.status_code == 200
    
    order = response.json()
    assert order["business_id"] == test_business["id"]
    assert order["status"] == "pending"
    assert len(order["items"]) == 1
    expected_total = 2 * test_product["price"]
    assert order["total_amount"] == expected_total


def test_create_order_with_invalid_business(client, user_token):
    """Test creating an order with invalid business ID."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    order_data = {
        "business_id": "550e8400-e29b-41d4-a716-446655440000",  # Non-existent business
        "items": [
            {
                "product_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantity": 2,
                "unit_price": 10.0
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data, headers=headers)
    assert response.status_code == 404


def test_create_order_with_empty_items(client, user_token, test_business):
    """Test creating an order with empty items list."""
    if not user_token or not test_business:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    order_data = {
        "business_id": test_business["id"],
        "items": []
    }
    
    response = client.post("/api/v1/orders", json=order_data, headers=headers)
    # Should fail validation for empty items
    assert response.status_code in [400, 422]


def test_get_order_by_id(client, user_token, test_order):
    """Test getting a specific order by ID."""
    if not user_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/api/v1/orders/{test_order['id']}", headers=headers)
    assert response.status_code == 200
    
    order = response.json()
    assert order["id"] == test_order["id"]
    assert order["business_id"] == test_order["business_id"]


def test_get_nonexistent_order(client, user_token):
    """Test getting a non-existent order."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    fake_id = "550e8400-e29b-41d4-a716-446655440000"
    
    response = client.get(f"/api/v1/orders/{fake_id}", headers=headers)
    assert response.status_code == 404


def test_get_order_unauthorized(client):
    """Test getting an order without authentication."""
    fake_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.get(f"/api/v1/orders/{fake_id}")
    assert response.status_code == 401


def test_get_business_orders(client, admin_token, test_business, test_order):
    """Test getting orders for a business (admin access)."""
    if not admin_token or not test_business or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/v1/orders/business/{test_business['id']}", headers=headers)
    assert response.status_code == 200
    
    orders = response.json()
    assert isinstance(orders, list)


def test_get_business_orders_unauthorized(client, user_token):
    """Test getting business orders without proper permissions."""
    if not user_token:
        pytest.skip("Could not authenticate user")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    fake_business_id = "550e8400-e29b-41d4-a716-446655440000"
    
    response = client.get(f"/api/v1/orders/business/{fake_business_id}", headers=headers)
    # Should return 404 (business not found) or 403 (no permission)
    assert response.status_code in [403, 404]


def test_update_order_status(client, admin_token, test_order):
    """Test updating order status."""
    if not admin_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {"status": "confirmed"}
    
    response = client.put(f"/api/v1/orders/{test_order['id']}/status", json=update_data, headers=headers)
    assert response.status_code == 200
    
    updated_order = response.json()
    assert updated_order["status"] == "confirmed"


def test_user_cannot_update_order_status(client, user_token, test_order):
    """Test that regular users cannot update order status."""
    if not user_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {"status": "confirmed"}
    
    response = client.put(f"/api/v1/orders/{test_order['id']}/status", json=update_data, headers=headers)
    # Should fail with 403 Forbidden
    assert response.status_code == 403


def test_get_order_items(client, user_token, test_order):
    """Test getting order items."""
    if not user_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/api/v1/orders/{test_order['id']}/items", headers=headers)
    assert response.status_code == 200
    
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    
    # Check first item structure
    item = items[0]
    assert "quantity" in item
    assert "unit_price" in item
    assert "product_id" in item


def test_create_order_with_multiple_items(client, user_token, admin_token, test_business):
    """Test creating an order with multiple items."""
    if not user_token or not admin_token or not test_business:
        pytest.skip("Could not set up test data")
    
    # Create multiple products
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    timestamp = int(time.time())
    
    products = []
    for i in range(2):
        product_data = {
            "business_id": test_business["id"],
            "name": f"Test Product {i+1} {timestamp}",
            "description": f"Test product {i+1} for multiple items test",
            "price": 10.0 + i,
            "category": "test"
        }
        
        response = client.post("/api/v1/products", json=product_data, headers=admin_headers)
        if response.status_code == 200:
            products.append(response.json())
    
    if len(products) < 2:
        pytest.skip("Could not create test products")
    
    # Create order with multiple items
    user_headers = {"Authorization": f"Bearer {user_token}"}
    order_data = {
        "business_id": test_business["id"],
        "items": [
            {
                "product_id": products[0]["id"],
                "quantity": 2,
                "unit_price": products[0]["price"]
            },
            {
                "product_id": products[1]["id"], 
                "quantity": 1,
                "unit_price": products[1]["price"]
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data, headers=user_headers)
    assert response.status_code == 200
    
    order = response.json()
    assert len(order["items"]) == 2
    expected_total = (2 * products[0]["price"]) + (1 * products[1]["price"])
    assert order["total_amount"] == expected_total


def test_order_status_transitions(client, admin_token, test_order):
    """Test valid order status transitions."""
    if not admin_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test status progression: pending -> confirmed -> preparing -> ready -> completed
    status_transitions = ["confirmed", "preparing", "ready", "completed"]
    
    for status in status_transitions:
        update_data = {"status": status}
        response = client.put(f"/api/v1/orders/{test_order['id']}/status", json=update_data, headers=headers)
        assert response.status_code == 200
        
        updated_order = response.json()
        assert updated_order["status"] == status


def test_invalid_order_status(client, admin_token, test_order):
    """Test updating order with invalid status."""
    if not admin_token or not test_order:
        pytest.skip("Could not set up test data")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = {"status": "invalid_status"}
    
    response = client.put(f"/api/v1/orders/{test_order['id']}/status", json=update_data, headers=headers)
    # Should fail with validation error
    assert response.status_code == 422


def test_order_total_calculation(client, user_token, admin_token, test_business):
    """Test order total calculation accuracy."""
    if not user_token or not admin_token or not test_business:
        pytest.skip("Could not set up test data")
    
    # Create a product with specific price
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    timestamp = int(time.time())
    product_data = {
        "business_id": test_business["id"],
        "name": f"Price Test Product {timestamp}",
        "description": "Product for price calculation test",
        "price": 12.99,
        "category": "test"
    }
    
    product_response = client.post("/api/v1/products", json=product_data, headers=admin_headers)
    if product_response.status_code != 200:
        pytest.skip("Could not create test product")
    
    product = product_response.json()
    
    # Create order with specific quantity
    user_headers = {"Authorization": f"Bearer {user_token}"}
    order_data = {
        "business_id": test_business["id"],
        "items": [
            {
                "product_id": product["id"],
                "quantity": 3,
                "unit_price": product["price"]
            }
        ]
    }
    
    response = client.post("/api/v1/orders", json=order_data, headers=user_headers)
    assert response.status_code == 200
    
    order = response.json()
    expected_total = 3 * 12.99  # 38.97
    assert order["total_amount"] == expected_total


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])