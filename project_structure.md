ai-copilot/
├── app/
│   ├── __init__.py
│   ├── main.py                # create_app 入口
│   │
│   ├── core/                 # 核心配置
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── document.py
│   │       └── chunk.py
│   │
│   ├── schemas/              # Pydantic
│   │   ├── chat.py
│   │   ├── document.py
│   │   └── common.py
│   │
│   ├── services/             # 业务核心（重点）
│   │   ├── rag/
│   │   │   ├── retriever.py
│   │   │   ├── embedding.py
│   │   │   └── generator.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── file_parser.py
│   │   │   ├── url_loader.py
│   │   │   └── chunker.py
│   │   │
│   │   ├── llm/
│   │   │   └── minimax.py
│   │   │
│   │   └── cache/
│   │       └── redis_cache.py
│   │
│   ├── tasks/                # Celery
│   │   ├── worker.py
│   │   └── ingestion_task.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── chat.py
│   │       ├── upload.py
│   │       └── url.py
│   │
│   └── utils/
│       ├── text.py
│       └── time.py
│
├── alembic/
├── .env
├── pyproject.toml
├── ruff.toml
└── README.md
