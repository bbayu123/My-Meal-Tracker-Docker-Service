"""Create brand and brand_aliases tables

Revision ID: 7b81e04f0c1b
Revises:
Create Date: 2026-07-23 07:21:26.705091

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b81e04f0c1b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    brands = op.create_table(
        "brands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "brand_aliases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alias", sa.String(), nullable=False),
        sa.Column("brand_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brands.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias"),
    )
    op.bulk_insert(brands, [{"id": uuid4(), "name": "Generic"}])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("brand_aliases")
    op.drop_table("brands")
