import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List


class EmbeddingService:
    """
    支持：
    - 单例模型（避免重复加载）
    - 同步 embedding
    - 异步 embedding（线程池）
    """

    _model = None
    _executor = ThreadPoolExecutor(max_workers=4)
    _lock = threading.Lock()

    def __init__(self):
        if EmbeddingService._model is None:
            with EmbeddingService._lock:
                if EmbeddingService._model is None:
                    from sentence_transformers import SentenceTransformer
                    EmbeddingService._model = SentenceTransformer("BAAI/bge-m3")

        self.model = EmbeddingService._model

    # =========================
    # 1️⃣ 同步 embedding（底层）
    # =========================
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    # =========================
    # 2️⃣ 异步 embedding（核心）
    # =========================
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            EmbeddingService._executor,
            self.embed_texts,
            texts,
        )

    async def aembed_query(self, text: str) -> List[float]:
        result = await self.aembed_texts([text])
        return result[0]


# =========================
# 全局 lazy 单例
# =========================
# 推荐入口: 所有需要 EmbeddingService 的地方都走 get_default_embedding_service(),
# 而不是自己 EmbeddingService()。避免在多个 module-level 各 new 一份 wrapper。
#
# 加载代价: 首次调用会触发 bge-m3 加载(~80s,torch 66s + 权重 14s),
# 后续调用 < 1ms。
_default_service: EmbeddingService | None = None


def get_default_embedding_service() -> EmbeddingService:
    """进程级 bge-m3 lazy 单例入口。"""
    global _default_service
    if _default_service is None:
        with EmbeddingService._lock:
            if _default_service is None:
                _default_service = EmbeddingService()
    return _default_service