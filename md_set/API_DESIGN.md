# AI NewsHub API_DESIGN

## 1. 基础约定

| 项目 | 内容 |
|---|---|
| API 风格 | RESTful + SSE/Stream |
| 基础路径 | `/api/v1` |
| 数据格式 | JSON |
| 鉴权 | JWT Bearer Token |
| 主产品方向 | AI 资讯采集 + RAG 知识库 + AI 问答 |

统一响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

错误响应：

```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

---

## 2. 认证模块

现有认证接口保留，作为系统入口。

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/auth/register` | 注册 |
| POST | `/auth/login` | 登录 |
| GET | `/auth/me` | 获取当前用户 |

---

## 3. 每日采集模块

## 3.1 创建每日采集任务

```http
POST /daily-digest/runs
```

是否登录：是

用途：

触发固定 `ai-news-blogger-digest` 流程，抓取指定日期窗口内的 AI 资讯。V1 先预留接口，后端逻辑由你继续手写。

请求体：

```json
{
  "digest_date": "2026-06-03",
  "max_items": 30,
  "dry_run": true,
  "llm_config": {
    "api_base_url": "https://api.openai.com/v1",
    "api_key": "sk-xxxxx",
    "model": "gpt-4.1-mini"
  }
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| digest_date | date | 否 | 要采集的日期，不传默认为今天 |
| max_items | int | 否 | 最多保留候选资讯，默认 30 |
| dry_run | bool | 否 | true 只预览，false 写入知识库 |
| llm_config.api_base_url | string | 否 | OpenAI-compatible Base URL |
| llm_config.api_key | string | 否 | API Key，生产建议从后端环境变量读 |
| llm_config.model | string | 否 | 模型名 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "run_id": "run-demo-20260603",
    "status": "reserved",
    "digest_date": "2026-06-03",
    "message": "接口已预留：请在 crud/daily_digest.py 中补充固定 skill 抓取、整理、入库逻辑",
    "collected_count": 0,
    "document_count": 0,
    "chunk_count": 0,
    "failed_sources": [],
    "preview_items": []
  }
}
```

后端预留逻辑：

```text
1. 固定读取 AI 资讯源
2. 抓取当日资讯
3. 去重和过滤
4. 调用 LLM 结构化整理
5. dry_run=true 返回 preview_items
6. dry_run=false 写入 knowledge_documents
7. 切分正文写入 rag_chunks
```

---

## 3.2 获取采集任务列表

```http
GET /daily-digest/runs
```

是否登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 10,
    "pages": 0
  }
}
```

---

## 4. 知识库模块

## 4.1 获取知识库文档列表

```http
GET /knowledge/documents
```

是否登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| digest_date | date | 否 | 按归档日期筛选 |
| keyword | string | 否 | 搜索标题、摘要、来源 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "DeepSeek API 价格页出现新模型信息",
        "summary": "官方价格页出现模型和价格变化，适合继续核验。",
        "source_name": "DeepSeek Docs",
        "source_url": "https://api-docs.deepseek.com/quick_start/pricing",
        "published_at": "2026-06-03T10:00:00",
        "digest_date": "2026-06-03",
        "credibility": "official"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

---

## 4.2 获取知识库文档详情

```http
GET /knowledge/documents/{document_id}
```

是否登录：是

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "DeepSeek API 价格页出现新模型信息",
    "summary": "官方价格页出现模型和价格变化，适合继续核验。",
    "content": "用于 RAG 的完整正文或整理后的结构化内容。",
    "source_name": "DeepSeek Docs",
    "source_url": "https://api-docs.deepseek.com/quick_start/pricing",
    "published_at": "2026-06-03T10:00:00",
    "digest_date": "2026-06-03",
    "credibility": "official",
    "chunks": [
      {
        "id": 1,
        "chunk_index": 0,
        "chunk_text": "DeepSeek 官方价格页出现..."
      }
    ]
  }
}
```

---

## 5. RAG 问答模块

## 5.1 普通问答

```http
POST /rag-chat/ask
```

是否登录：是

用途：

非流式问答。适合 Swagger 调试，也适合作为前端失败降级方案。

请求体：

```json
{
  "question": "今天有哪些 AI 消息？",
  "date_from": "2026-06-03",
  "date_to": "2026-06-03",
  "top_k": 5
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "接口已预留：请在 crud/rag_chat.py 中补充检索和 LLM 回答逻辑。",
    "citations": [],
    "matched_chunks": []
  }
}
```

后端预留逻辑：

```text
1. 根据日期范围过滤 rag_chunks
2. 根据问题做向量检索或关键词检索
3. 取 top_k 片段
4. 组织 prompt
5. 调用 LLM
6. 返回 answer + citations
```

---

## 5.2 流式问答

```http
POST /rag-chat/stream
```

是否登录：是

用途：

让前端像 ChatGPT 一样逐字显示回答。

请求体同 `/rag-chat/ask`。

响应格式：

```text
text/event-stream
```

事件示例：

```text
data: {"type":"delta","content":"今天"}
data: {"type":"delta","content":"的 AI 消息包括..."}
data: {"type":"done","citations":[]}
```

---

## 6. 健康检查

```http
GET /health
```

是否登录：否

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok",
    "service": "ai-newshub-backend"
  }
}
```

---

## 7. V1 接口开发顺序

```text
1. POST /auth/register
2. POST /auth/login
3. GET /auth/me
4. POST /daily-digest/runs
5. GET /daily-digest/runs
6. GET /knowledge/documents
7. GET /knowledge/documents/{document_id}
8. POST /rag-chat/ask
9. POST /rag-chat/stream
10. GET /health
```
