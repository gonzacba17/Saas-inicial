"""add comprobantes and vencimientos tables

Revision ID: 006_add_comprobantes_vencimientos
Revises: 005_add_audit_logs_table
Create Date: 2025-10-07 16:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006_add_comprobantes_vencimientos'
down_revision = '005_add_audit_logs_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('comprobantes',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('business_id', sa.CHAR(36), nullable=False),
        sa.Column('user_id', sa.CHAR(36), nullable=False),
        sa.Column('tipo', sa.Enum('FACTURA_A', 'FACTURA_B', 'FACTURA_C', 'NOTA_CREDITO', 'NOTA_DEBITO', 'RECIBO', 'PRESUPUESTO', name='comprobantetype'), nullable=False),
        sa.Column('numero', sa.String(), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cuit_emisor', sa.String(length=11), nullable=True),
        sa.Column('razon_social_emisor', sa.String(), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('iva', sa.Float(), nullable=True),
        sa.Column('total', sa.Float(), nullable=False),
        sa.Column('moneda', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('PENDIENTE', 'PROCESADO', 'VALIDADO', 'RECHAZADO', 'ARCHIVADO', name='comprobantestatus'), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('ocr_data', sa.Text(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comprobantes_id'), 'comprobantes', ['id'], unique=False)
    op.create_index(op.f('ix_comprobantes_numero'), 'comprobantes', ['numero'], unique=False)
    op.create_index(op.f('ix_comprobantes_cuit_emisor'), 'comprobantes', ['cuit_emisor'], unique=False)
    
    op.create_table('vencimientos',
        sa.Column('id', sa.CHAR(36), nullable=False),
        sa.Column('business_id', sa.CHAR(36), nullable=False),
        sa.Column('comprobante_id', sa.CHAR(36), nullable=True),
        sa.Column('tipo', sa.Enum('IMPUESTO', 'SERVICIO', 'ALQUILER', 'PROVEEDOR', 'CREDITO', 'SEGURO', 'OTRO', name='vencimientotype'), nullable=False),
        sa.Column('descripcion', sa.String(), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('moneda', sa.String(), nullable=True),
        sa.Column('fecha_vencimiento', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_pago', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('PENDIENTE', 'PAGADO', 'VENCIDO', 'CANCELADO', name='vencimientostatus'), nullable=True),
        sa.Column('recordatorio_dias_antes', sa.Integer(), nullable=True),
        sa.Column('notificacion_enviada', sa.Boolean(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['comprobante_id'], ['comprobantes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vencimientos_id'), 'vencimientos', ['id'], unique=False)
    op.create_index(op.f('ix_vencimientos_fecha_vencimiento'), 'vencimientos', ['fecha_vencimiento'], unique=False)
    op.create_index(op.f('ix_vencimientos_status'), 'vencimientos', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_vencimientos_status'), table_name='vencimientos')
    op.drop_index(op.f('ix_vencimientos_fecha_vencimiento'), table_name='vencimientos')
    op.drop_index(op.f('ix_vencimientos_id'), table_name='vencimientos')
    op.drop_table('vencimientos')
    
    op.drop_index(op.f('ix_comprobantes_cuit_emisor'), table_name='comprobantes')
    op.drop_index(op.f('ix_comprobantes_numero'), table_name='comprobantes')
    op.drop_index(op.f('ix_comprobantes_id'), table_name='comprobantes')
    op.drop_table('comprobantes')
    
    op.execute('DROP TYPE IF EXISTS vencimientostatus')
    op.execute('DROP TYPE IF EXISTS vencimientotype')
    op.execute('DROP TYPE IF EXISTS comprobantestatus')
    op.execute('DROP TYPE IF EXISTS comprobantetype')
