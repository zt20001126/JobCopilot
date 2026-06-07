"""enforce generation metadata constraints

Revision ID: 20260607_0002
Revises: 20260607_0001
Create Date: 2026-06-07
"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "20260607_0002"
down_revision: Union[str, Sequence[str], None] = "20260607_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            "SELECT id FROM generation_record "
            "WHERE request_id IS NULL OR request_id = ''",
        ),
    )
    for row in rows:
        bind.execute(
            sa.text(
                "UPDATE generation_record "
                "SET request_id = :request_id WHERE id = :id",
            ),
            {"request_id": str(uuid4()), "id": row.id},
        )

    bind.execute(
        sa.text(
            "UPDATE generation_record SET platform = 'boss' "
            "WHERE platform IS NULL OR platform = ''",
        ),
    )
    with op.batch_alter_table("generation_record") as batch_op:
        batch_op.alter_column(
            "request_id",
            existing_type=sa.String(36),
            nullable=False,
        )
        batch_op.alter_column(
            "platform",
            existing_type=sa.String(30),
            nullable=False,
            server_default=None,
        )


def downgrade() -> None:
    with op.batch_alter_table("generation_record") as batch_op:
        batch_op.alter_column(
            "platform",
            existing_type=sa.String(30),
            nullable=True,
            server_default="boss",
        )
        batch_op.alter_column(
            "request_id",
            existing_type=sa.String(36),
            nullable=True,
        )
