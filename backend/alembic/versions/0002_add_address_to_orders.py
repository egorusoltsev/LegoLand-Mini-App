"""add address to orders

Revision ID: 0002_add_address_to_orders
Revises: 0001_baseline
Create Date: 2026-03-01 00:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_address_to_orders"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.add_column(sa.Column("address", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_column("address")
