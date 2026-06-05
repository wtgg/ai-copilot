"""Retriever 单元测试。

不连真实数据库, 用 AsyncMock 模拟 AsyncSession, 验证:
- 返回 top_k 条 content
- SQL 走 pgvector cosine_distance 排序 + CAST(:e AS vector)
- 注入的 db 没被打开/关闭(生命周期归调用方)
- embedding 必须转成 8 位精度 (17 位 repr 会被 pgvector 拒)
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag.retriever import Retriever


def _build_db_with_rows(rows: list[str]) -> AsyncMock:
    """构造一个能返回 rows 的 fake session。

    retriever 只调 1 次 db.execute (SELECT ... LIMIT :k)。
    scalars().all() 直接返回字符串 list(模拟 SQLAlchemy scalars 把 content 列展开)。
    """
    db = AsyncMock(spec=AsyncSession)
    select_result = MagicMock(
        scalars=MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=list(rows))),
        ),
    )
    db.execute = AsyncMock(return_value=select_result)
    return db


async def test_search_returns_contents_in_db_order():
    """retriever 应该按 db 返回的顺序把每行 content 取出来。"""
    retriever = Retriever()
    db = _build_db_with_rows(["chunk-1", "chunk-2", "chunk-3"])

    result = await retriever.search([0.1] * 1024, db, top_k=3)

    assert result == ["chunk-1", "chunk-2", "chunk-3"]
    db.execute.assert_awaited_once()


async def test_search_passes_top_k_as_bind_param():
    """SQL 里 LIMIT 必须绑定 top_k,不能硬编码。"""
    retriever = Retriever()
    db = _build_db_with_rows(["only-one"])

    await retriever.search([0.0] * 1024, db, top_k=1)

    select_call = db.execute.await_args
    params = select_call.args[1]
    assert params["k"] == 1


async def test_search_uses_cosine_distance_with_cast():
    """SQL 必须按 cosine_distance 升序,且 query 用 CAST AS vector。"""
    retriever = Retriever()
    db = _build_db_with_rows([])

    await retriever.search([0.0] * 1024, db, top_k=3)

    select_stmt = db.execute.await_args.args[0]
    sql_text = str(select_stmt)
    assert "<=>" in sql_text
    assert "CAST" in sql_text.upper()
    assert "AS VECTOR" in sql_text.upper()


async def test_search_serializes_embedding_to_8_digit_repr():
    """embedding 必须转成 8 位精度的 pgvector 字符串,不能用 str(list) 的 17 位 repr。"""
    retriever = Retriever()
    db = _build_db_with_rows([])

    emb = [0.123456789012345, -0.987654321098765] + [0.0] * 1022
    await retriever.search(emb, db, top_k=3)

    e_arg = db.execute.await_args.args[1]["e"]
    # 8 位精度截断后: 0.12345679 / -0.98765432
    assert "0.12345679" in e_arg
    assert "-0.98765432" in e_arg
    assert e_arg.startswith("[") and e_arg.endswith("]")


async def test_search_does_not_open_or_close_session():
    """session 的生命周期归调用方,retriever 不应介入。"""
    retriever = Retriever()
    db = _build_db_with_rows([])

    await retriever.search([0.0] * 1024, db)

    db.commit.assert_not_called()
    db.rollback.assert_not_called()
    db.close.assert_not_called()


async def test_search_passes_through_empty_table():
    """chunks 表为空时,返回空 list,不抛异常。"""
    retriever = Retriever()
    db = _build_db_with_rows([])

    result = await retriever.search([0.0] * 1024, db, top_k=3)

    assert result == []
