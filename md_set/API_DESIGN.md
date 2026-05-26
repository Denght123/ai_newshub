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

## 9. 健康检查

## 9.1 服务健康检查

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

## 10. 前端联调约定

## 10.1 Token 存储

前端登录成功后，将 token 存入：

```text
localStorage.access_token
```

## 10.2 Axios 请求拦截器

每次请求自动加：

```http
Authorization: Bearer <token>
```

## 10.3 登录失效处理

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

## 11. 接口开发优先级

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
```

---

## 12. 最小联调闭环

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
