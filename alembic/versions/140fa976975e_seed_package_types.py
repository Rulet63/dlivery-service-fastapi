"""seed package types

Revision ID: 140fa976975e
Revises: 68d8bc62a60f
Create Date: 2026-01-15 13:11:17.453299

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "140fa976975e"
down_revision: str | Sequence[str] | None = "68d8bc62a60f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    package_types = sa.table(
        "package_types",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )

    op.bulk_insert(
        package_types,
        [
            {"id": 1, "name": "одежда"},
            {"id": 2, "name": "электроника"},
            {"id": 3, "name": "разное"},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM package_types WHERE id IN (1, 2, 3)")
