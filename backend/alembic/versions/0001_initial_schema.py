"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-07-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String(length=150), nullable=False),
        sa.Column('last_name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('administrator', 'teacher', 'student', name='roleenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # courses, chapters, lessons, quizzes, questions
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
    )

    op.create_table(
        'chapters',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('order', sa.Integer, nullable=False),
    )

    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('chapter_id', sa.Integer, sa.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
    )

    op.create_table(
        'quizzes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lesson_id', sa.Integer, sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False, unique=True),
    )

    op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('quiz_id', sa.Integer, sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('type', sa.Enum('multiple_choice','short_answer','true_false', name='questiontypeenum'), nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
    )

    # users -> students, teachers
    op.create_table(
        'students',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('current_level', sa.Integer, nullable=False, server_default='1'),
        sa.Column('placement_score', sa.Integer, nullable=False, server_default='0'),
    )

    op.create_table(
        'teachers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
    )

    op.create_table(
        'student_progress',
        sa.Column('student_id', sa.Integer, sa.ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('lesson_id', sa.Integer, sa.ForeignKey('lessons.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('completed', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('score', sa.Integer, nullable=True),
        sa.Column('attempts', sa.Integer, nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_table('student_progress')
    op.drop_table('teachers')
    op.drop_table('students')
    op.drop_table('questions')
    op.drop_table('quizzes')
    op.drop_table('lessons')
    op.drop_table('chapters')
    op.drop_table('courses')
    op.drop_table('users')
    # drop enums
    op.execute('DROP TYPE IF EXISTS questiontypeenum')
    op.execute('DROP TYPE IF EXISTS roleenum')
