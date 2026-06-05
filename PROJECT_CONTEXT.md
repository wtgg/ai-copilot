# AI Copilot 项目上下文文档（给 AI Coding 工具使用）

---

## 🧭 一、项目目标（核心）

本项目是一个 **AI Copilot 系统（RAG + Agent）**，目标是实现类似「豆包 / ChatGPT」的能力：

### 核心能力：

1. 对话系统（Chat UI）
2. 文件上传自动处理（RAG ingestion）
3. URL 自动解析入库
4. 向量检索（pgvector）
5. LLM 生成回答
6. 任务理解（Agent 雏形）

---

## 🧱 二、整体架构

```mermaid
flowchart TD
    User --> API
    API --> ChatService
    API --> UploadService

    UploadService --> Chunker
    UploadService --> Embedding
    UploadService --> DB[(PostgreSQL + pgvector)]

    ChatService --> Retriever
    Retriever --> DB
    ChatService --> LLM
```

---

## 🧪 三、当前技术栈（已确定）

### 后端

* FastAPI（异步）
* SQLAlchemy 2.x（Async）
* PostgreSQL + pgvector
* Redis（缓存，暂未 fully 使用）
* Celery（暂未接入）

### AI

* LLM：MiniMax M3（OpenAI 兼容接口）
* Embedding：bge-m3（sentence-transformers）

### 工程

* uv（包管理）
* ruff（代码规范）
* loguru（日志）
* pydantic v2（数据校验）
* alembic（数据库迁移）

---

## 📁 四、当前项目结构

```text
.
├── alembic
│     ├── env.py
│     ├── README
│     ├── script.py.mako
│     └── versions
│         └── 665678e7c9c9_init.py
├── alembic.ini
├── app
│     ├── api
│     │     ├── deps.py
│     │     ├── __init__.py
│     │     └── v1
│     │         ├── chat.py
│     │         ├── __init__.py
│     │         ├── upload.py
│     │         └── url.py
│     ├── core
│     │     ├── config.py
│     │     ├── __init__.py
│     │     ├── logger.py
│     │     └── security.py
│     ├── db
│     │     ├── base.py
│     │     ├── __init__.py
│     │     ├── models
│     │     │     ├── chunk.py
│     │     │     ├── document.py
│     │     │     └── __init__.py
│     │     └── session.py
│     ├── __init__.py
│     ├── main.py
│     ├── schemas
│     │     ├── chat.py
│     │     ├── common.py
│     │     ├── document.py
│     │     └── __init__.py
│     ├── services
│     │     ├── cache
│     │     │     ├── __init__.py
│     │     │     └── redis_cache.py
│     │     ├── ingestion
│     │     │     ├── chunker.py
│     │     │     ├── file_parser.py
│     │     │     ├── ingestion_service.py
│     │     │     ├── __init__.py
│     │     │     └── url_loader.py
│     │     ├── __init__.py
│     │     ├── llm
│     │     │     ├── __init__.py
│     │     │     └── minimax.py
│     │     └── rag
│     │         ├── embedding.py
│     │         ├── generator.py
│     │         ├── __init__.py
│     │         └── retriever.py
│     ├── tasks
│     │     ├── ingestion_task.py
│     │     ├── __init__.py
│     │     └── worker.py
│     └── utils
│         ├── __init__.py
│         ├── text.py
│         └── time_util.py
├── notes
│     └── alembic_pgvector.md
├── PROJECT_CONTEXT.md
├── project_structure.md
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## 🧠 五、核心设计原则（非常重要）

### 1️⃣ 全异步架构

* FastAPI async
* SQLAlchemy async
* embedding 使用线程池包装（因为模型是同步的）

---

### 2️⃣ Session 管理（必须遵守）

* 使用 `async_sessionmaker`
* 通过 FastAPI `Depends(get_db)` 注入
* ❌ 不允许 service 内部创建 session

---

### 3️⃣ Embedding 设计

* 使用类变量单例（避免重复加载模型）
* 支持 async（run_in_executor）

---

### 4️⃣ RAG Pipeline

```text
文件 → 解析 → 切分 → embedding → 入库
```

---

## 🧩 六、数据库设计（已完成）

### documents 表

* id
* filename
* content（可选）
* created_at

### chunks 表

* id
* content
* embedding (VECTOR)
* document_id（FK）

---

## ⚠️ 七、已踩过的坑（非常关键）

### ❌ 1. pgvector 未在当前数据库启用

解决：

```sql
CREATE EXTENSION vector;
```

必须在目标数据库执行（如 ai_copilot）

---

### ❌ 2. Alembic async 问题

解决：

* migration 使用 sync driver（psycopg2）
* runtime 使用 asyncpg

---

### ❌ 3. pgvector 类型未 import

迁移文件必须：

```python
from pgvector.sqlalchemy import Vector
```

---

### ❌ 4. async_session 不存在

正确：

```python
async_sessionmaker
```

---

## 🚧 八、当前已完成

✅ 数据库建模 + migration
✅ pgvector 正常工作
✅ embedding service（支持 async）
✅ chunker
✅ ingestion service（含 DB 写入）
✅ upload API（基础版，支持 PDF, Markdown, txt, docx）未完成

---

## ❗ 九、当前未完成（重点任务）

### 🔥 P0（必须完成）

1. Retriever（向量检索）

   * 使用 pgvector cosine distance
   * top-k 检索

2. Chat API 完整流程：

   * query → embedding
   * vector search
   * 拼接 context
   * 调用 LLM

---

### 🔥 P1

3. URL ingestion
4. PDF 解析增强
5. Redis 缓存 embedding / query

---

### 🔥 P2

6. Agent（任务识别）
7. 多轮对话 memory

---

## 🧪 十、下一步开发任务（AI必须从这里接手）

### 👉 Task 1：实现 Retriever

要求：

* 输入：query embedding
* 输出：最相关 chunks
* 使用 pgvector

---

### 👉 Task 2：实现 ChatService

流程：

```text
用户输入
→ embedding
→ 向量检索
→ 拼接上下文
→ 调用 LLM
→ 返回答案
```

---

### 👉 Task 3：完善 upload 接口

支持：

* PDF
* txt
* docx

---

## 🧠 十一、代码风格要求

* 尽量 async
* service 层不依赖框架
* 避免重复代码
* 使用类型注解
* 保持结构清晰

---

## 🧩 十二、环境变量

```env
DATABASE_URL=postgresql+asyncpg://postgre:postgre@127.0.0.1:5432/ai_copilot

HF_ENDPOINT=https://hf-mirror.com

MINIMAX_API_KEY=xxx
```

---

## 🚀 十三、目标（给 AI 的指令）

你需要：

1. 补全 Retriever
2. 实现完整 Chat RAG 流程
3. 保证代码清晰、可扩展
4. 避免同步阻塞
5. 优先保证工程质量

---

## 🧩 十四、最终目标（重要）

这是一个：

👉 **可用于面试的 AI 项目**
👉 **可扩展为 SaaS / 一人公司产品**

不是 demo，而是：

✔ 可运行
✔ 可讲清楚
✔ 有架构深度

---

## 🧩 十五、重要设定，需要AI始终遵守：

1. 你的思考过程和输出一律使用中文
2. 任何时候都应该诚实，对应不知道，不确定，没有能力的事要坦诚告知用户，或者进一步询问以获取更多信息，而不是不懂装懂，胡说八道，瞎编乱造，以免误导用户。

