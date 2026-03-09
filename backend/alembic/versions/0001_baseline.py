"""baseline tables

Revision ID: 0001_baseline
Revises:
Create Date: 2026-03-01 00:00:00
"""

from alembic import op

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fake baseline migration: production schema already exists.
    # This revision only marks the current state in alembic_version.
    pass


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_index("ix_auth_sessions_telegram_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_created_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_code", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index("ix_user_profiles_user_id", table_name="user_profiles")
    op.drop_index("ix_user_profiles_id", table_name="user_profiles")
    op.drop_table("user_profiles")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_orders_id", table_name="orders")
    op.drop_table("orders")
