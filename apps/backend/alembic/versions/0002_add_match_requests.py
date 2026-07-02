"""add match requests

Revision ID: 0002_add_match_requests
Revises: 0001_initial_khudarchive
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_match_requests"
down_revision: str | None = "0001_initial_khudarchive"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_match_requests_user_id", "match_requests", ["user_id"])
    op.create_index("ix_match_requests_status", "match_requests", ["status"])
    op.create_table(
        "match_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("match_request_id", sa.String(36), sa.ForeignKey("match_requests.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_match_questions_match_request_id", "match_questions", ["match_request_id"])


def downgrade() -> None:
    op.drop_index("ix_match_questions_match_request_id", table_name="match_questions")
    op.drop_table("match_questions")
    op.drop_index("ix_match_requests_status", table_name="match_requests")
    op.drop_index("ix_match_requests_user_id", table_name="match_requests")
    op.drop_table("match_requests")
