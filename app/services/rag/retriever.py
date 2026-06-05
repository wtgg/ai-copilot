from sqlalchemy import select

from app.db.models import Chunk
from app.db.session import async_session_maker


class Retriever:
    async def search(self, embedding: list[float], top_k: int = 3) -> list[str]:
        # 用 ORM column 的 cosine_distance,SQLAlchemy 会自动把 list 序列化成 pgvector 字符串
        # 等价 raw SQL: SELECT content FROM chunks ORDER BY embedding <=> :emb LIMIT :k
        stmt = (
            select(Chunk.content)
            .order_by(Chunk.embedding.cosine_distance(embedding))
            .limit(top_k)
        )

        async with async_session_maker() as session:
            result = await session.execute(stmt)
            return [row[0] for row in result.scalars().all()]