"""Add role field to User model

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_payment'
branch_labels = None
depends_on = None

def upgrade():
    """Add role enum and role field to users table."""
    # Check if we're using SQLite or PostgreSQL
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        # Create UserRole enum for PostgreSQL
        user_role_enum = postgresql.ENUM('user', 'owner', 'admin', name='userrole')
        user_role_enum.create(bind)
        
        # Add role column to users table
        op.add_column('users', sa.Column('role', user_role_enum, nullable=False, server_default='user'))
        
        # Remove server_default after column creation
        op.alter_column('users', 'role', server_default=None)
    else:
        # For SQLite, use String with check constraint
        op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='user'))
        
        # Add check constraint for SQLite
        op.create_check_constraint(
            'check_user_role', 
            'users', 
            "role IN ('user', 'owner', 'admin')"
        )
        
        # Remove server_default after column creation
        op.alter_column('users', 'role', server_default=None)

def downgrade():
    """Remove role field and enum from users table."""
    # Check if we're using SQLite or PostgreSQL
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        # Drop role column
        op.drop_column('users', 'role')
        
        # Drop UserRole enum
        user_role_enum = postgresql.ENUM('user', 'owner', 'admin', name='userrole')
        user_role_enum.drop(bind)
    else:
        # For SQLite, drop check constraint first
        op.drop_constraint('check_user_role', 'users', type_='check')
        
        # Drop role column
        op.drop_column('users', 'role')
