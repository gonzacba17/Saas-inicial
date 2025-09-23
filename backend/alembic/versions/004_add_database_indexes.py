"""Add database indexes for performance optimization

Revision ID: 004_add_database_indexes
Revises: 003_add_user_role_field
Create Date: 2025-09-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_database_indexes'
down_revision = '003_add_user_role_field'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance-critical indexes"""
    
    # Users table indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Businesses table indexes
    op.create_index('idx_businesses_owner_id', 'businesses', ['owner_id'])
    op.create_index('idx_businesses_created_at', 'businesses', ['created_at'])
    op.create_index('idx_businesses_name', 'businesses', ['name'])
    
    # Products table indexes
    op.create_index('idx_products_business_id', 'products', ['business_id'])
    op.create_index('idx_products_created_at', 'products', ['created_at'])
    op.create_index('idx_products_price', 'products', ['price'])
    op.create_index('idx_products_name', 'products', ['name'])
    
    # Orders table indexes
    op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    op.create_index('idx_orders_total', 'orders', ['total'])
    op.create_index('idx_orders_user_status', 'orders', ['user_id', 'status'])
    op.create_index('idx_orders_created_status', 'orders', ['created_at', 'status'])
    
    # Order Items table indexes (if exists)
    try:
        op.create_index('idx_order_items_order_id', 'order_items', ['order_id'])
        op.create_index('idx_order_items_product_id', 'order_items', ['product_id'])
    except:
        # Table might not exist yet
        pass
    
    # User Business relationships indexes (if exists)
    try:
        op.create_index('idx_user_business_user_id', 'user_business', ['user_id'])
        op.create_index('idx_user_business_business_id', 'user_business', ['business_id'])
        op.create_index('idx_user_business_role', 'user_business', ['role'])
        op.create_index('idx_user_business_unique', 'user_business', ['user_id', 'business_id'], unique=True)
    except:
        # Table might not exist yet
        pass
    
    # Payments table indexes (if exists)
    try:
        op.create_index('idx_payments_order_id', 'payments', ['order_id'])
        op.create_index('idx_payments_status', 'payments', ['status'])
        op.create_index('idx_payments_created_at', 'payments', ['created_at'])
        op.create_index('idx_payments_mercadopago_id', 'payments', ['mercadopago_payment_id'])
        op.create_index('idx_payments_external_ref', 'payments', ['external_reference'])
        op.create_index('idx_payments_business_id', 'payments', ['business_id'])
    except:
        # Table might not exist yet
        pass
    
    # AI Conversations table indexes (if exists)
    try:
        op.create_index('idx_ai_conversations_user_id', 'ai_conversations', ['user_id'])
        op.create_index('idx_ai_conversations_business_id', 'ai_conversations', ['business_id'])
        op.create_index('idx_ai_conversations_created_at', 'ai_conversations', ['created_at'])
        op.create_index('idx_ai_conversations_type', 'ai_conversations', ['conversation_type'])
    except:
        # Table might not exist yet
        pass


def downgrade():
    """Remove performance indexes"""
    
    # Users table indexes
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_role', 'users')
    op.drop_index('idx_users_created_at', 'users')
    
    # Businesses table indexes
    op.drop_index('idx_businesses_owner_id', 'businesses')
    op.drop_index('idx_businesses_created_at', 'businesses')
    op.drop_index('idx_businesses_name', 'businesses')
    
    # Products table indexes
    op.drop_index('idx_products_business_id', 'products')
    op.drop_index('idx_products_created_at', 'products')
    op.drop_index('idx_products_price', 'products')
    op.drop_index('idx_products_name', 'products')
    
    # Orders table indexes
    op.drop_index('idx_orders_user_id', 'orders')
    op.drop_index('idx_orders_status', 'orders')
    op.drop_index('idx_orders_created_at', 'orders')
    op.drop_index('idx_orders_total', 'orders')
    op.drop_index('idx_orders_user_status', 'orders')
    op.drop_index('idx_orders_created_status', 'orders')
    
    # Order Items table indexes
    try:
        op.drop_index('idx_order_items_order_id', 'order_items')
        op.drop_index('idx_order_items_product_id', 'order_items')
    except:
        pass
    
    # User Business relationships indexes
    try:
        op.drop_index('idx_user_business_user_id', 'user_business')
        op.drop_index('idx_user_business_business_id', 'user_business')
        op.drop_index('idx_user_business_role', 'user_business')
        op.drop_index('idx_user_business_unique', 'user_business')
    except:
        pass
    
    # Payments table indexes
    try:
        op.drop_index('idx_payments_order_id', 'payments')
        op.drop_index('idx_payments_status', 'payments')
        op.drop_index('idx_payments_created_at', 'payments')
        op.drop_index('idx_payments_mercadopago_id', 'payments')
        op.drop_index('idx_payments_external_ref', 'payments')
        op.drop_index('idx_payments_business_id', 'payments')
    except:
        pass
    
    # AI Conversations table indexes
    try:
        op.drop_index('idx_ai_conversations_user_id', 'ai_conversations')
        op.drop_index('idx_ai_conversations_business_id', 'ai_conversations')
        op.drop_index('idx_ai_conversations_created_at', 'ai_conversations')
        op.drop_index('idx_ai_conversations_type', 'ai_conversations')
    except:
        pass