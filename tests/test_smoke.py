"""烟雾测试:保证核心模块能 import 起来。

不连接数据库 / 加载模型 / 调 LLM,只验证语法和导入期错误。
"""
from __future__ import annotations


def test_app_imports():
    """主 app 能 import 起来,FastAPI 实例 title 正确。"""
    from app.main import app

    assert app.title == "AI Copilot"


def test_chat_module_imports():
    """chat endpoint 改完后还能 import(retriever 注入改造的回归网)。"""
    from app.api.v1 import chat  # noqa: F401

    assert hasattr(chat, "router")
    assert hasattr(chat, "retriever")
    assert hasattr(chat, "rag_service")


def test_retriever_search_signature_accepts_db():
    """Retriever.search 必须接受 db: AsyncSession 参数(Sprint 1 [#1] 契约)。"""
    import inspect

    from app.services.rag.retriever import Retriever

    sig = inspect.signature(Retriever.search)
    params = sig.parameters
    assert "db" in params, "Retriever.search 必须接受 db 参数"
    assert "embedding" in params, "Retriever.search 必须接受 embedding 参数"
    # db 应该是 AsyncSession 类型
    assert params["db"].annotation is not inspect.Parameter.empty
