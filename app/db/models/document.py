from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # 反向关系（可选但建议加）
    chunks: Mapped[list["Chunk"]] = relationship(  # noqa: F821 - SQLAlchemy forward ref
        back_populates="document",
        cascade="all, delete-orphan"
    )