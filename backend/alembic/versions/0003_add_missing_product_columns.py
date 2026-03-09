"""add missing products columns for legacy production databases

Revision ID: 0003_add_missing_product_columns
Revises: 0002_add_address_to_orders
Create Date: 2026-03-09 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_add_missing_product_columns"
down_revision = "0002_add_address_to_orders"
branch_labels = None
depends_on = None


PRODUCT_COLUMNS = {
    "sku": sa.String(),
    "pieces": sa.Integer(),
    "series": sa.String(),
    "description": sa.Text(),
    "category": sa.String(),
}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("products")}

    for column_name, column_type in PRODUCT_COLUMNS.items():
        if column_name not in existing_columns:
            op.add_column("products", sa.Column(column_name, column_type, nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("products")}

    for column_name in PRODUCT_COLUMNS:
        if column_name in existing_columns:
            op.drop_column("products", column_name)
