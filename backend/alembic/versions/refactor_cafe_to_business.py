"""refactor: rename cafe to business tables and relationships

Revision ID: 20250917_001
Revises: 
Create Date: 2025-09-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250917_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Rename cafes table to businesses
    op.rename_table('cafes', 'businesses')
    
    # Add business_type column to businesses table
    op.add_column('businesses', sa.Column('business_type', sa.String(), nullable=True))
    op.execute("UPDATE businesses SET business_type = 'restaurant' WHERE business_type IS NULL")
    
    # Rename cafe_id columns to business_id
    op.alter_column('products', 'cafe_id', new_column_name='business_id')
    op.alter_column('orders', 'cafe_id', new_column_name='business_id')
    
    # Update foreign key constraints
    op.drop_constraint('products_cafe_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key('products_business_id_fkey', 'products', 'businesses', ['business_id'], ['id'])
    
    op.drop_constraint('orders_cafe_id_fkey', 'orders', type_='foreignkey')
    op.create_foreign_key('orders_business_id_fkey', 'orders', 'businesses', ['business_id'], ['id'])

def downgrade() -> None:
    # Reverse the changes
    op.drop_constraint('orders_business_id_fkey', 'orders', type_='foreignkey')
    op.create_foreign_key('orders_cafe_id_fkey', 'orders', 'cafes', ['business_id'], ['id'])
    
    op.drop_constraint('products_business_id_fkey', 'products', type_='foreignkey')
    op.create_foreign_key('products_cafe_id_fkey', 'products', 'cafes', ['business_id'], ['id'])
    
    # Rename business_id columns back to cafe_id
    op.alter_column('orders', 'business_id', new_column_name='cafe_id')
    op.alter_column('products', 'business_id', new_column_name='cafe_id')
    
    # Remove business_type column
    op.drop_column('businesses', 'business_type')
    
    # Rename businesses table back to cafes
    op.rename_table('businesses', 'cafes')