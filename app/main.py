from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api import apis
from app.core.logger import init_logger


def _warmup_embedding() -> None:
    """启动期同步预热 bge-m3,绕过 run_in_executor 的不可控行为。

    单进程验证: 在 HF_HUB_OFFLINE=1 + 本地缓存完整的情况下,
    SentenceTransformer("BAAI/bge-m3") 加载 ~6.5s。
    lifespan 阶段 event loop 还没服务请求,同步阻塞 6.5s 完全可接受。
    """
    from app.services.rag.embedding import get_default_embedding_service

    logger.info("embedding warm-up starting...")
    get_default_embedding_service()
    logger.info("embedding warm-up done")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    _warmup_embedding()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="AI Copilot", lifespan=lifespan)
    app.include_router(apis)
    return app


app = create_app()
