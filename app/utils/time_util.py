"""时间工具: 统一使用东八区(北京时间, UTC+8)。"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

# 东八区(北京时间)
CST = ZoneInfo("Asia/Shanghai")


def now_cst() -> datetime:
    """返回带东八区时区的当前时间(aware datetime)。

    用于:
    - SQLAlchemy 字段的 default
    - 业务层任何"当前时间"语义
    - 跨进程/跨主机一致, 不依赖系统本地时区设置
    """
    return datetime.now(CST)
