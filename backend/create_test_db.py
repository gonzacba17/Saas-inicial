#!/usr/bin/env python3
"""
Script para crear base de datos SQLite para tests.
"""
import sqlite3
import os

def create_test_db():
    """Crear base de datos SQLite con schema básico para tests."""
    db_path = "saas_cafeterias.db"
    
    # Eliminar DB existente si existe
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla users
    cursor.execute('''
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME
        )
    ''')
    
    # Crear tabla businesses
    cursor.execute('''
        CREATE TABLE businesses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            business_type TEXT,
            owner_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Crear tabla products
    cursor.execute('''
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_url TEXT,
            is_available BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (business_id) REFERENCES businesses (id)
        )
    ''')
    
    # Crear tabla orders
    cursor.execute('''
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            business_id TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            total_amount REAL NOT NULL,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (business_id) REFERENCES businesses (id)
        )
    ''')
    
    # Crear tabla order_items
    cursor.execute('''
        CREATE TABLE order_items (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Crear tabla payments
    cursor.execute('''
        CREATE TABLE payments (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            business_id TEXT NOT NULL,
            mercadopago_payment_id TEXT,
            preference_id TEXT,
            external_reference TEXT,
            amount REAL NOT NULL,
            currency TEXT,
            status TEXT,
            payment_method TEXT,
            payment_type TEXT,
            transaction_amount REAL,
            net_received_amount REAL,
            total_paid_amount REAL,
            payment_metadata TEXT,
            webhook_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            processed_at DATETIME,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (business_id) REFERENCES businesses (id)
        )
    ''')
    
    # Crear tabla user_businesses
    cursor.execute('''
        CREATE TABLE user_businesses (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            business_id TEXT NOT NULL,
            role TEXT DEFAULT 'owner',
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (business_id) REFERENCES businesses (id)
        )
    ''')
    
    # Crear tabla ai_conversations
    cursor.execute('''
        CREATE TABLE ai_conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            business_id TEXT,
            assistant_type TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            response_time_ms INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (business_id) REFERENCES businesses (id)
        )
    ''')
    
    # Crear índices básicos
    cursor.execute('CREATE INDEX idx_users_email ON users (email)')
    cursor.execute('CREATE INDEX idx_users_username ON users (username)')
    cursor.execute('CREATE INDEX idx_businesses_name ON businesses (name)')
    cursor.execute('CREATE INDEX idx_products_business_id ON products (business_id)')
    cursor.execute('CREATE INDEX idx_orders_user_id ON orders (user_id)')
    cursor.execute('CREATE INDEX idx_orders_status ON orders (status)')
    cursor.execute('CREATE INDEX idx_payments_order_id ON payments (order_id)')
    cursor.execute('CREATE INDEX idx_user_businesses_user_id ON user_businesses (user_id)')
    cursor.execute('CREATE INDEX idx_user_businesses_business_id ON user_businesses (business_id)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de datos SQLite creada: {db_path}")
    print("✅ Tablas creadas: users, businesses, products, orders, order_items, payments, user_businesses, ai_conversations")
    print("✅ Índices básicos creados")

if __name__ == "__main__":
    create_test_db()