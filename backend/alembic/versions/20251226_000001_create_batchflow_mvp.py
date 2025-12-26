# alembic/versions/20251226_000001_create_batchflow_mvp.py
"""create batchflow mvp schema

Revision ID: 20251226_000001
Revises:
Create Date: 2025-12-26 00:00:01.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "20251226_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------
    # roles
    # -----------------------------
    op.create_table(
        "roles",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_roles_code"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )

    # -----------------------------
    # users
    # -----------------------------
    op.create_table(
        "users",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("is_active", mysql.TINYINT(1), nullable=False, server_default=sa.text("1")),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_users_public_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_users_is_active", "users", ["is_active"], unique=False)

    # -----------------------------
    # zones
    # -----------------------------
    op.create_table(
        "zones",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", mysql.TINYINT(1), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_zones_code"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_zones_is_active", "zones", ["is_active"], unique=False)

    # -----------------------------
    # addresses (FK -> users, zones)
    # -----------------------------
    op.create_table(
        "addresses",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=True),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("line1", sa.String(length=255), nullable=False),
        sa.Column("line2", sa.String(length=255), nullable=True),
        sa.Column("subdistrict", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("province", sa.String(length=100), nullable=False),
        sa.Column("postal_code", sa.String(length=20), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False, server_default=sa.text("'TH'")),
        sa.Column("zone_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("is_default", mysql.TINYINT(1), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_addresses_public_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_addresses_user_id"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], name="fk_addresses_zone_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_addresses_user_id_is_default", "addresses", ["user_id", "is_default"], unique=False)
    op.create_index("idx_addresses_zone_id", "addresses", ["zone_id"], unique=False)

    # -----------------------------
    # products
    # -----------------------------
    op.create_table(
        "products",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", mysql.TINYINT(1), nullable=False, server_default=sa.text("1")),
        sa.Column("deleted_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_products_public_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_products_is_active", "products", ["is_active"], unique=False)

    # -----------------------------
    # product_variants (FK -> products)
    # -----------------------------
    op.create_table(
        "product_variants",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("product_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_active", mysql.TINYINT(1), nullable=False, server_default=sa.text("1")),
        sa.Column("deleted_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_product_variants_public_id"),
        sa.UniqueConstraint("sku", name="uq_product_variants_sku"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_product_variants_product_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index(
        "idx_product_variants_product_id_is_active",
        "product_variants",
        ["product_id", "is_active"],
        unique=False,
    )

    # -----------------------------
    # inventory (PK/FK -> product_variants)
    # -----------------------------
    op.create_table(
        "inventory",
        sa.Column("variant_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("qty_on_hand", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("qty_reserved", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("variant_id"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], name="fk_inventory_variant_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )

    # -----------------------------
    # plans
    # -----------------------------
    op.create_table(
        "plans",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("interval_unit", mysql.ENUM("day", "week", "month", name="plans_interval_unit"), nullable=False),
        sa.Column("interval_count", mysql.SMALLINT(unsigned=True), nullable=False),
        sa.Column("is_active", mysql.TINYINT(1), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_plans_code"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_plans_is_active", "plans", ["is_active"], unique=False)

    # -----------------------------
    # subscriptions (FK -> users, plans, addresses)
    # -----------------------------
    op.create_table(
        "subscriptions",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("plan_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("status", mysql.TINYINT(unsigned=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("next_run_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default=sa.text("'Asia/Bangkok'")),
        sa.Column("default_address_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("paused_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("canceled_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("deleted_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_subscriptions_public_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_subscriptions_user_id"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], name="fk_subscriptions_plan_id"),
        sa.ForeignKeyConstraint(["default_address_id"], ["addresses.id"], name="fk_subscriptions_default_address_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_subscriptions_user_id_status", "subscriptions", ["user_id", "status"], unique=False)
    op.create_index("idx_subscriptions_status_next_run_date", "subscriptions", ["status", "next_run_date"], unique=False)
    op.create_index("idx_subscriptions_plan_id", "subscriptions", ["plan_id"], unique=False)
    op.create_index("idx_subscriptions_default_address_id", "subscriptions", ["default_address_id"], unique=False)

    # -----------------------------
    # subscription_items (FK -> subscriptions, product_variants)
    # -----------------------------
    op.create_table(
        "subscription_items",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("subscription_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("variant_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("is_active", mysql.TINYINT(1), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subscription_id",
            "variant_id",
            name="uq_subscription_items_subscription_id_variant_id",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            name="fk_subscription_items_subscription_id",
        ),
        sa.ForeignKeyConstraint(
            ["variant_id"],
            ["product_variants.id"],
            name="fk_subscription_items_variant_id",
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index(
        "idx_subscription_items_subscription_id_is_active",
        "subscription_items",
        ["subscription_id", "is_active"],
        unique=False,
    )
    op.create_index("idx_subscription_items_variant_id", "subscription_items", ["variant_id"], unique=False)

    # -----------------------------
    # orders (FK -> users, subscriptions, zones, addresses)
    # -----------------------------
    op.create_table(
        "orders",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("order_no", sa.String(length=32), nullable=False),
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("subscription_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("status", mysql.TINYINT(unsigned=True), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("zone_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("shipping_address_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'THB'")),
        sa.Column("subtotal_amount", mysql.BIGINT(), nullable=False, server_default=sa.text("0")),
        sa.Column("shipping_amount", mysql.BIGINT(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", mysql.BIGINT(), nullable=False, server_default=sa.text("0")),
        sa.Column("generated_key", sa.String(length=64), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_orders_public_id"),
        sa.UniqueConstraint("order_no", name="uq_orders_order_no"),
        sa.UniqueConstraint("generated_key", name="uq_orders_generated_key"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_orders_user_id"),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], name="fk_orders_subscription_id"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], name="fk_orders_zone_id"),
        sa.ForeignKeyConstraint(["shipping_address_id"], ["addresses.id"], name="fk_orders_shipping_address_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_orders_user_id_created_at", "orders", ["user_id", "created_at"], unique=False)
    op.create_index("idx_orders_subscription_id_delivery_date", "orders", ["subscription_id", "delivery_date"], unique=False)
    op.create_index("idx_orders_status_delivery_date", "orders", ["status", "delivery_date"], unique=False)
    op.create_index("idx_orders_delivery_date_zone_id", "orders", ["delivery_date", "zone_id"], unique=False)
    op.create_index("idx_orders_shipping_address_id", "orders", ["shipping_address_id"], unique=False)

    # -----------------------------
    # order_items (FK -> orders, product_variants)
    # -----------------------------
    op.create_table(
        "order_items",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("order_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("variant_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_amount", mysql.BIGINT(), nullable=False, server_default=sa.text("0")),
        sa.Column("line_total_amount", mysql.BIGINT(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", "variant_id", name="uq_order_items_order_id_variant_id"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name="fk_order_items_order_id"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], name="fk_order_items_variant_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_order_items_order_id", "order_items", ["order_id"], unique=False)
    op.create_index("idx_order_items_variant_id", "order_items", ["variant_id"], unique=False)

    # -----------------------------
    # delivery_batches (FK -> zones)
    # -----------------------------
    op.create_table(
        "delivery_batches",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("batch_code", sa.String(length=32), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("zone_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("cutoff_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("status", mysql.TINYINT(unsigned=True), nullable=False),
        sa.Column("locked_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("dispatched_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("completed_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_delivery_batches_public_id"),
        sa.UniqueConstraint("batch_code", name="uq_delivery_batches_batch_code"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], name="fk_delivery_batches_zone_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_delivery_batches_delivery_date_zone_id", "delivery_batches", ["delivery_date", "zone_id"], unique=False)
    op.create_index("idx_delivery_batches_status_cutoff_at", "delivery_batches", ["status", "cutoff_at"], unique=False)
    op.create_index("idx_delivery_batches_zone_id", "delivery_batches", ["zone_id"], unique=False)

    # -----------------------------
    # delivery_batch_orders (FK -> delivery_batches, orders)
    # -----------------------------
    op.create_table(
        "delivery_batch_orders",
        sa.Column("batch_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("order_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("batch_id", "order_id"),
        sa.ForeignKeyConstraint(["batch_id"], ["delivery_batches.id"], name="fk_delivery_batch_orders_batch_id"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name="fk_delivery_batch_orders_order_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_delivery_batch_orders_order_id", "delivery_batch_orders", ["order_id"], unique=False)

    # -----------------------------
    # payments (FK -> orders)
    # -----------------------------
    op.create_table(
        "payments",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("order_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("status", mysql.TINYINT(unsigned=True), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'THB'")),
        sa.Column("amount", mysql.BIGINT(), nullable=False),
        sa.Column("provider_ref", sa.String(length=100), nullable=True),
        sa.Column("idempotency_key", sa.String(length=80), nullable=True),
        sa.Column("paid_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("failed_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_payments_public_id"),
        sa.UniqueConstraint("provider", "provider_ref", name="uq_payments_provider_provider_ref"),
        sa.UniqueConstraint("idempotency_key", name="uq_payments_idempotency_key"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name="fk_payments_order_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_payments_order_id", "payments", ["order_id"], unique=False)
    op.create_index("idx_payments_status_created_at", "payments", ["status", "created_at"], unique=False)
    op.create_index("idx_payments_provider_provider_ref_lookup", "payments", ["provider", "provider_ref"], unique=False)

    # -----------------------------
    # payment_slips (FK -> payments, users)
    # -----------------------------
    op.create_table(
        "payment_slips",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=26), nullable=True),
        sa.Column("payment_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("uploaded_by_user_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("verified_by_user_id", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("verified_at", mysql.DATETIME(fsp=3), nullable=True),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.Column("updated_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_payment_slips_public_id"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], name="fk_payment_slips_payment_id"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], name="fk_payment_slips_uploaded_by_user_id"),
        sa.ForeignKeyConstraint(["verified_by_user_id"], ["users.id"], name="fk_payment_slips_verified_by_user_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_payment_slips_payment_id", "payment_slips", ["payment_id"], unique=False)
    op.create_index("idx_payment_slips_verified_at", "payment_slips", ["verified_at"], unique=False)
    op.create_index("idx_payment_slips_uploaded_by_user_id", "payment_slips", ["uploaded_by_user_id"], unique=False)
    op.create_index("idx_payment_slips_verified_by_user_id", "payment_slips", ["verified_by_user_id"], unique=False)

    # -----------------------------
    # user_roles (FK -> users, roles) created last among auth-related
    # -----------------------------
    op.create_table(
        "user_roles",
        sa.Column("user_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("role_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("created_at", mysql.DATETIME(fsp=3), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_roles_user_id"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name="fk_user_roles_role_id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    op.create_index("idx_user_roles_role_id", "user_roles", ["role_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index("idx_user_roles_role_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index("idx_payment_slips_verified_by_user_id", table_name="payment_slips")
    op.drop_index("idx_payment_slips_uploaded_by_user_id", table_name="payment_slips")
    op.drop_index("idx_payment_slips_verified_at", table_name="payment_slips")
    op.drop_index("idx_payment_slips_payment_id", table_name="payment_slips")
    op.drop_table("payment_slips")

    op.drop_index("idx_payments_provider_provider_ref_lookup", table_name="payments")
    op.drop_index("idx_payments_status_created_at", table_name="payments")
    op.drop_index("idx_payments_order_id", table_name="payments")
    op.drop_table("payments")

    op.drop_index("idx_delivery_batch_orders_order_id", table_name="delivery_batch_orders")
    op.drop_table("delivery_batch_orders")

    op.drop_index("idx_delivery_batches_zone_id", table_name="delivery_batches")
    op.drop_index("idx_delivery_batches_status_cutoff_at", table_name="delivery_batches")
    op.drop_index("idx_delivery_batches_delivery_date_zone_id", table_name="delivery_batches")
    op.drop_table("delivery_batches")

    op.drop_index("idx_order_items_variant_id", table_name="order_items")
    op.drop_index("idx_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("idx_orders_shipping_address_id", table_name="orders")
    op.drop_index("idx_orders_delivery_date_zone_id", table_name="orders")
    op.drop_index("idx_orders_status_delivery_date", table_name="orders")
    op.drop_index("idx_orders_subscription_id_delivery_date", table_name="orders")
    op.drop_index("idx_orders_user_id_created_at", table_name="orders")
    op.drop_table("orders")

    op.drop_index("idx_subscription_items_variant_id", table_name="subscription_items")
    op.drop_index("idx_subscription_items_subscription_id_is_active", table_name="subscription_items")
    op.drop_table("subscription_items")

    op.drop_index("idx_subscriptions_default_address_id", table_name="subscriptions")
    op.drop_index("idx_subscriptions_plan_id", table_name="subscriptions")
    op.drop_index("idx_subscriptions_status_next_run_date", table_name="subscriptions")
    op.drop_index("idx_subscriptions_user_id_status", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("idx_plans_is_active", table_name="plans")
    op.drop_table("plans")

    op.drop_table("inventory")

    op.drop_index("idx_product_variants_product_id_is_active", table_name="product_variants")
    op.drop_table("product_variants")

    op.drop_index("idx_products_is_active", table_name="products")
    op.drop_table("products")

    op.drop_index("idx_addresses_zone_id", table_name="addresses")
    op.drop_index("idx_addresses_user_id_is_default", table_name="addresses")
    op.drop_table("addresses")

    op.drop_index("idx_zones_is_active", table_name="zones")
    op.drop_table("zones")

    op.drop_index("idx_users_is_active", table_name="users")
    op.drop_table("users")

    op.drop_table("roles")
