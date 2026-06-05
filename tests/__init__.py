"""Pytest 全局配置 / fixture。

约定:
- 默认所有 async test 都用 asyncio 跑（pyproject.toml 里 asyncio_mode = "auto"）
- 这里只放跨文件共享的 fixture
"""
from __future__ import annotations
