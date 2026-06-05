# AI Copilot · 开发任务清单

> 详细路线见 `PROJECT_CONTEXT.md` 第十章；本文件是**可勾选 issue** 视图。
>
> 勾选语法：`- [x]` 完成 / `- [~]` 进行中 / `- [ ]` 未开始
>
> 状态图例：🔥 必做 ｜ ⭐ 推荐 ｜ 💡 可选

---

## 状态总览

| 模块 | P0 | P1 | P2 | 备注 |
| --- | --- | --- | --- | --- |
| 数据库 | ✅ | ⏳ | — | 已 2 次迁移 |
| Embedding | ✅ | 💡 warm-up | — | lazy 单例稳定 |
| Ingestion (PDF/TXT) | ✅ | — | — | |
| Ingestion (docx/md) | — | 🔥 | — | 依赖 Sprint 1 |
| URL ingestion | — | 🔥 | — | 依赖 docx |
| Upload API | ✅ | — | — | |
| Chat API | ✅ | — | — | 端到端跑通 |
| Retriever | ✅ | 🔧 注入改造 | — | 历史味道清理 |
| RAG Generator | ✅ | — | — | |
| LLM 客户端 | ✅ | — | — | LLM_MOCK 可用 |
| Redis 缓存 | — | 🔥 | — | 依赖 retriever 改造 |
| Celery 异步 | — | 🔥 | — | |
| Chunker | ✅ | 💡 升级 | — | 当前字符滑窗 |
| 向量索引 | ✅ | — | — | ivfflat 已删,1k+ 行换 hnsw |
| 鉴权 | — | — | 🔥 | P2 |
| Memory | — | — | 🔥 | P2 |
| Agent | — | — | ⭐ | P2 |
| Web UI | — | — | 💡 | P2 |
| 可观测性 | — | — | ⭐ | P2 |

---

## 🔧 Sprint 1 · 清理 + 内容扩展

### [#1] Retriever 注入改造 🔧 小重构

预估：0.5 天 ｜ 依赖：无

- [ ] `app/services/rag/retriever.py`：`Retriever.search()` 接收 `db: AsyncSession`（或 `__init__` 注入）
- [ ] `app/api/v1/chat.py`：用 `Depends(get_db)` 注入；去掉 `_db` 占位
- [ ] 单测：mock session，验证 top_k 和 SQL

**验收**：`curl -X POST .../v1/chat -d '{...}'` 行为不变；retriever 内部不再 `async with async_session_maker()`

---

### [#2] file_parser 增强 (docx / md) 🔥

预估：0.5 天 ｜ 依赖：无

- [ ] `app/services/ingestion/file_parser.py:parse_docx()`：`python-docx` 抽 `paragraph.text`，段间 `\n`
- [ ] `app/services/ingestion/file_parser.py:parse_md()`：先走 TXT 分支；后续可加 `markdown` 包结构化
- [ ] `parse_file()` 路由表补全 `.docx` / `.md` / `.markdown`
- [ ] 抛 `UnsupportedFileType` 自定义异常（在 `app/utils/exceptions.py`）
- [ ] 单测：上传 `.docx`、`.md` 文件，验证 chunks 入库

**验收**：curl 上传 `.docx` / `.md`，`chunks` 表新增对应行

---

### [#3] URL ingestion 🔥

预估：1 天 ｜ 依赖：[#2]

- [ ] `pyproject.toml` 加 `trafilatura`（或 `readability-lxml`）：`uv add trafilatura`
- [ ] `app/services/ingestion/url_loader.py`：`async fetch_url(url: str) -> str`
  - [ ] httpx 10s 超时，自定义 UA，follow_redirects
  - [ ] `trafilatura.extract(html, include_comments=False, include_tables=False)` 抽正文
  - [ ] 抽不到正文 → 抛 `EmptyContentError`
- [ ] `app/schemas/document.py`：`UrlIngestRequest(url, tags?)`
- [ ] `app/api/v1/url.py`：`POST /v1/url`，复用 `IngestionService` 写库
- [ ] 异常映射：超时→504 / 非 2xx→502 / 空内容→422
- [ ] 简单 SSRF 防护：拒绝 `localhost` / `127.0.0.1` / 私网 IP（生产前再强化）
- [ ] 单测：mock httpx 返回 fixture HTML

**验收**：`curl -X POST .../v1/url -d '{"url":"https://example.com/article"}'` 成功入库

---

## ⚙️ Sprint 2 · 质量 + 异步

### [#4] Redis 缓存 🔥

预估：1 天 ｜ 依赖：[#1]

- [ ] `app/services/cache/redis_cache.py`：
  - [ ] `get_redis() -> redis.asyncio.Redis`（从 `settings.REDIS_URL` 构造）
  - [ ] `cache_get(key)` / `cache_setex(key, ttl, value)`（`orjson` 序列化）
- [ ] `app/services/rag/embedding.py`：`aembed_texts` 前置查 `emb:{sha1(text)}`，命中跳过模型
- [ ] `app/services/rag/retriever.py`：`search` 前置查 `search:{sha1(query)}:{top_k}`，命中直接返回
- [ ] 关键链路 loguru 日志：cache hit / miss + 命中率（每 100 次打印一次）
- [ ] 单测：fake redis 验证读路径

**验收**：相同 query 二次调用耗时 < 5ms（cache hit），embedding 维度不变

---

### [#5] Celery 异步 ingestion 🔥

预估：1~2 天 ｜ 依赖：[#3]

- [ ] `app/tasks/worker.py`：
  - [ ] `celery_app = Celery("ai_copilot", broker=..., backend=...)`
  - [ ] 配 `task_serializer="json"`、`task_acks_late=True`、`worker_prefetch_multiplier=1`
- [ ] `app/tasks/ingestion_task.py`：
  - [ ] `process_file(filename, content_b64) -> {"document_id": int, "chunks": int}`
  - [ ] `process_url(url) -> ...`
  - [ ] 内部用 `asyncio.run(...)` 调 `IngestionService`
- [ ] `app/api/v1/upload.py`：改 `process_file.delay(...)`，返回 `{task_id, status:"pending"}`
- [ ] `app/api/v1/url.py`：同上
- [ ] 新增 `app/api/v1/tasks.py`：`GET /v1/tasks/{task_id}` 查 `AsyncResult`
- [ ] 启动 worker：`uv run celery -A app.tasks.worker.celery_app worker -l info`
- [ ] 单测：eager 模式（`task_always_eager=True`）跑通

**验收**：上传 5MB PDF，HTTP 立即返回；worker 端日志显示任务完成

---

### [#6] Chunker 升级（可选）💡

预估：0.5 天 ｜ 依赖：无

- [ ] `uv add langchain-text-splitters`
- [ ] `app/services/ingestion/chunker.py:chunk_text()` 改用 `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`
- [ ] 分隔符：`["\n\n", "\n", "。", "！", "？", ". ", "? ", "! ", " ", ""]`
- [ ] 签名保持 `(text: str) -> list[str]`
- [ ] 入库前 chunk 数对比（升级前 vs 升级后），召回 spot check

**验收**：相同文档升级后 chunk 数合理增加；现有 ingestion 链路无破坏

---

### [x] [#7] 向量索引评估 💡 ✅ commit f1a2b3c

预估：0.5 天 ｜ 依赖：无

- [x] 跑 `EXPLAIN ANALYZE` 测（26 行 chunks）
  - [x] seq force-off-indexes: 0.053ms
  - [x] ivfflat default probes=1: 0.049ms
  - [x] ivfflat probes=10: 0.047ms
  - [x] ivfflat probes=100: 0.049ms
  - [x] **结论：26 行数据下索引完全没用,直接删**
- [x] 新增 alembic 迁移 `9c0d1e2f3a4b` drop ivfflat
- [x] retriever 去掉 `SET LOCAL enable_indexscan=off` 死代码

**验收**：迁移后 `pg_indexes` 中 chunks 无 `idx_chunks_embedding`；26 行 retriever 召回 3 个相关 chunks（"Python 后端" dist=0.37）

**未来决策**：

- 1k~100k 行：建 hnsw（`CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`）
- >100k 行：重建 ivfflat `lists=sqrt(rows)`，或继续 hnsw
- 触发条件：单测 `test_search_returns_relevant_chunks_at_scale`（用合成 1k+ 数据跑 recall@k）

---

## 🚀 Sprint 3 · P2 启动

### [#8] 鉴权 / 多租户 🔥

预估：1~2 天 ｜ 依赖：无（与 Memory 并行更好）

- [ ] `app/core/security.py`：
  - [ ] JWT 模式：`create_token / decode_token / get_current_user`（`uv add pyjwt`）
  - [ ] 或 API Key 模式：Header `X-API-Key`，查 `users` 表
- [ ] 迁移：`documents` / `chunks` 加 `user_id`（外键 → `users.id`）
- [ ] `app/db/models/user.py`：新增 `User` 模型
- [ ] `Depends(get_current_user)` 注入所有 endpoint
- [ ] `app/schemas/common.py`：`APIError(code, message)`、`Page(items, total)`
- [ ] 错误统一中间件：`app/api/middleware.py`

**验收**：未带 token 请求 → 401；带 token 写入的数据带正确 `user_id`

---

### [#9] Memory 会话表 🔥

预估：1~2 天 ｜ 依赖：[#8]

- [ ] 迁移：`conversations(id, user_id, title, created_at, updated_at)` + `messages(id, conversation_id, role, content, created_at)`
- [ ] `app/db/models/conversation.py` / `message.py`
- [ ] `app/schemas/chat.py`：`ChatRequest` 加可选 `conversation_id`
- [ ] `app/services/chat/history.py`：`get_recent_messages(conversation_id, limit=10)`
- [ ] `app/api/v1/chat.py`：把历史 + 当前 query 拼成 retriever 的"伪 query"（或作为 system message）
- [ ] `app/api/v1/conversations.py`：`GET /v1/conversations`、`GET /v1/conversations/{id}/messages`
- [ ] 单测：多轮对话上下文不丢

**验收**：二轮对话能正确召回第一轮涉及的文档片段

---

### [#10] Agent 工具路由 ⭐

预估：2~3 天 ｜ 依赖：[#8]

- [ ] 不引 LangGraph，自建"规则 + LLM 分类"版
- [ ] `app/services/agent/router.py`：`route(query) -> Literal["rag", "llm", "tool"]`
- [ ] `app/services/agent/tools/`：
  - [ ] `@tool` 装饰器 + `ToolRegistry` 单例
  - [ ] 内置 `calculator` / `web_search`（可选，Bing/Google API）
- [ ] `app/api/v1/chat.py`：走 router 分发
- [ ] 后续可平滑切到 LangGraph（接口一致）

**验收**：`"1+1 等于几"` 走 tool；`"项目里有什么文档"` 走 rag；通用问答走 llm

---

### [#11] 可观测性 ⭐

预估：1 天 ｜ 依赖：无

- [ ] `app/core/logger.py`：loguru 加 `request_id`（`logger.contextualize`）
- [ ] `app/api/middleware.py`：
  - [ ] 请求开始生成 `request_id`（header `X-Request-ID` 或 uuid）
  - [ ] 记录 method/path/status/duration_ms
- [ ] LLM latency：在 `MiniMaxLLM.chat` 外层包计时 + 慢阈值告警日志
- [ ] DB 慢查询：`DB_ECHO` + 自定义事件监听
- [ ] `notes/observability.md`：使用方式

**验收**：每个请求有唯一 `request_id`，日志可串起来

---

### [#12] Web UI 💡

预估：2~3 天 ｜ 依赖：[#9]

- [ ] 选型：Next.js（最灵活） / Gradio（最快） / FastAPI 模板（最简）
- [ ] MVP：聊天界面 + 文件上传 + 引用高亮（retriever top_k 答案位置标 [1][2]）
- [ ] 鉴权接入 [\#8]

**验收**：浏览器能对话 + 看到引用片段

---

## 🧹 工程债务（任意 Sprint 顺手清）

- [ ] `app/utils/text.py`：实现 `clean_text`（去多余空白、统一引号、strip 控制字符）
- [ ] `app/schemas/document.py`：`DocumentOut(id, filename, created_at, chunk_count)`
- [ ] `app/schemas/common.py`：`APIError`、`Page<T>`
- [ ] `app/core/security.py` 至少补个 stub raise，避免空文件
- [ ] `pyproject.toml` 加 `[tool.ruff.lint]` `select = ["E","F","I","UP","B","SIM"]`（升级规则集）
- [ ] GitHub Actions：lint + alembic upgrade head + pytest
- [ ] 预提交：`pre-commit` 装 ruff
- [ ] **`.env.example` 同步真实 `.env` 字段顺序 + 加 `# 注意保持 LF` 注释**
- [ ] **`notes/llm_api_smoke.md`：第三方 API（minimax / 任何 OpenAI 兼容）路径上线前用 httpx 5 秒验通**,不要信文档
- [ ] **`app/api/middleware.py`：loguru `request_id` 注入 + LLM 慢阈值告警**(同时解决"P2 可观测性"的 [#11])

---

## 📌 不在当前路线（备查）

- 多语言 embedding（`bge-m3` 已支持 100+ 语言，先观察）
- Rerank 阶段（`bge-reranker-v2-m3`，P3 再考虑）
- 多模态（图片/音频）
- 联邦知识库 / 跨租户检索

---

## 如何使用本文件

1. 开新任务前先看依赖矩阵（PROJECT_CONTEXT.md 第二节）和本文件
2. 任务做完把 `- [ ]` 改成 `- [x]`，加 commit 引用：`[x] [#3] commit abc1234`
3. 跨 Sprint 改动大时，开 git 分支：`git checkout -b feat/url-ingestion`
4. 阻塞/风险标到对应任务下的「备注」字段
