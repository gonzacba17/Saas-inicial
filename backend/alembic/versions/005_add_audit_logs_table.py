"""Add audit logs table for security and compliance tracking

Revision ID: 005_add_audit_logs_table
Revises: 004_add_database_indexes
Create Date: 2025-09-18 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_audit_logs_table'
down_revision = '004_add_database_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Create audit_logs table"""
    
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Action details
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        
        # User context
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('user_role', sa.String(50), nullable=True),
        
        # Request context
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(), nullable=True),
        
        # Resource context
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('business_id', sa.String(), nullable=True),
        
        # Action details
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        
        # Status
        sa.Column('success', sa.Boolean(), nullable=False, default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        
        # Additional metadata
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('correlation_id', sa.String(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_severity', 'audit_logs', ['severity'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_ip_address', 'audit_logs', ['ip_address'])
    op.create_index('idx_audit_logs_request_id', 'audit_logs', ['request_id'])
    op.create_index('idx_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('idx_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('idx_audit_logs_business_id', 'audit_logs', ['business_id'])
    op.create_index('idx_audit_logs_success', 'audit_logs', ['success'])
    op.create_index('idx_audit_logs_session_id', 'audit_logs', ['session_id'])
    op.create_index('idx_audit_logs_correlation_id', 'audit_logs', ['correlation_id'])
    
    # Composite indexes for common queries
    op.create_index('idx_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_logs_action_timestamp', 'audit_logs', ['action', 'timestamp'])
    op.create_index('idx_audit_logs_business_timestamp', 'audit_logs', ['business_id', 'timestamp'])
    op.create_index('idx_audit_logs_success_timestamp', 'audit_logs', ['success', 'timestamp'])


def downgrade():
    """Drop audit_logs table and indexes"""
    
    # Drop indexes first
    op.drop_index('idx_audit_logs_timestamp', 'audit_logs')
    op.drop_index('idx_audit_logs_action', 'audit_logs')
    op.drop_index('idx_audit_logs_severity', 'audit_logs')
    op.drop_index('idx_audit_logs_user_id', 'audit_logs')
    op.drop_index('idx_audit_logs_ip_address', 'audit_logs')
    op.drop_index('idx_audit_logs_request_id', 'audit_logs')
    op.drop_index('idx_audit_logs_resource_type', 'audit_logs')
    op.drop_index('idx_audit_logs_resource_id', 'audit_logs')
    op.drop_index('idx_audit_logs_business_id', 'audit_logs')
    op.drop_index('idx_audit_logs_success', 'audit_logs')
    op.drop_index('idx_audit_logs_session_id', 'audit_logs')
    op.drop_index('idx_audit_logs_correlation_id', 'audit_logs')
    op.drop_index('idx_audit_logs_user_timestamp', 'audit_logs')
    op.drop_index('idx_audit_logs_action_timestamp', 'audit_logs')
    op.drop_index('idx_audit_logs_business_timestamp', 'audit_logs')
    op.drop_index('idx_audit_logs_success_timestamp', 'audit_logs')
    
    # Drop table
    op.drop_table('audit_logs')