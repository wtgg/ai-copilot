"""rename documents.name to filename, switch timestamps to timestamptz

Revision ID: d4e5f6a7b8c9
Revises: 665678e7c9c9
Create Date: 2026-06-05 10:55:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "665678e7c9c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. documents.name -> documents.filename (列重命名,数据保留)
    op.alter_column(
        "documents",
        "name",
        new_column_name="filename",
    )

    # 2. documents.created_at: timestamp -> timestamptz
    #    旧字段是 naive UTC(datetime.utcnow 写入),USING 子句告诉 PG 把它当 UTC
    op.alter_column(
        "documents",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )

    # 3. chunks.created_at: timestamp -> timestamptz
    op.alter_column(
        "chunks",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    op.alter_column(
        "chunks",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "documents",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "documents",
        "filename",
        new_column_name="name",
    )