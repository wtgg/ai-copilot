import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Copilot"

    DATABASE_URL: str
    REDIS_URL: str

    MINIMAX_API_KEY: str
    DB_ECHO: bool = False

    HF_ENDPOINT: str = "https://hf-mirror.com"

    # =========================
    # 开发期开关
    # =========================
    # LLM_MOCK=true 时,MiniMaxLLM 不真发请求,返回固定 mock 答案
    # 用于本地/离线/CI 环境跑通端到端流程
    LLM_MOCK: bool = False

    @property
    def sync_database_url(self):
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")

    class Config:
        env_file = ".env"


settings = Settings()
os.environ["HF_ENDPOINT"] = settings.HF_ENDPOINT