# AI Copilot 🚀

一个基于 **FastAPI + PostgreSQL(pgvector) + LLM** 构建的 AI Copilot 系统，支持：

* 🤖 智能对话（RAG，端到端已跑通）
* 📄 文件上传自动解析与向量化（PDF / TXT）
* 🌐 URL 内容抓取与入库（P1，待实现）
* 🧠 知识库增强问答（pgvector cosine 检索）
* ⚙️ 可扩展 Agent 架构（P2，待实现）

---

# 🧭 项目目标

本项目旨在实现一个类似「豆包 / ChatGPT」的 AI 助手系统，具备：

* 对话能力（LLM）
* 知识增强（RAG）
* 自动数据处理（Ingestion Pipeline）
* 后续可扩展为 Agent / 自动化系统

👉 不只是 Demo，而是一个**可扩展为产品**的工程项目。

---

# 🧱 技术架构

```mermaid
flowchart TD
    User --> API
    API --> ChatAPI["POST /v1/chat"]
    API --> UploadAPI["POST /v1/upload"]
    API --> URLAPI["POST /v1/url (P1)"]

    UploadAPI --> IngestionService
    URLAPI -.-> IngestionService
    IngestionService --> Chunker
    IngestionService --> Embedding
    IngestionService --> DB[(PostgreSQL + pgvector)]

    ChatAPI --> Embedding
    ChatAPI --> Retriever
    Retriever --> DB
    ChatAPI --> RAGService
    RAGService --> LLM[MiniMax M3]
    RAGService -.cache.-> Redis[(Redis)]
```

---

# 🧪 技术栈

## 后端

* FastAPI（异步）
* SQLAlchemy 2.x（Async，asyncpg 驱动）
* PostgreSQL + pgvector（向量数据库，ivfflat 索引）
* Redis（已配 `REDIS_URL`，缓存模块 P1 启用）
* Celery（依赖已装，worker P1 启动）

## AI

* LLM：MiniMax M3（OpenAI 兼容接口 `https://api.minimaxi.com/v1/text/chat`）
* Embedding：bge-m3（sentence-transformers，1024 维）
* `LLM_MOCK` 开关：本地/离线/CI 跑端到端

## 工程

* uv（依赖管理，Python 3.11）
* ruff（代码规范，line-length 100）
* loguru（日志，控制台 + 日切文件）
* pydantic v2 + pydantic-settings
* alembic（迁移走 psycopg2 同步，runtime asyncpg）

---

# 📁 项目结构

> 实际布局以 `PROJECT_CONTEXT.md` 第四章节为准，下面是精简版。

```text
app/
├── main.py                       # create_app() 入口
├── api/
│   ├── deps.py                   # get_db 依赖注入
│   ├── __init__.py               # 聚合 v1 router
│   └── v1/
│       ├── chat.py               # POST /v1/chat
│       ├── upload.py             # POST /v1/upload
│       └── url.py                # 占位 (P1)
├── core/
│   ├── config.py                 # Settings (DB / Redis / LLM_MOCK ...)
│   ├── logger.py                 # loguru 初始化
│   └── security.py               # 占位 (P2)
├── db/
│   ├── base.py
│   ├── session.py                # async engine + async_sessionmaker
│   └── models/
│       ├── document.py
│       └── chunk.py
├── schemas/
│   ├── chat.py
│   ├── common.py                 # 占位
│   └── document.py               # 占位
├── services/
│   ├── ingestion/
│   │   ├── chunker.py            # 500/50 滑窗
│   │   ├── file_parser.py        # PDF + TXT
│   │   ├── ingestion_service.py
│   │   └── url_loader.py         # 占位 (P1)
│   ├── rag/
│   │   ├── embedding.py          # bge-m3 lazy 单例
│   │   ├── retriever.py          # pgvector cosine_distance
│   │   └── generator.py          # RAGService
│   ├── llm/
│   │   └── minimax.py            # httpx async client
│   └── cache/
│       └── redis_cache.py        # 占位 (P1)
├── tasks/                        # Celery 占位 (P1)
└── utils/
    ├── text.py                   # 占位
    └── time_util.py              # now_cst() 东八区
```

---

# 🧪 技术栈

## 后端

* FastAPI（异步）
* SQLAlchemy 2.x（Async）
* PostgreSQL + pgvector（向量数据库）
* Redis（缓存，预留）
* Celery（异步任务，预留）

## AI

* LLM：MiniMax M3（OpenAI兼容接口）
* Embedding：bge-m3（sentence-transformers）

## 工程

* uv（依赖管理）
* ruff（代码规范）
* loguru（日志）
* pydantic v2（数据校验）
* alembic（数据库迁移）

---

# 📁 项目结构

```text
app/
├── api/
│   ├── deps.py
│   └── v1/
│       ├── chat.py
│       ├── upload.py
│       └── url.py
├── core/
│   ├── config.py
│   ├── logger.py
├── db/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── document.py
│       └── chunk.py
├── services/
│   ├── ingestion/
│   │   ├── chunker.py
│   │   └── file_parser.py
│   ├── rag/
│   │   ├── embedding.py
│   │   ├── retriever.py
│   │   └── generator.py
│   └── llm/
│       └── minimax.py
```

---

# ⚙️ 环境准备

## 1️⃣ 安装依赖

```bash
uv venv
source .venv/bin/activate
uv sync
```

---

## 2️⃣ 配置环境变量

`.env` 模板（参考 `.env.example`）：

```env
DATABASE_URL=postgresql+asyncpg://postgre:postgre@127.0.0.1:5432/ai_copilot
REDIS_URL=redis://:redis_root@127.0.0.1:6379/0
HF_ENDPOINT=https://hf-mirror.com
MINIMAX_API_KEY=sk-your-key
DB_ECHO=False
LLM_MOCK=False
```

* `LLM_MOCK=true` → LLM 不发请求，返回 mock，方便离线调试
* `DB_ECHO=True` → 打印 SQL（开发期用）

---

## 3️⃣ PostgreSQL + pgvector

确保目标数据库已启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

⚠️ 必须在目标数据库（如 `ai_copilot`）执行，extension 是 database 级

---

## 4️⃣ 数据库迁移

```bash
# 已有两次迁移,直接 upgrade
uv run alembic upgrade head

# 之后修改 model 时:
uv run alembic revision --autogenerate -m "your_message"
uv run alembic upgrade head
```

---

# 🚀 启动项目

```bash
uv run uvicorn app.main:app --reload
```

访问：

👉 http://127.0.0.1:8000/docs

快速验证（开 `LLM_MOCK=true` 跑端到端）：

```bash
# 1. 上传一个文件
curl -F "file=@README.md" http://127.0.0.1:8000/v1/upload

# 2. 提问
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"这个项目是干什么的?"}'
```

---

# 🧠 核心模块说明

## 1️⃣ Ingestion Pipeline

```text
文件
→ parse_file (PDF / TXT)
→ chunk_text (500/50 滑窗)
→ aembed_texts
→ IngestionService 写库
```

支持：

* ✅ PDF（pypdf）
* ✅ TXT
* ⏳ docx（python-docx 已装，P1 接入）
* ⏳ URL（url_loader 占位，P1 实现）
* ⏳ md（可走 TXT 分支，P1 可单独处理）

---

## 2️⃣ Embedding

* 模型：bge-m3，1024 维
* 入口：`get_default_embedding_service()`（**模块级 lazy 单例**）
* async 包装：`run_in_executor`，避免阻塞 event loop
* ⚠️ 首次加载约 80s（torch 66s + 权重 14s）

---

## 3️⃣ 向量存储

* PostgreSQL + pgvector，`VECTOR(1024)`
* ivfflat 索引（`lists=100`，`vector_cosine_ops`）
* ⚠️ 1k 行以内 ivfflat 召回反而比暴力差，P1 阶段视数据量决定是否换 hnsw / 删除

---

## 4️⃣ RAG 流程

```text
用户问题
→ aembed_query
→ retriever.search(embedding, top_k=3)   # pgvector cosine
→ RAGService.generate(query, docs)        # 拼 prompt
→ MiniMaxLLM.chat()                       # httpx async
→ 答案
```

---

# ⚠️ 已踩坑记录（重要）

### ❌ pgvector 不生效

原因：没有在当前数据库启用扩展

---

### ❌ Alembic async 报错

解决：

* migration 用 psycopg2（同步）
* runtime 用 asyncpg（异步）

---

### ❌ ImportError: async_session

原因：错误使用 session

正确方式：

```python
async_sessionmaker
```

---

### ❌ embedding 重复加载

解决：

* 用 `get_default_embedding_service()` 走单例入口，不要在别处 `EmbeddingService()`

---

### ❌ naive datetime 落库差 8 小时

原因：旧迁移 `DateTime()` 无时区，PG 按 session timezone 解释

解决：

* 模型 `default=now_cst`（`app/utils/time_util.py`）
* 迁移 `d4e5f6a7b8c9` 改 `timestamptz`，旧数据用 `AT TIME ZONE 'UTC'` 转换

---

# 📌 当前进度

## ✅ P0（核心 RAG）

* [x] 数据库建模 + 2 次迁移（init + filename/timestamptz）
* [x] pgvector + ivfflat 索引
* [x] bge-m3 Embedding（lazy 单例 + async 包装）
* [x] Chunker
* [x] Ingestion pipeline（PDF + TXT）
* [x] Retriever（pgvector cosine）
* [x] Chat API（端到端 RAG）
* [x] MiniMaxLLM + LLM_MOCK

## ✅ 工程

* [x] 全异步架构
* [x] 东八区时间统一
* [x] Loguru 控制台 + 日切文件

---

# 🚧 待开发

## 🔥 P1

* [ ] URL ingestion（`url_loader.py` + `POST /v1/url`）
* [ ] file_parser 加 docx / md
* [ ] Redis 缓存（embedding + 检索结果）
* [ ] Celery 异步 ingestion + `GET /v1/tasks/{id}`
* [ ] Chunker 升级（RecursiveCharacterTextSplitter）

## 🔥 P2

* [ ] Agent（任务识别 + 工具路由）
* [ ] 多轮对话 memory
* [ ] 鉴权（`core/security.py`，JWT 或 API Key）
* [ ] Web UI
* [ ] 可观测性（请求 ID / 慢查询 / 慢 LLM）

详见 `PROJECT_CONTEXT.md` 第十章。

---

# 🧩 设计原则

* 全异步优先（embedding 走 `run_in_executor`）
* Session 写库链路走 `Depends(get_db)`；retriever 内部自管 session 是历史味道，P1 改造
* Service 层不依赖框架（FastAPI / Celery 只在 api/tasks 边界出现）
* 模块解耦（RAG / ingestion / LLM / cache 各自独立）
* 可扩展为生产系统

---

# 🎯 项目定位

这是一个：

✔ 可运行的 AI 项目
✔ 可用于技术面试讲解
✔ 可扩展为 SaaS 产品
✔ 支持个人开发者商业化

---

# 🤝 后续规划

* Web UI（类似 ChatGPT）
* 多用户系统 + 知识库管理
* Agent 自动化任务
* 私有部署版本
* 结构化日志 / 监控

---

# 📄 License

MIT License


