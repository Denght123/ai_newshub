# AI NewsHub 技术选型与技术设计文档 TECH_DESIGN

## 1. 文档信息

| 项目 | 内容 |
|---|---|
| 项目名称 | AI NewsHub |
| 文档类型 | 技术选型与技术设计 |
| 前端 | Vue 3 |
| 后端 | FastAPI |
| ORM | SQLAlchemy |
| 数据库 | MySQL |
| 缓存 | Redis |
| 部署 | Docker Compose + Nginx |
| 目标 | 一个月内完成后端开发并上线 |

---

## 2. 技术目标

本项目的技术目标不是追求复杂架构，而是模拟真实工作中的小型后台系统开发流程。

核心目标：

1. 前后端分离；
2. RESTful API；
3. 后端分层清晰；
4. 数据库结构规范；
5. 支持登录鉴权；
6. 支持权限控制；
7. 支持分页、搜索、筛选；
8. 支持 Redis 缓存；
9. 支持 Docker 一键启动；
10. 支持服务器部署上线。

---

## 3. 技术选型

## 3.1 前端

| 技术 | 选择 |
|---|---|
| 框架 | Vue 3 |
| 构建工具 | Vite |
| UI 组件库 | Element Plus |
| 请求库 | Axios |
| 路由 | Vue Router |
| 状态管理 | Pinia |

说明：

前端使用 Vue 3 是为了快速搭建后台管理界面。后端只需要按照接口文档提供 API，前端可以通过 Axios 调用。

---

## 3.2 后端

| 技术 | 选择 |
|---|---|
| Web 框架 | FastAPI |
| ASGI 服务器 | Uvicorn |
| ORM | SQLAlchemy |
| 数据校验 | Pydantic |
| 配置管理 | pydantic-settings |
| 密码加密 | passlib + bcrypt |
| JWT | python-jose |
| 数据库迁移 | Alembic |
| 测试 | pytest |
| HTTP 测试 | httpx |

说明：

FastAPI 负责接口开发，SQLAlchemy 负责数据库模型和查询，Pydantic 负责请求和响应数据校验，Alembic 负责数据库表结构迁移。

---

## 3.3 数据库

| 技术 | 选择 |
|---|---|
| 数据库 | MySQL 8 |
| 字符集 | utf8mb4 |
| 排序规则 | utf8mb4_unicode_ci |

说明：

MySQL 用于存储用户、分类、标签、资讯、选题等核心业务数据。

---

## 3.4 缓存

| 技术 | 选择 |
|---|---|
| 缓存 | Redis |
| 用途 | Dashboard 统计缓存、后续可扩展 Token 黑名单和限流 |

第一版 Redis 只做一个明确场景：

```text
缓存 Dashboard 统计数据 60 秒
```

这样不会增加太多复杂度，但可以体验真实项目中的缓存使用。

---

## 3.5 部署

| 技术 | 用途 |
|---|---|
| Docker | 打包后端服务 |
| Docker Compose | 编排 FastAPI、MySQL、Redis |
| Nginx | 反向代理 |
| Linux 服务器 | 项目上线环境 |

---

## 4. 系统架构

## 4.1 整体架构

```text
Vue 前端
  ↓ HTTP / Axios
Nginx
  ↓ 反向代理
FastAPI 后端
  ↓
Service 业务层
  ↓
CRUD 数据访问层
  ↓
SQLAlchemy ORM
  ↓
MySQL

FastAPI 后端
  ↓
Redis 缓存
```

## 4.2 请求流程

以“创建资讯”为例：

```text
用户在 Vue 页面填写资讯表单
    ↓
Axios 请求 POST /api/v1/news
    ↓
FastAPI Router 接收请求
    ↓
Pydantic Schema 校验请求体
    ↓
Depends 校验当前登录用户
    ↓
Service 处理业务规则
    ↓
CRUD 写入 MySQL
    ↓
返回统一响应
```

---

## 5. 后端目录结构

推荐结构：

```text
app/
  main.py

  api/
    deps.py
    v1/
      router.py
      endpoints/
        auth.py
        categories.py
        tags.py
        news.py
        topics.py
        dashboard.py

  core/
    config.py
    security.py
    response.py
    exceptions.py

  db/
    session.py
    base.py

  models/
    user.py
    category.py
    tag.py
    news.py
    topic.py

  schemas/
    common.py
    user.py
    category.py
    tag.py
    news.py
    topic.py
    dashboard.py

  crud/
    user.py
    category.py
    tag.py
    news.py
    topic.py

  services/
    auth_service.py
    category_service.py
    tag_service.py
    news_service.py
    topic_service.py
    dashboard_service.py

  utils/
    pagination.py
    datetime.py

tests/
  test_auth.py
  test_news.py
  test_topics.py

alembic/
  versions/

Dockerfile
docker-compose.yml
.env.example
requirements.txt
README.md
```

---

## 6. 分层职责

## 6.1 Router 层

位置：

```text
app/api/v1/endpoints/
```

职责：

1. 定义接口路径；
2. 接收请求参数；
3. 调用 Service；
4. 返回统一响应；
5. 不写复杂业务逻辑。

示例：

```python
@router.post("/news")
def create_news(
    payload: NewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    news = news_service.create_news(db, payload, current_user)
    return success(data=news)
```

---

## 6.2 Schema 层

位置：

```text
app/schemas/
```

职责：

1. 定义请求体；
2. 定义响应体；
3. 做字段校验；
4. 控制返回字段，避免返回敏感数据。

常见类型：

```text
UserCreate
UserLogin
UserOut
NewsCreate
NewsUpdate
NewsOut
TopicCreate
TopicUpdate
TopicOut
```

---

## 6.3 Service 层

位置：

```text
app/services/
```

职责：

1. 处理业务逻辑；
2. 判断权限；
3. 调用多个 CRUD；
4. 处理状态流转；
5. 处理缓存。

示例：

```text
从资讯创建选题：
1. 查询资讯是否存在
2. 判断当前用户是否有权限
3. 创建选题
4. 修改资讯状态为 added_to_topic
5. 删除 Dashboard 缓存
6. 返回选题
```

---

## 6.4 CRUD 层

位置：

```text
app/crud/
```

职责：

1. 只负责数据库操作；
2. 不处理复杂业务；
3. 不关心 HTTP；
4. 不直接返回统一响应格式。

示例：

```python
def get_news_by_id(db: Session, news_id: int):
    return db.query(News).filter(
        News.id == news_id,
        News.is_deleted == False
    ).first()
```

---

## 6.5 Model 层

位置：

```text
app/models/
```

职责：

1. 定义 SQLAlchemy ORM 模型；
2. 定义字段；
3. 定义表关系；
4. 定义索引。

---

## 7. 数据库设计

## 7.1 users 表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK, auto increment | 用户 ID |
| username | varchar(50) | unique, not null | 用户名 |
| email | varchar(100) | unique, not null | 邮箱 |
| hashed_password | varchar(255) | not null | 加密密码 |
| nickname | varchar(50) | nullable | 昵称 |
| role | varchar(20) | not null | user/admin |
| is_active | tinyint | default 1 | 是否启用 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

索引：

```text
unique index username
unique index email
index role
```

---

## 7.2 categories 表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | 分类 ID |
| name | varchar(50) | unique, not null | 分类名称 |
| description | varchar(255) | nullable | 描述 |
| sort_order | int | default 0 | 排序 |
| is_active | tinyint | default 1 | 是否启用 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

---

## 7.3 tags 表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | 标签 ID |
| name | varchar(50) | unique, not null | 标签名称 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

---

## 7.4 news 表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | 资讯 ID |
| title | varchar(200) | not null | 标题 |
| source_name | varchar(100) | nullable | 来源名称 |
| source_url | varchar(500) | nullable | 原文链接 |
| summary | text | nullable | 摘要 |
| content | text | nullable | 内容笔记 |
| category_id | bigint | FK | 分类 ID |
| status | varchar(30) | not null | unread/read/added_to_topic/ignored |
| importance_score | int | default 3 | 重要程度 |
| heat_score | int | default 3 | 热度 |
| is_favorite | tinyint | default 0 | 是否收藏 |
| is_deleted | tinyint | default 0 | 是否删除 |
| publish_time | datetime | nullable | 原文发布时间 |
| created_by | bigint | FK | 创建人 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

索引：

```text
index category_id
index status
index is_favorite
index is_deleted
index created_by
index publish_time
index created_at
```

---

## 7.5 news_tags 表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| news_id | bigint | PK, FK | 资讯 ID |
| tag_id | bigint | PK, FK | 标签 ID |

说明：

这是一张多对多关联表。

---

## 7.6 topics 表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | 选题 ID |
| news_id | bigint | FK, nullable | 关联资讯 |
| title | varchar(200) | not null | 选题标题 |
| angle | text | nullable | 写作角度 |
| recommended_title | varchar(200) | nullable | 推荐公众号标题 |
| reason | text | nullable | 推荐理由 |
| target_reader | varchar(100) | nullable | 目标读者 |
| category_id | bigint | FK, nullable | 分类 ID |
| status | varchar(30) | not null | pending/selected/writing/published/abandoned |
| value_score | int | default 3 | 价值分 |
| difficulty_score | int | default 3 | 难度分 |
| traffic_score | int | default 3 | 传播潜力 |
| deadline | datetime | nullable | 计划发布时间 |
| is_deleted | tinyint | default 0 | 是否删除 |
| created_by | bigint | FK | 创建人 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

索引：

```text
index news_id
index category_id
index status
index is_deleted
index created_by
index deadline
index created_at
```

---

## 8. Redis 设计

## 8.1 Redis 使用场景

第一版只做 Dashboard 缓存。

原因：

1. 学习成本低；
2. 业务边界清晰；
3. 符合真实项目使用场景；
4. 不会让项目变复杂。

## 8.2 Key 设计

| Key | 说明 | 过期时间 |
|---|---|---|
| dashboard:overview:user:{user_id} | 普通用户仪表盘统计 | 60 秒 |
| dashboard:overview:admin:{user_id} | 管理员仪表盘统计 | 60 秒 |

## 8.3 缓存策略

读取 Dashboard：

```text
1. 先查 Redis
2. Redis 有数据，直接返回
3. Redis 没有数据，查询 MySQL
4. 查询结果写入 Redis
5. 返回结果
```

数据变更后：

```text
创建资讯
修改资讯
删除资讯
创建选题
修改选题
删除选题
```

这些操作执行后，可以删除当前用户的 Dashboard 缓存。

第一版可以简单处理：

```text
涉及资讯和选题变更时，删除当前用户 dashboard key
```

---

## 9. 鉴权设计

## 9.1 JWT 载荷

JWT payload 建议包含：

```json
{
  "sub": "用户ID",
  "username": "用户名",
  "role": "user",
  "exp": "过期时间"
}
```

## 9.2 Token 过期时间

建议：

```text
access_token 过期时间：7 天
```

第一版不做 refresh_token，避免复杂度过高。

## 9.3 Depends 依赖函数

```text
get_db
get_current_user
get_current_active_user
get_current_admin_user
```

职责：

| 函数 | 说明 |
|---|---|
| get_db | 获取数据库 Session |
| get_current_user | 解析 token，获取用户 |
| get_current_active_user | 判断用户是否启用 |
| get_current_admin_user | 判断是否管理员 |

---

## 10. 统一响应设计

## 10.1 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 10.2 分页响应

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

## 10.3 错误响应

```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

---

## 11. 异常设计

建议定义业务异常：

```python
class BusinessException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
```

常见错误码：

| code | 说明 |
|---|---|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未登录或 token 无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 数据冲突，例如用户名重复 |
| 500 | 服务器内部错误 |

---

## 12. 环境变量设计

`.env.example`：

```env
APP_NAME=AI NewsHub
APP_ENV=development
DEBUG=true

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=ai_newshub
MYSQL_PASSWORD=ai_newshub_password
MYSQL_DATABASE=ai_newshub

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

JWT_SECRET_KEY=please-change-this-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 13. Docker Compose 设计

服务：

1. backend；
2. mysql；
3. redis；
4. nginx，可选。

示例结构：

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
    env_file:
      - .env

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: ai_newshub
      MYSQL_USER: ai_newshub
      MYSQL_PASSWORD: ai_newshub_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

---

## 14. 开发流程

按照真实工作流程，建议每个功能都这样走：

```text
1. 先看 PRD，确认功能要做什么
2. 写 API 设计，确认请求和响应
3. 设计数据库字段
4. 创建 SQLAlchemy Model
5. 生成 Alembic 迁移
6. 写 Schema
7. 写 CRUD
8. 写 Service
9. 写 Router
10. 在 Swagger 调试
11. 前后端联调
12. 写简单测试
13. 提交 Git
```

---

## 15. Git 分支建议

一个人开发也建议模拟真实流程：

```text
main：稳定分支
dev：开发分支
feature/auth：认证功能
feature/news：资讯功能
feature/topics：选题功能
feature/deploy：部署功能
```

每完成一个模块，合并到 dev。

---

## 16. 测试策略

第一版测试不要求覆盖率很高，但至少覆盖核心接口。

建议测试：

```text
test_register_success
test_login_success
test_get_current_user
test_create_news
test_list_news
test_create_topic_from_news
test_dashboard_overview
```

测试目标：

1. 保证核心链路正常；
2. 避免改代码后核心接口坏掉；
3. 体验真实项目中的测试流程。

---

## 17. 部署方案

## 17.1 本地启动

```bash
docker compose up -d
```

启动后：

```text
后端：http://localhost:8000
接口文档：http://localhost:8000/docs
MySQL：localhost:3306
Redis：localhost:6379
```

## 17.2 服务器部署

推荐流程：

```text
1. 购买或使用已有 Linux 服务器
2. 安装 Docker 和 Docker Compose
3. 上传项目代码
4. 配置 .env
5. 执行 docker compose up -d
6. 执行 Alembic 数据库迁移
7. 配置 Nginx 反向代理
8. 配置安全组开放 80/443
```

## 17.3 Nginx 反向代理

示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 18. 技术风险与控制

| 风险 | 控制方式 |
|---|---|
| 功能越做越大 | 严格按 V1.0 范围做 |
| 前后端接口不一致 | 先写 API_DESIGN.md，再开发 |
| 数据库频繁改字段 | 使用 Alembic 管理迁移 |
| 权限混乱 | 统一用 Depends 做当前用户和管理员校验 |
| Redis 过度使用 | 第一版只缓存 Dashboard |
| 部署失败 | 先本地 Docker Compose 跑通，再上服务器 |

---

## 19. 技术验收标准

完成以下内容，技术上可认为 V1.0 合格：

```text
[ ] FastAPI 项目可以正常启动
[ ] /docs 可以查看完整接口
[ ] SQLAlchemy Model 完整
[ ] Alembic 可以迁移数据库
[ ] MySQL 表结构正确
[ ] JWT 登录鉴权可用
[ ] 用户权限判断可用
[ ] Redis Dashboard 缓存可用
[ ] Docker Compose 可以启动 backend/mysql/redis
[ ] 主要接口有测试
[ ] 项目成功部署到服务器
```
