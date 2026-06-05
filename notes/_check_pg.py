"""临时 PG 连通性检查脚本(可删)"""
import asyncio
import asyncpg


async def check(label: str, dsn: str) -> None:
    try:
        conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=3)
        print(f"[OK]   {label}: {dsn}")
        await conn.close()
    except Exception as e:
        print(f"[FAIL] {label}: {type(e).__name__}: {e}")


async def main() -> None:
    # 用户 .env 里的两种可能写法
    await check("default db", "postgresql://postgre:postgre@127.0.0.1:5432/postgres")
    await check("ai_copilot db", "postgresql://postgre:postgre@127.0.0.1:5432/ai_copilot")


asyncio.run(main())
