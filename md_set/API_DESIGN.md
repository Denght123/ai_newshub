# AI NewsHub 接口设计文档 API_DESIGN

## 1. 文档信息

| 项目 | 内容 |
|---|---|
| 项目名称 | AI NewsHub |
| 文档类型 | 接口设计文档 |
| API 风格 | RESTful |
| 后端 | FastAPI |
| 前端 | Vue |
| 数据格式 | JSON |
| 基础路径 | `/api/v1` |

---

## 2. 通用约定

## 2.1 基础地址

本地开发：

```text
http://localhost:8000/api/v1
```

生产环境：

```text
https://your-domain.com/api/v1
```

---

## 2.2 请求格式

除文件上传外，所有接口默认使用 JSON。

请求头：

```http
Content-Type: application/json
```

需要登录的接口额外携带：

```http
Authorization: Bearer <access_token>
```

---

## 2.3 统一响应格式

成功响应：

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

分页响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "pages": 10
  }
}
```

---

## 2.4 通用错误码

| code | HTTP 状态码 | 说明 |
|---|---|---|
| 200 | 200 | 成功 |
| 400 | 400 | 参数错误 |
| 401 | 401 | 未登录或 token 无效 |
| 403 | 403 | 无权限 |
| 404 | 404 | 资源不存在 |
| 409 | 409 | 数据冲突 |
| 500 | 500 | 服务器内部错误 |

---

## 2.5 分页参数

列表接口统一支持：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| page | int | 否 | 1 | 当前页码 |
| page_size | int | 否 | 10 | 每页数量，最大 100 |

---

## 3. 认证模块

## 3.1 用户注册

```http
POST /auth/register
```

是否登录：否

请求体：

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | string | 是 | 用户名，唯一 |
| email | string | 是 | 邮箱，唯一 |
| password | string | 是 | 密码，至少 6 位 |

响应：

```json
{
  "code": 200,
  "message": "register success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "nickname": null,
    "role": "user",
    "is_active": true
  }
}
```

可能错误：

| code | message |
|---|---|
| 400 | password length must be at least 6 |
| 409 | username already exists |
| 409 | email already exists |

---

## 3.2 用户登录

```http
POST /auth/login
```

是否登录：否

请求体：

```json
{
  "username_or_email": "testuser",
  "password": "123456"
}
```

响应：

```json
{
  "code": 200,
  "message": "login success",
  "data": {
    "access_token": "xxxxx.yyyyy.zzzzz",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "nickname": null,
      "role": "user"
    }
  }
}
```

可能错误：

| code | message |
|---|---|
| 401 | invalid username or password |
| 403 | user is disabled |

---

## 3.3 获取当前用户

```http
GET /auth/me
```

是否登录：是

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "nickname": "测试用户",
    "role": "user",
    "is_active": true,
    "created_at": "2026-04-28T10:00:00"
  }
}
```

---

## 4. 分类模块

## 4.1 创建分类

```http
POST /categories
```

是否登录：是  
权限：管理员

请求体：

```json
{
  "name": "大模型",
  "description": "大模型发布、更新和评测",
  "sort_order": 1
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "大模型",
    "description": "大模型发布、更新和评测",
    "sort_order": 1,
    "is_active": true
  }
}
```

---

## 4.2 分类列表

```http
GET /categories
```

是否登录：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| only_active | bool | 否 | 是否只返回启用分类 |

示例：

```http
GET /categories?only_active=true
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "大模型",
      "description": "大模型发布、更新和评测",
      "sort_order": 1,
      "is_active": true
    }
  ]
}
```

---

## 4.3 修改分类

```http
PUT /categories/{category_id}
```

是否登录：是  
权限：管理员

请求体：

```json
{
  "name": "大模型",
  "description": "大模型相关资讯",
  "sort_order": 1,
  "is_active": true
}
```

---

## 4.4 删除分类

```http
DELETE /categories/{category_id}
```

是否登录：是  
权限：管理员

规则：

如果分类下已有资讯或选题，第一版建议不允许删除。

响应：

```json
{
  "code": 200,
  "message": "delete success",
  "data": null
}
```

---

## 5. 标签模块

## 5.1 创建标签

```http
POST /tags
```

是否登录：是  
权限：管理员

请求体：

```json
{
  "name": "DeepSeek"
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "DeepSeek"
  }
}
```

---

## 5.2 标签列表

```http
GET /tags
```

是否登录：是

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "DeepSeek"
    },
    {
      "id": 2,
      "name": "开源"
    }
  ]
}
```

---

## 5.3 修改标签

```http
PUT /tags/{tag_id}
```

是否登录：是  
权限：管理员

请求体：

```json
{
  "name": "DeepSeek"
}
```

---

## 5.4 删除标签

```http
DELETE /tags/{tag_id}
```

是否登录：是  
权限：管理员

响应：

```json
{
  "code": 200,
  "message": "delete success",
  "data": null
}
```

---

## 6. 资讯模块

## 6.1 新增资讯

```http
POST /news
```

是否登录：是

请求体：

```json
{
  "title": "DeepSeek 发布新一代大模型",
  "source_name": "DeepSeek 官方",
  "source_url": "https://example.com/news/1",
  "summary": "DeepSeek 发布了新一代模型，价格和性能受到关注。",
  "content": "这里可以记录更详细的阅读笔记。",
  "category_id": 1,
  "tag_ids": [1, 2],
  "status": "unread",
  "importance_score": 5,
  "heat_score": 5,
  "publish_time": "2026-04-28T10:00:00"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| title | string | 是 | 资讯标题 |
| source_name | string | 否 | 来源名称 |
| source_url | string | 否 | 原文链接 |
| summary | string | 否 | 摘要 |
| content | string | 否 | 内容笔记 |
| category_id | int | 否 | 分类 ID |
| tag_ids | int[] | 否 | 标签 ID 列表 |
| status | string | 否 | 默认 unread |
| importance_score | int | 否 | 1-5 |
| heat_score | int | 否 | 1-5 |
| publish_time | datetime | 否 | 原文发布时间 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "DeepSeek 发布新一代大模型",
    "source_name": "DeepSeek 官方",
    "source_url": "https://example.com/news/1",
    "summary": "DeepSeek 发布了新一代模型，价格和性能受到关注。",
    "content": "这里可以记录更详细的阅读笔记。",
    "category": {
      "id": 1,
      "name": "国产 AI"
    },
    "tags": [
      {
        "id": 1,
        "name": "DeepSeek"
      }
    ],
    "status": "unread",
    "importance_score": 5,
    "heat_score": 5,
    "is_favorite": false,
    "publish_time": "2026-04-28T10:00:00",
    "created_at": "2026-04-28T12:00:00"
  }
}
```

---

## 6.2 资讯列表

```http
GET /news
```

是否登录：是

查询参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 10 | 每页数量 |
| keyword | string | 否 | - | 搜索标题、摘要、来源 |
| category_id | int | 否 | - | 分类筛选 |
| status | string | 否 | - | 状态筛选 |
| is_favorite | bool | 否 | - | 收藏筛选 |
| order_by | string | 否 | created_at | 排序字段 |
| order | string | 否 | desc | asc/desc |

示例：

```http
GET /news?page=1&page_size=10&keyword=DeepSeek&category_id=1&status=unread
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "DeepSeek 发布新一代大模型",
        "source_name": "DeepSeek 官方",
        "category": {
          "id": 1,
          "name": "国产 AI"
        },
        "tags": [
          {
            "id": 1,
            "name": "DeepSeek"
          }
        ],
        "status": "unread",
        "importance_score": 5,
        "heat_score": 5,
        "is_favorite": false,
        "publish_time": "2026-04-28T10:00:00",
        "created_at": "2026-04-28T12:00:00"
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

## 6.3 资讯详情

```http
GET /news/{news_id}
```

是否登录：是

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "DeepSeek 发布新一代大模型",
    "source_name": "DeepSeek 官方",
    "source_url": "https://example.com/news/1",
    "summary": "DeepSeek 发布了新一代模型，价格和性能受到关注。",
    "content": "这里可以记录更详细的阅读笔记。",
    "category": {
      "id": 1,
      "name": "国产 AI"
    },
    "tags": [
      {
        "id": 1,
        "name": "DeepSeek"
      }
    ],
    "status": "unread",
    "importance_score": 5,
    "heat_score": 5,
    "is_favorite": false,
    "publish_time": "2026-04-28T10:00:00",
    "created_by": {
      "id": 1,
      "username": "testuser"
    },
    "created_at": "2026-04-28T12:00:00",
    "updated_at": "2026-04-28T12:00:00"
  }
}
```

---

## 6.4 修改资讯

```http
PUT /news/{news_id}
```

是否登录：是  
权限：创建人或管理员

请求体：

```json
{
  "title": "DeepSeek 新模型发布",
  "source_name": "DeepSeek 官方",
  "source_url": "https://example.com/news/1",
  "summary": "更新后的摘要",
  "content": "更新后的笔记",
  "category_id": 1,
  "tag_ids": [1, 2, 3],
  "status": "read",
  "importance_score": 4,
  "heat_score": 5,
  "publish_time": "2026-04-28T10:00:00"
}
```

响应：

```json
{
  "code": 200,
  "message": "update success",
  "data": {
    "id": 1,
    "title": "DeepSeek 新模型发布"
  }
}
```

---

## 6.5 删除资讯

```http
DELETE /news/{news_id}
```

是否登录：是  
权限：创建人或管理员

说明：软删除。

响应：

```json
{
  "code": 200,
  "message": "delete success",
  "data": null
}
```

---

## 6.6 收藏 / 取消收藏资讯

```http
PATCH /news/{news_id}/favorite
```

是否登录：是

请求体：

```json
{
  "is_favorite": true
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "is_favorite": true
  }
}
```

---

## 6.7 从资讯创建选题

```http
POST /news/{news_id}/to-topic
```

是否登录：是

请求体：

```json
{
  "title": "DeepSeek 新模型为什么值得关注？",
  "angle": "从国产 AI、成本下降和生态影响三个角度分析。",
  "recommended_title": "DeepSeek 这次，不只是追赶",
  "reason": "兼具技术热点和大众传播价值。",
  "target_reader": "AI 兴趣用户、大学生、科技公众号读者",
  "category_id": 1,
  "value_score": 5,
  "difficulty_score": 3,
  "traffic_score": 5,
  "deadline": "2026-05-01T20:00:00"
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "news_id": 1,
    "title": "DeepSeek 新模型为什么值得关注？",
    "status": "pending"
  }
}
```

---

## 7. 选题模块

## 7.1 新建选题

```http
POST /topics
```

是否登录：是

请求体：

```json
{
  "news_id": null,
  "title": "AI 编程助手正在改变大学生学习方式",
  "angle": "从学习效率、代码理解、作业辅助三个角度写。",
  "recommended_title": "大学生正在偷偷用 AI 重写学习方式",
  "reason": "大众读者容易理解，也和实际使用场景相关。",
  "target_reader": "大学生、AI 工具用户",
  "category_id": 3,
  "value_score": 4,
  "difficulty_score": 2,
  "traffic_score": 4,
  "deadline": "2026-05-10T20:00:00"
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "AI 编程助手正在改变大学生学习方式",
    "status": "pending",
    "value_score": 4,
    "difficulty_score": 2,
    "traffic_score": 4
  }
}
```

---

## 7.2 选题列表

```http
GET /topics
```

是否登录：是

查询参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 10 | 每页数量 |
| keyword | string | 否 | - | 搜索标题、角度、推荐标题 |
| status | string | 否 | - | 状态筛选 |
| category_id | int | 否 | - | 分类筛选 |
| order_by | string | 否 | created_at | 排序字段 |
| order | string | 否 | desc | asc/desc |

允许的 order_by：

```text
created_at
deadline
value_score
traffic_score
difficulty_score
```

示例：

```http
GET /topics?page=1&page_size=10&status=pending&order_by=value_score&order=desc
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "DeepSeek 新模型为什么值得关注？",
        "recommended_title": "DeepSeek 这次，不只是追赶",
        "status": "pending",
        "value_score": 5,
        "difficulty_score": 3,
        "traffic_score": 5,
        "deadline": "2026-05-01T20:00:00",
        "category": {
          "id": 1,
          "name": "国产 AI"
        },
        "created_at": "2026-04-28T12:00:00"
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

## 7.3 选题详情

```http
GET /topics/{topic_id}
```

是否登录：是

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "news": {
      "id": 1,
      "title": "DeepSeek 发布新一代大模型"
    },
    "title": "DeepSeek 新模型为什么值得关注？",
    "angle": "从国产 AI、成本下降和生态影响三个角度分析。",
    "recommended_title": "DeepSeek 这次，不只是追赶",
    "reason": "兼具技术热点和大众传播价值。",
    "target_reader": "AI 兴趣用户、大学生、科技公众号读者",
    "category": {
      "id": 1,
      "name": "国产 AI"
    },
    "status": "pending",
    "value_score": 5,
    "difficulty_score": 3,
    "traffic_score": 5,
    "deadline": "2026-05-01T20:00:00",
    "created_at": "2026-04-28T12:00:00",
    "updated_at": "2026-04-28T12:00:00"
  }
}
```

---

## 7.4 修改选题

```http
PUT /topics/{topic_id}
```

是否登录：是  
权限：创建人或管理员

请求体：

```json
{
  "title": "DeepSeek 新模型值得普通人关注吗？",
  "angle": "从使用成本、国产 AI 和开源生态分析。",
  "recommended_title": "DeepSeek 这次，把 AI 价格打下来了",
  "reason": "选题更贴近大众关心的价格问题。",
  "target_reader": "AI 兴趣用户",
  "category_id": 1,
  "status": "selected",
  "value_score": 5,
  "difficulty_score": 3,
  "traffic_score": 5,
  "deadline": "2026-05-01T20:00:00"
}
```

响应：

```json
{
  "code": 200,
  "message": "update success",
  "data": {
    "id": 1,
    "title": "DeepSeek 新模型值得普通人关注吗？",
    "status": "selected"
  }
}
```

---

## 7.5 删除选题

```http
DELETE /topics/{topic_id}
```

是否登录：是  
权限：创建人或管理员

说明：软删除。

响应：

```json
{
  "code": 200,
  "message": "delete success",
  "data": null
}
```

---

## 7.6 修改选题状态

```http
PATCH /topics/{topic_id}/status
```

是否登录：是  
权限：创建人或管理员

请求体：

```json
{
  "status": "writing"
}
```

允许状态：

```text
pending
selected
writing
published
abandoned
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "status": "writing"
  }
}
```

---

## 8. 仪表盘模块

## 8.1 获取仪表盘概览

```http
GET /dashboard/overview
```

是否登录：是

说明：

该接口使用 Redis 缓存 60 秒。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "news_total": 120,
    "unread_news_total": 30,
    "favorite_news_total": 18,
    "topic_total": 25,
    "pending_topic_total": 8,
    "writing_topic_total": 3,
    "published_topic_total": 10,
    "recent_news": [
      {
        "id": 1,
        "title": "DeepSeek 发布新一代大模型",
        "status": "unread",
        "created_at": "2026-04-28T12:00:00"
      }
    ],
    "recent_topics": [
      {
        "id": 1,
        "title": "DeepSeek 新模型为什么值得关注？",
        "status": "pending",
        "created_at": "2026-04-28T12:00:00"
      }
    ]
  }
}
```

---

## 9. AI 自动抓取模块

## 9.1 创建 AI 抓取任务

```http
POST /ai-digest/runs
```

是否登录：是  
权限：管理员或已登录用户，第一版可先只要求登录

接口用途：

前端点击“AI 自动抓取”后，调用该接口创建一次 AI 资讯抓取任务。后端第一版会根据 `ai-news-blogger-digest` 工作流规则抓取资讯、调用 OpenAI-compatible 大模型、匹配现有分类，并按配置决定是否写入 `news`。

第一版建议：

- `dry_run=true` 时只返回预览结果，不写入数据库；
- `dry_run=false` 时才真正写入资讯表，可选生成选题；
- API Key 可以临时从请求体传入，也可以后续改为只读取后端 `.env`；
- 大模型接口必须兼容 OpenAI 风格：`base_url + api_key + model`；
- 自动分类优先使用当前系统已有分类，避免随意创建大量脏分类。

请求体：

```json
{
  "skill_name": "ai-news-blogger-digest",
  "llm_provider": "openai_compatible",
  "api_base_url": "https://api.openai.com/v1",
  "api_key": "sk-xxxxx",
  "model": "gpt-4.1-mini",
  "time_window_hours": 24,
  "max_items": 30,
  "source_profile": "balanced",
  "category_strategy": "match_existing",
  "category_ids": [1, 2, 3],
  "auto_create_missing_categories": false,
  "create_topics": true,
  "dry_run": true,
  "prompt_note": "更关注国产大模型、开源 Agent、API 降价，不要收录纯融资八卦。"
}
```

字段说明：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| skill_name | string | 否 | ai-news-blogger-digest | 要调用或参考的资讯抓取工作流名称 |
| llm_provider | string | 否 | openai_compatible | 大模型服务商标识，例如 openai、openai_compatible、deepseek_compatible |
| api_base_url | string | 是 | - | OpenAI-compatible API 基础地址，例如 `https://api.openai.com/v1` |
| api_key | string | 否 | null | 大模型 API Key。生产环境建议从后端环境变量读取，不建议长期由前端保存 |
| model | string | 否 | gpt-4.1-mini | 模型名，例如 `gpt-4.1-mini`、`deepseek-chat`、`qwen-plus` |
| time_window_hours | int | 否 | 24 | 抓取最近多少小时的信息，范围 1-168 |
| max_items | int | 否 | 30 | 最多保留多少条候选资讯，范围 5-100 |
| source_profile | string | 否 | balanced | 来源覆盖策略，见下方枚举说明 |
| category_strategy | string | 否 | match_existing | 分类策略，见下方枚举说明 |
| category_ids | array[int] | 否 | [] | 可参与匹配或固定写入的现有分类 ID |
| auto_create_missing_categories | bool | 否 | false | 是否允许后端自动创建缺失分类 |
| create_topics | bool | 否 | true | 是否根据高价值资讯同步生成选题建议 |
| dry_run | bool | 否 | true | 是否只预览不入库 |
| prompt_note | string | 否 | null | 用户给抓取工作流的补充要求 |

`source_profile` 可选值：

| 值 | 说明 |
|---|---|
| balanced | 均衡覆盖官方、媒体、社区、论文、开源 |
| minimal | 最小可用抓取，只覆盖少量核心来源 |
| official_first | 官方来源优先 |
| community_hot | 社区热度优先，例如 Hacker News、GitHub Trending |

`category_strategy` 可选值：

| 值 | 说明 |
|---|---|
| match_existing | 让大模型根据 `category_ids` 对候选资讯匹配现有分类 |
| fixed | 所有入库资讯固定写入所选分类，适合只选一个分类时使用 |
| none | 不设置分类 |

响应：

```json
{
  "code": 200,
  "message": "ai digest run success",
  "data": {
    "run_id": "run-a1b2c3d4e5f6",
    "status": "completed",
    "message": "AI 抓取整理完成，当前仅返回预览数据",
    "received_items": 12,
    "created_news_count": 0,
    "created_topic_count": 0,
    "skipped_count": 2,
    "failed_sources": [],
    "preview_items": [],
    "config_summary": {
      "current_user_id": 1,
      "skill_name": "ai-news-blogger-digest",
      "llm_provider": "openai_compatible",
      "api_base_url": "https://api.openai.com/v1",
      "model": "gpt-4.1-mini",
      "time_window_hours": 24,
      "max_items": 30,
      "source_profile": "balanced",
      "category_strategy": "match_existing",
      "matched_category_count": 3,
      "auto_create_missing_categories": false,
      "create_topics": true,
      "dry_run": true
    }
  }
}
```

后端真实实现后的响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "run_id": "run-20260601-001",
    "status": "completed",
    "message": "抓取完成，已生成预览结果",
    "received_items": 18,
    "created_news_count": 0,
    "created_topic_count": 0,
    "skipped_count": 2,
    "failed_sources": [
      "Hugging Face Trending timeout"
    ],
    "preview_items": [
      {
        "title": "DeepSeek API 价格页出现新模型信息",
        "source_name": "DeepSeek 官方文档",
        "source_url": "https://api-docs.deepseek.com/quick_start/pricing",
        "matched_category": {
          "id": 1,
          "name": "大模型"
        },
        "importance_score": 5,
        "heat_score": 4,
        "one_line_summary": "官方价格页出现新模型或价格变化，适合继续核验并写成资讯。"
      }
    ]
  }
}
```

响应字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| run_id | string | 本次抓取任务 ID |
| status | string | 任务状态，第一版可返回 completed/failed |
| message | string | 任务说明 |
| received_items | int | 抓取和筛选后的候选数量 |
| created_news_count | int | 实际写入资讯数量，dry_run=true 时应为 0 |
| created_topic_count | int | 实际生成选题数量，dry_run=true 时应为 0 |
| skipped_count | int | 去重、低分、来源不可信等原因跳过的数量 |
| failed_sources | array[string] | 抓取失败的来源说明 |
| preview_items | array | 预览候选资讯列表 |
| config_summary | object | 本次任务配置摘要，方便确认前端传参和分类匹配数量 |

可能错误：

| code | HTTP 状态码 | message | 说明 |
|---|---|---|---|
| 400 | 400 | invalid ai digest config | 请求参数不合法 |
| 401 | 401 | token invalid | 未登录或 token 失效 |
| 422 | 422 | validation error | 字段类型或枚举值错误 |
| 500 | 500 | ai digest run failed | 抓取或模型调用失败 |

后端实现建议：

```text
1. 校验请求参数
2. 读取当前启用分类列表
3. 根据 skill_name 找到 ai-news-blogger-digest 工作流规则
4. 抓取官方源、媒体源、社区源、GitHub、arXiv 等来源
5. 对候选资讯去重、过滤低可信来源
6. 调用 OpenAI-compatible 大模型生成摘要、评分、分类匹配
7. dry_run=true：只返回 preview_items
8. dry_run=false：写入 news 表，必要时写入 topics 表
9. 返回入库统计、跳过统计和失败来源
```

安全注意：

- 不要把 `api_key` 写入数据库日志；
- 生产环境更推荐后端从 `.env` 读取 API Key；
- 不要让大模型直接决定执行 SQL；
- 抓取失败的来源要返回到 `failed_sources`，不要伪造内容；
- 重大资讯必须保留 `source_url`，方便人工复核。

---

## 10. 健康检查

## 10.1 服务健康检查

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

## 11. 前端联调约定

## 11.1 Token 存储

前端登录成功后，将 token 存入：

```text
localStorage.access_token
```

## 11.2 Axios 请求拦截器

每次请求自动加：

```http
Authorization: Bearer <token>
```

## 11.3 登录失效处理

如果后端返回：

```json
{
  "code": 401,
  "message": "token invalid",
  "data": null
}
```

前端处理：

1. 清除 localStorage token；
2. 跳转登录页；
3. 提示用户重新登录。

---

## 12. 接口开发优先级

按照下面顺序开发，方便前后端联调：

```text
1. GET /health
2. POST /auth/register
3. POST /auth/login
4. GET /auth/me
5. GET /categories
6. POST /categories
7. GET /tags
8. POST /tags
9. POST /news
10. GET /news
11. GET /news/{id}
12. PUT /news/{id}
13. DELETE /news/{id}
14. PATCH /news/{id}/favorite
15. POST /news/{id}/to-topic
16. POST /topics
17. GET /topics
18. GET /topics/{id}
19. PUT /topics/{id}
20. PATCH /topics/{id}/status
21. DELETE /topics/{id}
22. GET /dashboard/overview
23. POST /ai-digest/runs
```

---

## 13. 最小联调闭环

当前后端实现以下接口时，前端就可以做第一轮联调：

```text
POST /auth/register
POST /auth/login
GET /auth/me
GET /categories
GET /tags
POST /news
GET /news
POST /news/{news_id}/to-topic
GET /topics
GET /dashboard/overview
```

这一组接口可以打通：

```text
注册 → 登录 → 新增资讯 → 查看资讯列表 → 加入选题池 → 查看选题列表 → 查看首页统计
```
