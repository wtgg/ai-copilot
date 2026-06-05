from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class Retriever:
    """无状态 pgvector cosine 检索器。

    实例可全局复用（不持有连接 / 模型 / 缓存）；
    session 通过方法参数注入,与 FastAPI ``Depends(get_db)`` 保持一致写法。
    """

    async def search(
        self,
        embedding: list[float],
        db: AsyncSession,
        top_k: int = 3,
    ) -> list[str]:
        # pgvector 解析 vector 字符串只接受有限精度 (~8 位有效数字)。
        # Python str(list) 用 17 位 repr, 直接当 vector 字面量会被 PG 拒绝。
        # 必须 8 位精度 + 显式 CAST AS vector。
        emb_str = "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"

        stmt = text(
            """
            SELECT content FROM chunks
            ORDER BY embedding <=> CAST(:e AS vector)
            LIMIT :k
            """
        )
        result = await db.execute(stmt, {"e": emb_str, "k": top_k})
        # scalars().all() 已经把每行展开成标量(content 字符串),不要再 row[0]
        return list(result.scalars().all())
