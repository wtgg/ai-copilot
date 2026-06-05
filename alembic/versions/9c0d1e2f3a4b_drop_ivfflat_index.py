"""drop ivfflat index on chunks.embedding

ivfflat 在小数据上(<1k 行)不仅没用,还会扫不到任何 centroid,导致 retriever 返回空。
后续视数据量决定:
- 1k-100k 行: 换 hnsw
- >100k 行: 重建 ivfflat lists=sqrt(rows)
当前 26 行,直接走 Seq Scan 最简。

Revision ID: 9c0d1e2f3a4b
Revises: d4e5f6a7b8c9
Create Date: 2026-06-05 18:20:00.000000
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9c0d1e2f3a4b"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        "idx_chunks_embedding",
        table_name="chunks",
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.execute(
        "CREATE INDEX idx_chunks_embedding ON chunks "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
