"""add capability facets to experiences

Revision ID: 0005_add_experience_facets
Revises: 0004_pgvector_embedding
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_add_experience_facets"
down_revision: str | None = "0004_pgvector_embedding"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "experiences",
        sa.Column("facets", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.alter_column("experiences", "facets", server_default=None)


def downgrade() -> None:
    op.drop_column("experiences", "facets")
