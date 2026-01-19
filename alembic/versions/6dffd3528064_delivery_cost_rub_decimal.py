"""delivery_cost_rub decimal

Revision ID: 6dffd3528064
Revises: 140fa976975e
Create Date: 2026-01-19 18:17:46.298518
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6dffd3528064"
down_revision: str | Sequence[str] | None = "140fa976975e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE packages MODIFY COLUMN delivery_cost_rub DECIMAL(12,2) NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE packages MODIFY COLUMN delivery_cost_rub FLOAT NULL")
