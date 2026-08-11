"""add citations to ai_messages

Revision ID: d670265ba5d4
Revises: 536690d514ef
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d670265ba5d4"
down_revision: Union[str, Sequence[str], None] = "536690d514ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ai_messages",
        sa.Column(
            "citations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "ai_messages",
        "citations",
    )