"""Add Payment model

Revision ID: 002_add_payment
Revises: 001_initial
Create Date: 2025-09-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '002_add_payment'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create PaymentStatus enum
    op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'approved', 'authorized', 'in_process', 'in_mediation', 'rejected', 'cancelled', 'refunded', 'charged_back')")
    
    # Create payments table
    op.create_table('payments',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('mercadopago_payment_id', sa.String(), nullable=True),
    sa.Column('preference_id', sa.String(), nullable=True),
    sa.Column('external_reference', sa.String(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('currency', sa.String(), nullable=True),
    sa.Column('status', sa.Enum(name='paymentstatus'), nullable=True),
    sa.Column('payment_method', sa.String(), nullable=True),
    sa.Column('payment_type', sa.String(), nullable=True),
    sa.Column('transaction_amount', sa.Float(), nullable=True),
    sa.Column('net_received_amount', sa.Float(), nullable=True),
    sa.Column('total_paid_amount', sa.Float(), nullable=True),
    sa.Column('metadata', sa.Text(), nullable=True),
    sa.Column('webhook_data', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_external_reference'), 'payments', ['external_reference'], unique=False)
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_mercadopago_payment_id'), 'payments', ['mercadopago_payment_id'], unique=True)
    op.create_index(op.f('ix_payments_preference_id'), 'payments', ['preference_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_payments_preference_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_mercadopago_payment_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_external_reference'), table_name='payments')
    
    # Drop table
    op.drop_table('payments')
    
    # Drop enum
    op.execute("DROP TYPE paymentstatus")