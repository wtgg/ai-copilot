# AI Copilot 🚀

一个基于 **FastAPI + PostgreSQL(pgvector) + LLM** 构建的 AI Copilot 系统，支持：

* 🤖 智能对话（RAG）
* 📄 文件上传自动解析与向量化
* 🌐 URL 内容抓取与入库（规划中）
* 🧠 知识库增强问答
* ⚙️ 可扩展 Agent 架构

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

创建 `.env`：

```env
DATABASE_URL=postgresql+asyncpg://postgre:postgre@127.0.0.1:5432/ai_copilot

HF_ENDPOINT=https://hf-mirror.com

MINIMAX_API_KEY=your_api_key
```

---

## 3️⃣ PostgreSQL + pgvector

确保数据库已启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

⚠️ 必须在目标数据库（如 `ai_copilot`）执行

---

## 4️⃣ 数据库迁移

```bash
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```

---

# 🚀 启动项目

```bash
uv run uvicorn app.main:app --reload
```

访问：

👉 http://127.0.0.1:8000/docs

---

# 🧠 核心模块说明

## 1️⃣ Ingestion Pipeline

```text
文件 → 解析 → 切分 → embedding → 入库
```

支持：

* PDF
* TXT
* 后续支持 URL

---

## 2️⃣ Embedding

* 使用 bge-m3
* 单例加载（避免重复加载模型）
* 使用线程池实现 async

---

## 3️⃣ 向量存储

* PostgreSQL + pgvector
* embedding 存储在 VECTOR 字段
* 支持相似度检索（cosine）

---

## 4️⃣ RAG 流程

```text
用户问题
→ embedding
→ 向量检索
→ 拼接上下文
→ LLM生成回答
```

---

# ⚠️ 已踩坑记录（重要）

### ❌ pgvector 不生效

原因：没有在当前数据库启用扩展

---

### ❌ Alembic async 报错

解决：

* migration 使用 psycopg2（同步）
* 运行使用 asyncpg（异步）

---

### ❌ ImportError: async_session

原因：错误使用 session

正确方式：

```python
Depends(get_db)
```

---

### ❌ embedding 重复加载

解决：

* 使用类变量单例模式

---

# 📌 当前进度

✅ 数据库建模 + 迁移
✅ pgvector 正常使用
✅ embedding service（支持 async）
✅ chunker
✅ ingestion pipeline
✅ upload API（基础版）

---

# 🚧 待开发（重点）

## 🔥 P0

* [ ] Retriever（向量检索）
* [ ] Chat API（完整RAG流程）

## 🔥 P1

* [ ] URL ingestion
* [ ] PDF解析优化
* [ ] Redis缓存

## 🔥 P2

* [ ] Agent（任务识别）
* [ ] 多轮对话 memory

---

# 🧩 设计原则

* 全异步优先
* Session 统一由 FastAPI 管理
* Service 层不依赖框架
* 模块解耦（RAG / ingestion / LLM）
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
* 多用户系统
* 知识库管理
* Agent 自动化任务
* 私有部署版本

---

# 📄 License

MIT License


