"""add page_count to documents

Revision ID: 536690d514ef
Revises: dd04f597f95c
Create Date: 2026-08-10 14:52:18.662048
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "536690d514ef"
down_revision: Union[str, Sequence[str], None] = "dd04f597f95c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "page_count",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "documents",
        "page_count",
    )