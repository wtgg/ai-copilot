"""P1 占位: Celery 接入后实现异步 ingestion 任务。

当前为 stub,函数被调用会直接抛 NotImplementedError,
避免在 P1 完工前出现"看起来能跑"的假实现。
"""
from app.services.rag.embedding import EmbeddingService

# 模块级单例保留(供 P1 实现时复用),不立即加载模型
embedding_service = EmbeddingService()


def process_file(file_path: str) -> None:  # noqa: ARG001 - 待 P1 实现
    """异步 ingestion 任务(P1 stub)。

    TODO(celery):
        - 读取 file_path 对应的文件 bytes
        - parse_file(filename, content) 解析
        - EmbeddingService.aembed_texts() 生成向量
        - 写入 PostgreSQL chunks 表
    """
    raise NotImplementedError(
        "ingestion_task.process_file 是 P1 stub,等 Celery 接入后实现"
    )