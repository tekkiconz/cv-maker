"""add timestamps to project entries

Revision ID: 106c875e5ebb
Revises: 34a634dca953
Create Date: 2026-05-01 03:53:03.967373

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "106c875e5ebb"
down_revision: str | None = "34a634dca953"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "project_entries",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.add_column(
        "project_entries",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )


def downgrade() -> None:
    op.drop_column("project_entries", "updated_at")
    op.drop_column("project_entries", "created_at")
