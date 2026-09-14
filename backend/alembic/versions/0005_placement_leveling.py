"""placement tests + student points/leveling columns

Revision ID: 0005_placement_leveling
Revises: 0004_multi_tenant_foundation
Create Date: 2026-09-14 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PGEnum


revision = "0005_placement_leveling"
down_revision = "0004_multi_tenant_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("students", sa.Column("points", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("students", sa.Column("placement_completed_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "placement_tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_placement_tests_organization_id"), "placement_tests", ["organization_id"], unique=False)

    op.create_table(
        "placement_test_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("placement_test_id", sa.Integer(), sa.ForeignKey("placement_tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column(
            "type",
            PGEnum("multiple_choice", "short_answer", "true_false", name="questiontypeenum", create_type=False),
            nullable=False,
        ),
        sa.Column("metadata", sa.JSON(), nullable=True),
    )
    op.create_index(
        op.f("ix_placement_test_questions_placement_test_id"),
        "placement_test_questions",
        ["placement_test_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_placement_test_questions_placement_test_id"), table_name="placement_test_questions")
    op.drop_table("placement_test_questions")
    op.drop_index(op.f("ix_placement_tests_organization_id"), table_name="placement_tests")
    op.drop_table("placement_tests")
    op.drop_column("students", "placement_completed_at")
    op.drop_column("students", "points")
