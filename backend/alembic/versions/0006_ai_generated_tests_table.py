"""add ai_generated_tests table (existing model had no migration; quiz/validation submission needs it)

Revision ID: 0006_ai_generated_tests_table
Revises: 0005_placement_leveling
Create Date: 2026-09-14 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0006_ai_generated_tests_table"
down_revision = "0005_placement_leveling"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_generated_tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id", ondelete="SET NULL"), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("test_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_ai_generated_tests_course_id"), "ai_generated_tests", ["course_id"], unique=False)
    op.create_index(op.f("ix_ai_generated_tests_student_id"), "ai_generated_tests", ["student_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_generated_tests_student_id"), table_name="ai_generated_tests")
    op.drop_index(op.f("ix_ai_generated_tests_course_id"), table_name="ai_generated_tests")
    op.drop_table("ai_generated_tests")
