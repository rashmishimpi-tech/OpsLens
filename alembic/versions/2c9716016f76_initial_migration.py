"""initial migration

Revision ID: 2c9716016f76
Revises:
Create Date: 2026-08-10 20:23:28.744905

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2c9716016f76"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
