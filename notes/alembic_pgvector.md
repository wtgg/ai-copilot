# Alembic + PostgreSQL + pgvector 踩坑笔记（AI RAG 项目）

## 一、背景

技术栈：

* FastAPI（异步）
* SQLAlchemy 2.0（async）
* PostgreSQL（Docker）
* pgvector（向量检索）
* Alembic（数据库迁移）

目标：

> 实现支持向量存储的数据库结构（documents + chunks）

---

## 二、核心结论（先记住）

### 1️⃣ pgvector 是“数据库级扩展”

错误认知：

> 在 PostgreSQL 容器中安装一次就全局可用 ❌

正确认知：

> 每个 database 都需要单独执行：

```sql
CREATE EXTENSION vector;
```

---

### 2️⃣ Alembic 不直接支持 async driver

你不能用：

```
postgresql+asyncpg
```

必须在 Alembic 中转换为：

```
postgresql+psycopg2
```

---

### 3️⃣ Alembic 自动生成依赖 metadata

如果 migration 是空的：

```python
def upgrade():
    pass
```

说明：

> ❗ Alembic 没检测到你的模型

---

## 三、常见错误 & 解决方案

---

### ❌ 错误1：迁移文件是空的

#### 原因：

没有正确导入 model

#### 解决：

```python
# alembic/env.py
from app.db.models import *
```

---

### ❌ 错误2：

```
Can't locate revision identified by 'xxx'
```

#### 原因：

你删除了 migration 文件，但数据库或缓存还引用它

#### 解决：

```bash
rm -rf alembic/versions/*
```

重新生成：

```bash
alembic revision --autogenerate -m "init"
```

---

### ❌ 错误3：

```
psycopg2 is not async
```

#### 原因：

Alembic 使用 async engine

#### 解决：

👉 Alembic 使用同步模式

```python
from sqlalchemy import engine_from_config
```

---

### ❌ 错误4：

```
NameError: pgvector is not defined
```

#### 原因：

migration 文件缺少 import

#### 解决：

```python
from pgvector.sqlalchemy import Vector
```

---

### ❌ 错误5（最关键）：

```
type "vector" does not exist
```

#### 原因：

当前数据库没有启用 pgvector

#### 解决：

```sql
\c ai_copilot
CREATE EXTENSION vector;
```

---

## 四、正确的 Alembic 配置（最终版）

### env.py 关键点

```python
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
)
```

---

### 使用同步 engine

```python
from sqlalchemy import engine_from_config

connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
```

---

## 五、标准迁移流程（必须记住）

---

### 1️⃣ 初始化（只做一次）

```bash
alembic init alembic
```

---

### 2️⃣ 修改 env.py

* 导入 Base
* 导入 models
* 替换 asyncpg → psycopg2

---

### 3️⃣ 生成迁移

```bash
alembic revision --autogenerate -m "init"
```

---

### 4️⃣ 检查 migration 文件

确保：

```python
op.create_table(...)
```

存在

---

### 5️⃣ 执行迁移

```bash
alembic upgrade head
```

---

## 六、pgvector 正确使用方式

---

### 数据库必须执行：

```sql
CREATE EXTENSION vector;
```

---

### SQLAlchemy 模型

```python
from pgvector.sqlalchemy import Vector

embedding = Column(Vector(1024))
```

---

### 索引（性能关键）

```python
Index(
    "idx_chunks_embedding",
    "embedding",
    postgresql_using="ivfflat"
)
```

---

## 七、最佳实践（避免以后再踩坑）

---

### ✅ 1. 在 migration 中自动创建扩展

```python
op.execute("CREATE EXTENSION IF NOT EXISTS vector")
```

---

### ✅ 2. 开发环境建议

* 每次改模型 → 重新生成 migration
* 不要手动改数据库结构

---

### ✅ 3. 项目结构必须保证

```python
app/db/base.py
app/db/models/__init__.py
```

统一导入所有 model

---

## 八、你这次踩坑的本质总结

你遇到的问题，本质上是三件事：

---

### 1️⃣ 异步 vs 同步冲突

* FastAPI → async
* Alembic → sync

👉 必须隔离

---

### 2️⃣ metadata 未加载

👉 Alembic 根本不知道你的表

---

### 3️⃣ pgvector 作用域误解

👉 extension ≠ 全局

---

## 九、现在你的状态

你已经完成：

```text
✅ Alembic 正确配置
✅ pgvector 启用
✅ 表结构创建成功
```

---

## 十、下一步（真正进入核心）

👉 不再是数据库问题，而是：

```text
RAG ingestion pipeline
```

* chunk
* embedding
* 入库
* 检索

---




