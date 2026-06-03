# AI NewsHub TECH_DESIGN

## 1. 技术目标

项目从“AI 资讯 CMS 后台”收敛为：

```text
FastAPI + Vue + MySQL + Redis + OpenAI-compatible LLM 的 AI 资讯 RAG 知识库系统
```

V1 技术目标：

1. 前端只保留三条主流程：每日采集、知识库、AI 问答；
2. 后端预留清晰接口，方便继续手写逻辑；
3. 数据库围绕 RAG 设计，而不是围绕分类、标签、选题状态；
4. 支持后续 embedding、向量检索和流式输出；
5. 旧 CMS 模块保留代码文件，但不再作为主入口。

---

## 2. 系统架构

```text
Vue 前端
  ↓
FastAPI Router
  ↓
CRUD / Service 占位
  ↓
MySQL
  ↓
knowledge_documents / rag_chunks

FastAPI
  ↓
OpenAI-compatible LLM

FastAPI
  ↓
StreamingResponse
  ↓
前端 ReadableStream
```

---

## 3. 前端设计

## 3.1 主页面

| 页面 | 路由 | 说明 |
|---|---|---|
| 每日采集 | `/daily` | 触发抓取、显示采集结果 |
| 知识库 | `/knowledge` | 按日期和关键词查看入库资讯 |
| AI 问答 | `/ask` | 基于 RAG 知识库提问 |

## 3.2 旧页面处理

旧页面代码可以保留，方便学习和回退，但不放在主导航：

```text
/news
/topics
/taxonomy
```

---

## 4. 后端目录调整

新增文件：

```text
backend/schemas/daily_digest.py
backend/schemas/knowledge.py
backend/schemas/rag_chat.py

backend/crud/daily_digest.py
backend/crud/knowledge.py
backend/crud/rag_chat.py

backend/routers/daily_digest.py
backend/routers/knowledge.py
backend/routers/rag_chat.py
```

保留文件：

```text
auth.py
health.py
db_configs.py
security.py
response.py
exception_handlers.py
```

旧业务文件暂不删除：

```text
news.py
topics.py
categories.py
tags.py
dashboard.py
```

原因：这些是学习过程资产，直接删掉不利于回顾。

---

## 5. 每日采集流程设计

核心函数建议：

```python
async def create_daily_digest_run_crud(run_data, db, current_user_id):
    # 1. 读取固定来源
    # 2. 抓取当日资讯
    # 3. 调用大模型整理
    # 4. dry_run=True 只返回预览
    # 5. dry_run=False 写入 knowledge_documents 和 rag_chunks
    pass
```

V1 前端不再暴露复杂来源策略，只暴露：

```text
日期、最大条数、是否只预览、模型设置
```

---

## 6. RAG 设计

## 6.1 最小可用 RAG

第一阶段可以不用向量库，先用 MySQL 做关键词检索：

```text
WHERE digest_date BETWEEN date_from AND date_to
AND (title LIKE keyword OR summary LIKE keyword OR content LIKE keyword)
```

优点：

1. 学习成本低；
2. 容易验证；
3. 能先跑通问答闭环。

## 6.2 第二阶段 embedding

后续再增加：

```text
1. 调用 embedding 模型
2. 写入 rag_chunks.embedding
3. 查询时计算问题 embedding
4. 做相似度 top_k
```

MySQL 不擅长向量检索，如果后续要更专业，可以迁移到：

```text
pgvector / Qdrant / Milvus / Chroma
```

但 V1 不需要一开始就上向量库。

---

## 7. 流式输出设计

后端：

```python
from fastapi.responses import StreamingResponse

@router.post("/stream")
async def stream_answer():
    return StreamingResponse(generator(), media_type="text/event-stream")
```

前端：

```ts
const response = await fetch('/api/v1/rag-chat/stream', {
  method: 'POST',
  headers,
  body: JSON.stringify(payload),
})

const reader = response.body?.getReader()
```

V1 可以先返回占位流，确保前端展示逻辑跑通。

---

## 8. Redis 使用

V1 Redis 暂时不作为核心。

可选用途：

| 用途 | 是否必须 |
|---|---|
| 缓存知识库列表 | 否 |
| 缓存问答结果 | 否 |
| 记录采集任务状态 | 后续可做 |

当前重点是 MySQL 知识库和 RAG 闭环。

---

## 9. 环境变量

建议新增：

```env
AI_DIGEST_API_BASE_URL=https://api.openai.com/v1
AI_DIGEST_API_KEY=
AI_DIGEST_MODEL=gpt-4.1-mini

EMBEDDING_API_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
```

前端可以临时传 key，但生产环境应优先后端 `.env`。

---

## 10. 开发顺序

```text
1. 前端三页重构完成
2. 后端三个新模块接口预留
3. 写 knowledge_documents / rag_chunks ORM
4. Alembic 建表
5. 每日采集写入 knowledge_documents
6. chunk 切分写入 rag_chunks
7. MySQL like 检索问答
8. 流式输出
9. embedding 检索
```
