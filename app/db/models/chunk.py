from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.time_util import now_cst

if TYPE_CHECKING:
    from app.db.models.document import Document


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    content: Mapped[str] = mapped_column(Text)

    embedding: Mapped[list[float]] = mapped_column(Vector(1024))

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_cst
    )

    document: Mapped["Document"] = relationship(  # noqa: F821 - SQLAlchemy forward ref
        back_populates="chunks"
    )


# ⚠️ 向量索引(必须这样写,Alembic才识别)
Index(
    "idx_chunks_embedding",
    Chunk.embedding,
    postgresql_using="ivfflat",
    postgresql_with={"lists": 100},
    postgresql_ops={"embedding": "vector_cosine_ops"},
)