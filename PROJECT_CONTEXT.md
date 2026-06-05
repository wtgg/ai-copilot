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
* SQLAlchemy 2.x（Async，asyncpg 驱动）
* PostgreSQL + pgvector（向量数据库）
* Redis（已配 `REDIS_URL`，缓存模块占位未启用）
* Celery（依赖已装，worker 未启动）

### AI

* LLM：MiniMax M3（OpenAI 兼容接口 `https://api.minimaxi.com/v1/chat/completions`）
* Embedding：bge-m3（sentence-transformers，维度 1024）
* `LLM_MOCK` 开关：开发 / 离线 / CI 用，绕开真实 API

### 工程

* uv（包管理，Python 3.11）
* ruff（代码规范，line-length 100）
* loguru（日志，控制台 + `logs/app.log` 日切轮转）
* pydantic v2 + pydantic-settings（数据校验 / 配置）
* alembic（数据库迁移，迁移文件用 psycopg2 同步，runtime 用 asyncpg）

---

## 📁 四、当前项目结构

> 实际是 `app/api/v1/...`（不是 `endpoints/`），下面列出的都是已落地的文件。

```text
.
├── alembic
│     ├── env.py
│     ├── README
│     ├── script.py.mako
│     └── versions
│         ├── 665678e7c9c9_init.py
│         └── d4e5f6a7b8c9_rename_to_filename_and_cst.py
├── alembic.ini
├── app
│     ├── api
│     │     ├── deps.py                  # get_db 依赖注入
│     │     ├── __init__.py              # 聚合 v1 router 为 apis
│     │     └── v1
│     │         ├── __init__.py          # api_v1 = APIRouter(prefix='/v1')
│     │         ├── chat.py              # POST /v1/chat
│     │         ├── upload.py            # POST /v1/upload
│     │         └── url.py               # 占位 (P1)
│     ├── core
│     │     ├── config.py                # Settings (DATABASE_URL, REDIS_URL, LLM_MOCK, ...)
│     │     ├── __init__.py
│     │     ├── logger.py                # loguru 初始化
│     │     └── security.py              # 占位 (P2)
│     ├── db
│     │     ├── base.py                  # DeclarativeBase
│     │     ├── __init__.py
│     │     ├── models
│     │     │     ├── chunk.py           # pgvector VECTOR(1024) + ivfflat 索引
│     │     │     ├── document.py        # filename, created_at (timestamptz)
│     │     │     └── __init__.py
│     │     └── session.py               # async engine + async_sessionmaker
│     ├── __init__.py
│     ├── main.py                        # create_app() + include_router
│     ├── schemas
│     │     ├── chat.py                  # ChatRequest / ChatResponse
│     │     ├── common.py                # 占位
│     │     ├── document.py              # 占位
│     │     └── __init__.py
│     ├── services
│     │     ├── cache
│     │     │     ├── __init__.py
│     │     │     └── redis_cache.py     # 占位 (P1)
│     │     ├── ingestion
│     │     │     ├── chunker.py         # 滑窗 chunk (默认 500/50)
│     │     │     ├── file_parser.py     # PDF + TXT (P1 加 docx / md)
│     │     │     ├── ingestion_service.py
│     │     │     ├── __init__.py
│     │     │     └── url_loader.py      # 占位 (P1)
│     │     ├── __init__.py
│     │     ├── llm
│     │     │     ├── __init__.py
│     │     │     └── minimax.py         # MiniMaxLLM (httpx async)
│     │     └── rag
│     │         ├── embedding.py         # bge-m3 lazy 单例 + run_in_executor
│     │         ├── generator.py         # RAGService
│     │         ├── __init__.py
│     │         └── retriever.py         # pgvector cosine_distance
│     ├── tasks
│     │     ├── ingestion_task.py        # Celery 任务 stub (P1)
│     │     ├── __init__.py
│     │     └── worker.py                # 占位 (P1)
│     └── utils
│         ├── __init__.py
│         ├── text.py                    # 占位
│         └── time_util.py               # now_cst() 东八区
├── notes
│   ├── _check_pg.py
│   ├── _smoke_uvicorn.sh
│   ├── _time_embed.py
│   └── alembic_pgvector.md
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

* 使用 `async_sessionmaker`（`expire_on_commit=False`）
* 写入链路通过 FastAPI `Depends(get_db)` 注入（`IngestionService(db)` 模式）
* ⚠️ **当前 `Retriever` 内部自行 `async with async_session_maker()`**——属于历史味道，P1 改造为注入，避免请求级别 session 丢失导致的事务问题
* ❌ 不允许 service 在写库链路里私自创建 session

---

### 3️⃣ Embedding 设计

* 使用类变量单例（避免重复加载模型）
* 入口走 `get_default_embedding_service()`，**不要**自己在别处 `EmbeddingService()`
* 支持 async（`run_in_executor`，避免阻塞 event loop）
* 模型：bge-m3，维度 1024，`normalize_embeddings=True`

---

### 4️⃣ RAG Pipeline

**Ingestion（写入）**

```text
文件 / URL
→ 解析(parse_file / url_loader)
→ 切分(chunk_text, 500/50)
→ embedding(aembed_texts)
→ 入库(IngestionService + Document + Chunk)
```

**Chat（检索 + 生成）**

```text
query
→ aembed_query
→ retriever.search(embedding, top_k=3)        # pgvector cosine_distance
→ RAGService.generate(query, docs)            # 拼 prompt 调 MiniMaxLLM
→ answer
```

---

## 🧩 六、数据库设计（已完成）

### documents 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| filename | varchar(255) | 重命名自 `name`（见迁移 `d4e5f6a7b8c9`） |
| created_at | timestamptz | 统一为东八区，default=`now_cst()` |

关系：`Document 1—N Chunk`，`cascade="all, delete-orphan"`。

### chunks 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int PK | |
| content | text | |
| embedding | vector(1024) | bge-m3 输出 |
| document_id | int FK | `ondelete=CASCADE` |
| created_at | timestamptz | default=`now_cst()` |

### 索引

```python
Index(
    "idx_chunks_embedding",
    Chunk.embedding,
    postgresql_using="ivfflat",
    postgresql_with={"lists": 100},
    postgresql_ops={"embedding": "vector_cosine_ops"},
)
```

> ⚠️ 小数据量下 ivfflat 召回反而下降，生产前观察行数后再决定是否保留 / 换 hnsw。

### 迁移历史

* `665678e7c9c9_init` — 建表 + embedding 索引
* `d4e5f6a7b8c9_rename_to_filename_and_cst` — `name→filename`，两表 `created_at` 改 `timestamptz`（旧 naive UTC 数据用 `AT TIME ZONE 'UTC'` 转换）

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

### ❌ 5. naive datetime 被 PG 默默按本地时区落库

**症状**：写入后 `created_at` 时间和代码里的 `datetime.utcnow()` 对不上，差 8 小时

**根因**：旧 `init` 迁移用 `DateTime()`（无时区），PG 把它按 session timezone 解释；客户端是 UTC，库端是 CST（容器默认）

**解决**：

* 业务层统一 `app/utils/time_util.py:now_cst()`（`Asia/Shanghai` aware datetime）
* 迁移 `d4e5f6a7b8c9` 把两表 `created_at` 改 `DateTime(timezone=True)`，并用 `AT TIME ZONE 'UTC'` 把旧数据当成 UTC 再带时区
* 模型 `default=now_cst`（aware datetime 落 timestamptz 不会丢信息）

---

### ❌ 6. embedding 模型首次加载 80s+

**症状**：首次 `/v1/chat` 或 `/v1/upload` 慢到超时

**解决**：

* 入口统一 `get_default_embedding_service()`，避免重复 `EmbeddingService()` 各 new 一份
* 启动期有 `init` 段可考虑主动 warm-up（可选）

---

### ❌ 7. ivfflat 在小数据量召回反而下降

**症状**：1k 行以内 `idx_chunks_embedding` 比暴力 `ORDER BY ... LIMIT` 还差。26 行实测 seq/ivfflat 都 ~0.05ms,索引完全没用

**解决**：

* **本次**：迁移 `9c0d1e2f3a4b` 已 drop 索引,直接走 Seq Scan
* **1k~100k 行**：换 hnsw（probes 无需调,对小数据集也友好）
* **>100k 行**：重建 ivfflat `lists=sqrt(rows)`，或继续 hnsw

---

### ❌ 8. pgvector 解析 vector 字符串只接受 8 位精度

**症状**：`str(list[float])` 用 17 位 repr,直接当 vector 字面量被 PG 拒绝,retriever 静默返回 0 rows

**根因**：ORM 编译出 `chunks.embedding <=> '[-0.04715912789106369,...]'::vector`,string 解析失败

**解决**：`retriever.py` 手动 8 位精度序列化 + `CAST(:e AS vector)` 显式转

```python
emb_str = "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"
stmt = text("SELECT content FROM chunks ORDER BY embedding <=> CAST(:e AS vector) LIMIT :k")
```

---

### ❌ 9. minimax BASE_URL 写错导致 404

**症状**：`https://api.minimaxi.com/v1/text/chat` 返回 404，chat 端点 500

**根因**：minimax 没有这个 endpoint,真实路径是 OpenAI 兼容的 `/v1/chat/completions`（或自家命名 `/v1/text/chatcompletion_v2`）

**解决**：`app/services/llm/minimax.py:BASE_URL` 改为 `https://api.minimaxi.com/v1/chat/completions`

> ⚠️ 任何第三方 API 路径都要先用 httpx 5 秒验证,不能信文档

---

### ❌ 10. `threading.Lock` 重入死锁

**症状**：卡 30+ 分钟、Ctrl+C 杀不掉、pyinstrument "No samples"

**根因**：`get_default_embedding_service` 持锁 + `EmbeddingService.__init__` 持**同一**锁（不可重入）→ 永久阻塞。bge-m3 根本没开始加载

**解决**：`threading.Lock` → `threading.RLock`

**诊断信号**：

* 单进程快（绕开双重锁）vs 多线程慢（撞死锁）
* 进程不响应 Ctrl+C（主线程阻塞）
* pyinstrument 主线程无 sample

---

### ❌ 11. `.env` 是 CRLF 结尾

**症状**：用 `cut` / `awk` 读 .env 取 API key,header 末尾被加上 `\r`,httpx 报 `Illegal header value`

**根因**：`Settings()` pydantic 会 strip,但任何 shell 直接读 .env 的脚本都会踩

**解决**：`sed -i 's/\r$//' .env`，长期保持 LF

---

## 🚧 八、当前已完成

**P0 全部跑通**

* ✅ 数据库建模 + 3 次 alembic 迁移（init + filename/timestamptz + drop ivfflat）
* ✅ pgvector（无索引,小数据走 Seq Scan）
* ✅ bge-m3 Embedding（lazy 单例 + `run_in_executor` async 包装）
* ✅ Chunker（滑窗 500/50）
* ✅ File parser（PDF + TXT）
* ✅ IngestionService（写库 + 事务）
* ✅ Upload API `POST /v1/upload`
* ✅ Retriever（pgvector `cosine_distance` + top_k）
* ✅ RAG Generator（context 拼接 + MiniMax LLM）
* ✅ Chat API `POST /v1/chat`（query → embed → retrieve → generate 全链路）
* ✅ MiniMaxLLM 客户端 + `LLM_MOCK` 离线开关
* ✅ Loguru 控制台 + 日切日志
* ✅ 统一东八区时间（`app/utils/time_util.py:now_cst`）

**已知 stub（不影响 P0 跑通）**

* ⏳ `app/api/v1/url.py`、`url_loader.py`、`redis_cache.py`、`schemas/document.py`、`schemas/common.py`、`utils/text.py`、`core/security.py`、`tasks/worker.py` 为空
* ⏳ `tasks/ingestion_task.py` 是 `NotImplementedError` stub

---

## ❗ 九、当前未完成（重点任务）

### 🔥 P1

1. **URL ingestion**：实现 `url_loader.py`（httpx 抓 HTML → 抽取正文 → 复用 ingestion pipeline），补全 `POST /v1/url`
2. **File parser 增强**：`python-docx` 已装但未接入；可加 `.md` 解析
3. **Redis 缓存**：填充 `redis_cache.py`（query embedding、检索结果、热门 query 缓存），并在 chat/upload 链路里挂上
4. **Celery 异步 ingestion**：填 `tasks/ingestion_task.py` + `worker.py`，大文件 / URL 改成后台任务
5. **Chunker 升级**：当前是按字符滑窗，无语义边界；可加 `langchain-text-splitters` 的 RecursiveCharacterTextSplitter

### 🔥 P2

6. **Agent（任务识别）**：意图分类 + 工具路由（RAG / 计算 / 搜索）
7. **多轮对话 memory**：引入 conversation / message 表，retriever 拼接历史
8. **多租户 / 鉴权**：填 `core/security.py`（JWT 或 API Key）
9. **Web UI**：FastAPI 模板 / Next.js / Gradio 任选
10. **可观测性**：结构化日志、请求 ID、慢 SQL / 慢 LLM 监控

## 🧪 十、下一步开发任务（AI必须从这里接手）

> P0 已全部完成（见第八章），本节按 P1 优先级给出可执行子任务。

### 👉 Task 1：URL ingestion

* `app/services/ingestion/url_loader.py`：httpx 抓取 → BeautifulSoup / trafilatura 抽正文 → 返回纯文本
* `POST /v1/url`：`{url, optional tags}` → 走 `IngestionService` 同一条入库链路
* 失败处理：超时 / 非 2xx / 抽取后空内容，统一定义异常
* 验收：`curl -X POST .../v1/url -d '{"url":"..."}'` 后 `chunks` 表新增对应行

### 👉 Task 2：file_parser 增强

* `parse_docx(content)`：用 `python-docx` 抽 `paragraph.text`
* `parse_md(content)`：可选；可直接当 txt 处理
* `parse_file` 路由补全

### 👉 Task 3：Redis 缓存

* `redis_cache.py`：`get/set/ttl` 三件套；key 命名 `emb:{sha1(text)}`、`search:{sha1(query)}`
* `embedding.py`：`aembed_texts` 命中则直接返回
* `retriever.py`：可选，top_k 相同的 query 命中缓存的 `[(content, distance)]`
* 注意：service 仍保持 framework-free，依赖注入 client

### 👉 Task 4：Celery 异步 ingestion

* `app/tasks/worker.py`：`celery_app = Celery(...)` 配 Redis broker / backend
* `app/tasks/ingestion_task.py`：把 `IngestionService.ingest_file` 改成同步调用，wrapper 用 `asyncio.run` 或 `async_to_sync`
* `POST /v1/upload` 改为 `ingestion_task.delay(...)`，立刻返回 `task_id`
* 加一个 `GET /v1/tasks/{task_id}` 查状态

### 👉 Task 5：Chunker 升级（可选）

* 引 `langchain-text-splitters` 的 `RecursiveCharacterTextSplitter`
* 按段落 / 句子边界切，retriever 召回更准

### 通用要求

* 全程保持 async（embedding 仍走 `run_in_executor`）
* service 层不引入 FastAPI / Celery 依赖
* 每次新增迁移：`uv run alembic revision --autogenerate -m "..."` 后人工 review
* 关键链路加 loguru 日志（retriever hits、cache hit rate、LLM latency）

## 🧠 十一、代码风格要求

* 尽量 async
* service 层不依赖框架
* 避免重复代码
* 使用类型注解
* 保持结构清晰

---

## 🧩 十二、环境变量

`.env` 当前实际内容（参考 `.env.example`）：

```env
DATABASE_URL=postgresql+asyncpg://postgre:postgre@127.0.0.1:5432/ai_copilot
REDIS_URL=redis://:redis_root@127.0.0.1:6379/0
HF_ENDPOINT=https://hf-mirror.com
MINIMAX_API_KEY=sk-xxx
DB_ECHO=False
LLM_MOCK=False
```

字段说明：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | ✅ | runtime 用 asyncpg，alembic 在 `env.py` 内自动替换为 psycopg2 |
| `REDIS_URL` | ✅ | 缓存 +（P1 之后）Celery broker/backend |
| `HF_ENDPOINT` | | sentence-transformers 拉模型用，国内环境指 `https://hf-mirror.com` |
| `MINIMAX_API_KEY` | ✅ | MiniMax LLM 鉴权 |
| `DB_ECHO` | | 调试期打开，会打 SQL |
| `LLM_MOCK` | | `true` 时 LLM 返回 mock，方便离线 / CI 跑端到端 |

---

## 🚀 十三、目标（给 AI 的指令）

P0 已完成，AI 现在要：

1. 推进 P1（URL、docx、Redis、Celery、Chunker 升级），见第十章
2. 保证代码清晰、可扩展
3. 避免同步阻塞（embedding 仍走 `run_in_executor`）
4. 优先保证工程质量
5. 每次新增迁移都人工 review

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

1. **语言**：思考过程和输出一律使用中文
2. **诚实**：不知道 / 不确定 / 没能力的事要坦诚说明，必要时主动询问补充信息；严禁不懂装懂、瞎编乱造
3. **图表**：架构 / 流程图一律使用 **Mermaid**（默认）或 **PlantUML**；**严禁** ASCII 框图 / 文本字符拼的图
4. **技术栈偏好**：Python + uv + FastAPI；装第三方库用 `uv add` 或 `uv pip install`，不要用 `pip`
5. **环境**：开发在 WSL Ubuntu 24.04 上跑，Python 3.11，uv 0.11.x
6. **接口自测约定**：写完接口代码**不要**用 `curl` 自测；改用 `pytest` 写单元测试，或明确告诉用户去 `http://127.0.0.1:8000/docs` 自测并给出预期请求 / 响应

---

## 📑 十六、相关文档索引

| 文档 | 角色 | AI 接手时该看什么 |
| --- | --- | --- |
| `README.md` | 用户面入口 | 启动、cURL 例子、技术栈 |
| `PROJECT_CONTEXT.md`（本文件） | 架构 / 设计 / 踩坑 / 规则上下文 | 路线、原则、风格、坑 |
| `project_structure.md` | 真实目录树 | 文件落点 |
| `TODO.md` | **可勾选任务清单** | 下一个 issue 选哪个、看依赖、勾完成状态 |
| `notes/alembic_pgvector.md` | 历史踩坑 | Alembic + pgvector 排错 |

AI 接手任务的推荐流程：

1. 读本文件（一~十五章）
2. 读 `TODO.md`，定位下一个 `- [ ]`，看依赖
3. 按依赖开 git 分支（`feat/<task-id>-<slug>`），照 `TODO.md` 子任务勾选实现
4. **单测**优先（pytest + mock），不直接 curl
5. 完成后回到 `TODO.md` 勾 `- [x]`，并在 commit message 末尾写 `[#issue-id]`

