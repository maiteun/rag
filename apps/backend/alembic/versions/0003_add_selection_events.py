"""add selection events

Revision ID: 0003_add_selection_events
Revises: 0002_add_match_requests
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_add_selection_events"
down_revision: str | None = "0002_add_match_requests"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "selection_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question_type", sa.String(50), nullable=True),
        sa.Column("job_description", sa.Text(), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=True),
        sa.Column("exposed_block_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("selected_block_id", sa.String(36), nullable=True),
        sa.Column("rejected_block_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("signals_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_selection_events_user_id", "selection_events", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_selection_events_user_id", table_name="selection_events")
    op.drop_table("selection_events")
