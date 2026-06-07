"""initialize generation records with request metadata

Revision ID: 20260607_0001
Revises:
Create Date: 2026-06-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260607_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "generation_record" not in inspector.get_table_names():
        op.create_table(
            "generation_record",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("request_id", sa.String(length=36), nullable=False),
            sa.Column("user_id", sa.String(length=64), nullable=True),
            sa.Column("platform", sa.String(length=30), nullable=False),
            sa.Column("position_title", sa.String(length=200), nullable=False),
            sa.Column("job_description", sa.Text(), nullable=True),
            sa.Column("job_url", sa.Text(), nullable=True),
            sa.Column("generated_content", sa.Text(), nullable=False),
            sa.Column("prompt_version", sa.String(length=50), nullable=True),
            sa.Column("model_name", sa.String(length=100), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        columns = {
            column["name"] for column in inspector.get_columns("generation_record")
        }
        with op.batch_alter_table("generation_record") as batch_op:
            if "request_id" not in columns:
                batch_op.add_column(sa.Column("request_id", sa.String(36)))
            if "platform" not in columns:
                batch_op.add_column(
                    sa.Column("platform", sa.String(30), server_default="boss"),
                )
            if "prompt_version" not in columns:
                batch_op.add_column(sa.Column("prompt_version", sa.String(50)))
            if "model_name" not in columns:
                batch_op.add_column(sa.Column("model_name", sa.String(100)))

    inspector = sa.inspect(bind)
    indexes = {
        index["name"] for index in inspector.get_indexes("generation_record")
    }
    if "ix_generation_record_request_id" not in indexes:
        op.create_index(
            "ix_generation_record_request_id",
            "generation_record",
            ["request_id"],
            unique=True,
        )


def downgrade() -> None:
    op.drop_index(
        "ix_generation_record_request_id",
        table_name="generation_record",
    )
    with op.batch_alter_table("generation_record") as batch_op:
        batch_op.drop_column("model_name")
        batch_op.drop_column("prompt_version")
        batch_op.drop_column("platform")
        batch_op.drop_column("request_id")
