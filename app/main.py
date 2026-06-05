from fastapi import FastAPI

from app.api import apis
from app.core.logger import init_logger


def create_app() -> FastAPI:
    app = FastAPI(title="AI Copilot")

    init_logger()

    app.include_router(apis)

    return app


app = create_app()
