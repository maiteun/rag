"""initial KHU:DArchive schema

Revision ID: 0001_initial_khudarchive
Revises:
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_khudarchive"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("name", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "source_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("original_filename", sa.String(255)),
        sa.Column("external_url", sa.Text()),
        sa.Column("raw_text", sa.Text()),
        sa.Column("cleaned_text", sa.Text()),
        sa.Column("status", sa.String(50), nullable=False, server_default="uploaded"),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "experiences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("experience_type", sa.String(50)),
        sa.Column("organization", sa.String(255)),
        sa.Column("role", sa.String(255)),
        sa.Column("situation", sa.Text()),
        sa.Column("task", sa.Text()),
        sa.Column("action", sa.Text()),
        sa.Column("result", sa.Text()),
        sa.Column("learned", sa.Text()),
        sa.Column("skills", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("competencies", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("keywords", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("has_metric", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_role", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_result", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_conflict", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("has_learning", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("completeness_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "experience_sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("experience_id", sa.String(36), sa.ForeignKey("experiences.id"), nullable=False),
        sa.Column("source_document_id", sa.String(36), sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("source_span_start", sa.Integer()),
        sa.Column("source_span_end", sa.Integer()),
        sa.Column("source_excerpt", sa.Text()),
        sa.Column("extraction_confidence", sa.Numeric(5, 2)),
    )
    op.create_table(
        "experience_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("experience_id", sa.String(36), sa.ForeignKey("experiences.id")),
        sa.Column("source_document_id", sa.String(36), sa.ForeignKey("source_documents.id")),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("chunk_type", sa.String(50)),
        sa.Column("token_count", sa.Integer()),
        sa.Column("chunk_index", sa.Integer()),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("embedding", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "experience_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("experience_id", sa.String(36), sa.ForeignKey("experiences.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(50)),
        sa.Column("reason", sa.Text()),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("answer", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("experience_questions")
    op.drop_table("experience_chunks")
    op.drop_table("experience_sources")
    op.drop_table("experiences")
    op.drop_table("source_documents")
    op.drop_table("users")
