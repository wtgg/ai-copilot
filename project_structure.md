# 项目结构（与实际代码对齐）

> 真实路径以 `PROJECT_CONTEXT.md` 第四章为准。
> 历史版本里写的是 `app/api/endpoints/`，已经统一改为 `app/api/v1/`。

```text
ai-copilot/
├── app/
│   ├── __init__.py
│   ├── main.py                        # create_app() 入口
│   │
│   ├── core/                          # 核心配置
│   │   ├── config.py                  # Settings (DB / Redis / LLM_MOCK / ...)
│   │   ├── logger.py                  # loguru 初始化
│   │   └── security.py                # 占位 (P2 鉴权)
│   │
│   ├── db/
│   │   ├── base.py                    # DeclarativeBase
│   │   ├── session.py                 # async engine + async_sessionmaker
│   │   └── models/
│   │       ├── document.py            # filename, created_at (timestamptz)
│   │       └── chunk.py               # VECTOR(1024) + ivfflat 索引
│   │
│   ├── schemas/                       # Pydantic v2
│   │   ├── chat.py                    # ChatRequest / ChatResponse
│   │   ├── common.py                  # 占位
│   │   └── document.py                # 占位
│   │
│   ├── services/                      # 业务核心（不依赖框架）
│   │   ├── rag/
│   │   │   ├── embedding.py           # bge-m3 lazy 单例 + run_in_executor
│   │   │   ├── retriever.py           # pgvector cosine_distance
│   │   │   └── generator.py           # RAGService
│   │   │
│   │   ├── ingestion/
│   │   │   ├── file_parser.py         # PDF + TXT
│   │   │   ├── chunker.py             # 500/50 滑窗
│   │   │   ├── ingestion_service.py   # 写库主流程
│   │   │   └── url_loader.py          # 占位 (P1)
│   │   │
│   │   ├── llm/
│   │   │   └── minimax.py             # MiniMaxLLM (httpx async) + LLM_MOCK
│   │   │
│   │   └── cache/
│   │       └── redis_cache.py         # 占位 (P1)
│   │
│   ├── tasks/                         # Celery (P1)
│   │   ├── worker.py                  # 占位
│   │   └── ingestion_task.py          # NotImplementedError stub
│   │
│   ├── api/
│   │   ├── deps.py                    # get_db 依赖注入
│   │   ├── __init__.py                # 聚合 v1 router
│   │   └── v1/
│   │       ├── __init__.py            # api_v1 = APIRouter(prefix='/v1')
│   │       ├── chat.py                # POST /v1/chat
│   │       ├── upload.py              # POST /v1/upload
│   │       └── url.py                 # 占位 (P1)
│   │
│   └── utils/
│       ├── text.py                    # 占位
│       └── time_util.py               # now_cst() 东八区
│
├── alembic/                           # 迁移(同步 psycopg2)
│   ├── env.py
│   └── versions/
│       ├── 665678e7c9c9_init.py
│       └── d4e5f6a7b8c9_rename_to_filename_and_cst.py
├── alembic.ini
├── .env / .env.example
├── pyproject.toml
├── uv.lock
├── README.md
├── PROJECT_CONTEXT.md
└── project_structure.md
```

## 当前文件中 "空 / 占位" 的清单

不影响 P0 跑通，P1 / P2 阶段填：

| 文件 | 阶段 | 用途 |
| --- | --- | --- |
| `app/api/v1/url.py` | P1 | URL ingestion endpoint |
| `app/services/ingestion/url_loader.py` | P1 | httpx 抓 HTML + 抽正文 |
| `app/services/cache/redis_cache.py` | P1 | embedding / 检索结果缓存 |
| `app/tasks/worker.py` | P1 | Celery app 配置 |
| `app/tasks/ingestion_task.py` | P1 | 异步 ingestion 任务 |
| `app/utils/text.py` | P1/P2 | 文本预处理 |
| `app/schemas/document.py` | P1 | 文档相关的 Pydantic 模型 |
| `app/schemas/common.py` | 持续 | 通用响应/分页 |
| `app/core/security.py` | P2 | JWT / API Key 鉴权 |
