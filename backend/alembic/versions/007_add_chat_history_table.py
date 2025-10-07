"""add chat_history table

Revision ID: 007_add_chat_history_table
Revises: 006_add_comprobantes_vencimientos
Create Date: 2025-10-07 17:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '007_add_chat_history_table'
down_revision = '006_add_comprobantes_vencimientos'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('chat_history',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('business_id', sa.CHAR(36), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True, default=0),
        sa.Column('model', sa.String(), nullable=True, default='gpt-4'),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], )
    )
    op.create_index(op.f('ix_chat_history_id'), 'chat_history', ['id'], unique=False)
    op.create_index(op.f('ix_chat_history_user_id'), 'chat_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_chat_history_created_at'), 'chat_history', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_history_created_at'), table_name='chat_history')
    op.drop_index(op.f('ix_chat_history_user_id'), table_name='chat_history')
    op.drop_index(op.f('ix_chat_history_id'), table_name='chat_history')
    op.drop_table('chat_history')
