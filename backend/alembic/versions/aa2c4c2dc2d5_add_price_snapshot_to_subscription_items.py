"""add price snapshot to subscription_items

Revision ID: aa2c4c2dc2d5
Revises: <PUT_V1_REVISION_ID_HERE>
Create Date: 2025-12-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "aa2c4c2dc2d5"
down_revision = "20251226_000001"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column(
        "subscription_items",
        sa.Column("unit_amount", mysql.BIGINT(), nullable=False, server_default="0"),
    )
    op.add_column(
        "subscription_items",
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="THB"),
    )


def downgrade() -> None:
    op.drop_column("subscription_items", "currency")
    op.drop_column("subscription_items", "unit_amount")
