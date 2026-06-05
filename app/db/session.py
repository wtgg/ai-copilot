from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# =========================
# 1️⃣ 创建 Async Engine
# =========================
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # 是否打印 SQL
    future=True,

    # -------- 高并发关键参数 --------
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 超出连接池的最大连接
    pool_pre_ping=True,     # 自动检测连接是否失效
    pool_recycle=1800,      # 连接回收（防止被 DB 断开）
)


# -------------------------
# 2️⃣ 创建 Session 工厂
# -------------------------
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,

    # -------- 关键配置 --------
    expire_on_commit=False,  # 防止提交后对象失效（非常重要）
    autoflush=False,         # 手动控制 flush
)


# =========================
# 3️⃣ 可选：手动获取 session（非 FastAPI 场景）
# =========================
async def get_async_session() -> AsyncSession:
    """
    用于非 FastAPI 场景（如 Celery / 脚本）
    """
    async with async_session_maker() as session:
        return session


# =========================
# 4️⃣ 可选：初始化 DB（一般不用）
# =========================
async def init_db() -> None:
    """
    手动建表（一般用 Alembic，不建议用这个）
    """
    from app.db.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)