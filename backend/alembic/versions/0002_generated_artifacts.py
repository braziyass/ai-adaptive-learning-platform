"""add generated artifacts table

Revision ID: 0002_generated_artifacts
Revises: 0001_initial_schema
Create Date: 2026-07-14 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0002_generated_artifacts"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "generated_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("artifact_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("chapter_id", sa.Integer(), nullable=True),
        sa.Column("lesson_id", sa.Integer(), nullable=True),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("source_chunks", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_generated_artifacts_artifact_type"), "generated_artifacts", ["artifact_type"], unique=False)
    op.create_index(op.f("ix_generated_artifacts_course_id"), "generated_artifacts", ["course_id"], unique=False)
    op.create_index(op.f("ix_generated_artifacts_chapter_id"), "generated_artifacts", ["chapter_id"], unique=False)
    op.create_index(op.f("ix_generated_artifacts_lesson_id"), "generated_artifacts", ["lesson_id"], unique=False)
    op.create_index(op.f("ix_generated_artifacts_level"), "generated_artifacts", ["level"], unique=False)
    op.create_index(op.f("ix_generated_artifacts_student_id"), "generated_artifacts", ["student_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_generated_artifacts_student_id"), table_name="generated_artifacts")
    op.drop_index(op.f("ix_generated_artifacts_level"), table_name="generated_artifacts")
    op.drop_index(op.f("ix_generated_artifacts_lesson_id"), table_name="generated_artifacts")
    op.drop_index(op.f("ix_generated_artifacts_chapter_id"), table_name="generated_artifacts")
    op.drop_index(op.f("ix_generated_artifacts_course_id"), table_name="generated_artifacts")
    op.drop_index(op.f("ix_generated_artifacts_artifact_type"), table_name="generated_artifacts")
    op.drop_table("generated_artifacts")