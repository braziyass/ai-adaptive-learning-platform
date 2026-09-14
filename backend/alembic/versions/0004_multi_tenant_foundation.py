"""multi-tenant foundation: organizations, org scoping, audit log, platform_admin role

Revision ID: 0004_multi_tenant_foundation
Revises: 0003_refresh_tokens
Create Date: 2026-09-14 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0004_multi_tenant_foundation"
down_revision = "0003_refresh_tokens"
branch_labels = None
depends_on = None

DEFAULT_ORG_SLUG = "default"
DEFAULT_ORG_NAME = "Default Organization"


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("plan", sa.String(length=50), nullable=False, server_default="standard"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_organizations_slug"), "organizations", ["slug"], unique=True)

    org_table = sa.table(
        "organizations",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
    )
    op.bulk_insert(org_table, [{"id": 1, "name": DEFAULT_ORG_NAME, "slug": DEFAULT_ORG_SLUG}])
    op.execute("SELECT setval(pg_get_serial_sequence('organizations', 'id'), 1)")

    # New enum value for the platform-operator role. Not referenced by any
    # row written in this same migration, so it's safe inside the
    # transaction Alembic wraps this migration in (Postgres forbids using a
    # brand new enum value within the transaction that added it).
    op.execute("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'platform_admin'")

    for table_name in ("users", "courses", "generated_artifacts"):
        op.add_column(table_name, sa.Column("organization_id", sa.Integer(), nullable=True))
        op.execute(f"UPDATE {table_name} SET organization_id = 1")
        op.alter_column(table_name, "organization_id", nullable=False)
        op.create_foreign_key(
            f"fk_{table_name}_organization_id",
            table_name,
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_index(op.f(f"ix_{table_name}_organization_id"), table_name, ["organization_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_audit_logs_organization_id"), "audit_logs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_actor_user_id"), "audit_logs", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_organization_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    for table_name in ("generated_artifacts", "courses", "users"):
        op.drop_index(op.f(f"ix_{table_name}_organization_id"), table_name=table_name)
        op.drop_constraint(f"fk_{table_name}_organization_id", table_name, type_="foreignkey")
        op.drop_column(table_name, "organization_id")

    # Postgres cannot drop a single enum value; downgrading the role enum
    # would require recreating the type. Left as-is since no data can
    # reference 'platform_admin' after the column drops above.

    op.drop_index(op.f("ix_organizations_slug"), table_name="organizations")
    op.drop_table("organizations")
