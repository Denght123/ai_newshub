# AI NewsHub 后端学习笔记

更新时间：2026-05-12

## 当前进度

前端已经完成，目前进入后端开发学习阶段。

当前后端已经完成：

1. 创建并保留唯一后端虚拟环境：`backend/.venv`
2. 配置异步数据库连接文件：`backend/configs/db_configs.py`
3. 安装数据库相关依赖：`sqlalchemy`、`aiomysql`、`pymysql`、`alembic`
4. 根据设计文档创建 ORM 模型：
   - `models/base.py`
   - `models/users.py`
   - `models/categories.py`
   - `models/tags.py`
   - `models/news.py`
   - `models/topics.py`
   - `models/__init__.py`
5. 初始化 Alembic：
   - `backend/alembic.ini`
   - `backend/alembic/env.py`
   - `backend/alembic/versions/`
6. 成功生成初始迁移文件：
   - `backend/alembic/versions/bb1237c89332_create_initial_tables.py`

当前 ORM 已能识别这些表：

```text
categories
news
news_tags
tags
topics
users
```

下一步要执行：

```powershell
cd G:\fastapi_test\ai_newshub\backend
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

然后进入 MySQL 检查：

```sql
USE Deng;
SHOW TABLES;
```

预期应该看到：

```text
alembic_version
categories
news
news_tags
tags
topics
users
```

---

## 虚拟环境问题

项目里曾经同时存在两个虚拟环境：

```text
G:\fastapi_test\ai_newshub\.venv
G:\fastapi_test\ai_newshub\backend\.venv
```

这会导致 VS Code / Pylance / pip 安装依赖时混乱。

最终决定：

```text
只保留 backend/.venv
```

删除根目录 `.venv`：

```powershell
cd G:\fastapi_test\ai_newshub
Remove-Item -Recurse -Force .venv
```

检查结果：

```powershell
Test-Path .venv
Test-Path backend\.venv
```

预期：

```text
False
True
```

---

## VS Code 飘红问题

问题表现：

```text
无法解析导入 "sqlalchemy"
无法解析导入 "sqlalchemy.orm"
无法解析导入 "sqlalchemy.ext.asyncio"
```

实际原因：

```text
不是代码错，也不是依赖没装，而是 Pylance 没正确识别 backend/.venv。
```

验证依赖是否真的存在：

```powershell
cd G:\fastapi_test\ai_newshub\backend
.\.venv\Scripts\python.exe -c "import sqlalchemy; import sqlalchemy.orm; print(sqlalchemy.__version__)"
```

成功输出：

```text
2.0.49
```

为了解决 Pylance 识别问题，添加了：

```text
G:\fastapi_test\ai_newshub\.vscode\settings.json
G:\fastapi_test\ai_newshub\backend\.vscode\settings.json
G:\fastapi_test\ai_newshub\pyrightconfig.json
G:\fastapi_test\ai_newshub\backend\pyrightconfig.json
```

核心作用：

```text
明确告诉 VS Code / Pylance 使用 backend/.venv 作为 Python 解释器。
```

如果仍然飘红，需要执行：

```text
Ctrl + Shift + P
Developer: Reload Window
```

或：

```text
Ctrl + Shift + P
Pylance: Restart Language Server
```

手动选择解释器：

```text
Python: Select Interpreter
G:\fastapi_test\ai_newshub\backend\.venv\Scripts\python.exe
```

---

## Git 问题

问题表现：

执行：

```powershell
git add .
```

终端疯狂输出：

```text
warning: LF will be replaced by CRLF in backend/.venv/Lib/site-packages/...
```

原因：

```text
项目根目录没有 .gitignore，Git 把 backend/.venv、frontend/node_modules、frontend/dist 等依赖和构建产物也尝试加入版本管理。
```

解决：

新增 `.gitignore`，忽略：

```text
backend/.venv/
frontend/node_modules/
frontend/dist/
__pycache__/
.env
```

检查忽略是否生效：

```powershell
git status --short --ignored
```

看到：

```text
!! backend/.venv/
!! frontend/node_modules/
!! frontend/dist/
```

说明忽略成功。

学习结论：

```text
虚拟环境、node_modules、dist、缓存文件不要提交到 Git。
```

---

## MySQL 与 Docker 取舍

一开始尝试使用 Docker Compose 启动 MySQL：

```powershell
docker compose up -d
```

遇到镜像下载失败：

```text
failed size validation
```

原因：

```text
Docker Hub 镜像在当前网络环境下下载不稳定。
```

最终决定：

```text
暂时不用 Docker 跑 MySQL，改用本机安装的 MySQL 8。
```

重要理解：

```text
Docker 不依赖本机安装 MySQL。
Docker 会通过 image: mysql:8.0 创建一个独立 MySQL 容器。
```

但当前为了学习 ORM 和 Alembic，使用本机 MySQL 更直接。

---

## MySQL 命令问题

问题表现：

```powershell
mysql -u root -p
```

报错：

```text
无法将“mysql”项识别为 cmdlet、函数、脚本文件或可运行程序的名称
```

原因：

```text
MySQL 已安装，但 mysql.exe 没有加入 PATH，或者当前 PowerShell 还没有刷新 PATH。
```

可以用完整路径运行：

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

检查路径是否存在：

```powershell
Test-Path "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
```

---

## SQLAlchemy 异步连接配置

后端业务代码选择使用异步 SQLAlchemy。

安装依赖：

```powershell
python -m pip install sqlalchemy aiomysql alembic pymysql
```

几个库的作用：

```text
sqlalchemy：ORM 和数据库操作核心库
aiomysql：业务代码中连接 MySQL 的异步驱动
pymysql：Alembic 迁移时使用的同步 MySQL 驱动
alembic：数据库迁移工具
```

`aiomysql` 和 `asyncmy` 都是异步 MySQL 驱动。

当前选择：

```text
业务代码使用 aiomysql
Alembic 迁移使用 pymysql
```

原因：

```text
Alembic 默认迁移模板是同步流程，用 pymysql 最简单稳定。
```

业务连接串格式：

```text
mysql+aiomysql://root:密码@localhost:3306/Deng?charset=utf8mb4
```

Alembic 连接串格式：

```text
mysql+pymysql://root:<MYSQL_PASSWORD>@localhost:3306/Deng?charset=utf8mb4
```

---

## ORM 模型层

模型文件已经写在：

```text
backend/models/
```

文件职责：

```text
base.py：定义所有 ORM 模型共同继承的 Base
users.py：users 用户表
categories.py：categories 分类表
tags.py：tags 标签表
news.py：news 资讯表和 news_tags 多对多关联表
topics.py：topics 选题表
__init__.py：集中导入所有模型，方便 Alembic 识别
```

模型采用 SQLAlchemy 2.x 风格：

```python
Mapped
mapped_column
relationship
```

为什么使用 `TYPE_CHECKING`：

```text
模型之间有相互关系引用，例如 User -> News，News -> Tag。
如果直接相互 import，容易循环导入。
使用 TYPE_CHECKING 可以让编辑器知道类型，同时运行时不执行这些导入。
```

验证模型能否正常导入：

```powershell
cd G:\fastapi_test\ai_newshub\backend
.\.venv\Scripts\python.exe -c "import models; print(sorted(models.Base.metadata.tables.keys()))"
```

预期输出：

```text
['categories', 'news', 'news_tags', 'tags', 'topics', 'users']
```

验证 SQLAlchemy mapper：

```powershell
.\.venv\Scripts\python.exe -c "import models; from sqlalchemy.orm import configure_mappers; configure_mappers(); print('mappers ok')"
```

---

## Alembic 建表流程

Alembic 的作用：

```text
读取 ORM 模型 -> 生成迁移文件 -> 执行迁移 -> 在 MySQL 中真正建表
```

初始化命令：

```powershell
cd G:\fastapi_test\ai_newshub\backend
alembic init alembic
```

当前已经生成：

```text
backend/alembic.ini
backend/alembic/env.py
backend/alembic/versions/
```

`alembic.ini` 中配置迁移用的数据库连接：

```ini
sqlalchemy.url = mysql+pymysql://root:<MYSQL_PASSWORD>@localhost:3306/Deng?charset=utf8mb4
```

`alembic/env.py` 中配置模型元数据：

```python
from models import Base

target_metadata = Base.metadata
```

生成迁移文件：

```powershell
python -m alembic revision --autogenerate -m "create initial tables"
```

已成功生成：

```text
backend/alembic/versions/bb1237c89332_create_initial_tables.py
```

真正执行建表：

```powershell
python -m alembic upgrade head
```

---

## Alembic 遇到的问题 1：MissingGreenlet

报错：

```text
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
```

原因：

```text
alembic.ini 使用了 mysql+aiomysql 异步连接串，
但 alembic/env.py 是默认同步迁移模板。
同步迁移流程中不能直接使用异步驱动。
```

解决：

```text
业务代码继续使用 aiomysql。
Alembic 迁移改用 pymysql。
```

修改前：

```ini
sqlalchemy.url = mysql+aiomysql://root:密码@localhost:3306/Deng?charset=utf8mb4
```

修改后：

```ini
sqlalchemy.url = mysql+pymysql://root:<MYSQL_PASSWORD>@localhost:3306/Deng?charset=utf8mb4
```

---

## Alembic 遇到的问题 2：Unknown database

报错：

```text
pymysql.err.OperationalError: (1049, "Unknown database 'deng'")
```

原因：

```text
Alembic 已经能连接 MySQL 服务，但目标数据库 Deng 还不存在。
```

解决：创建数据库。

执行过的 Python 创建库命令：

```powershell
cd G:\fastapi_test\ai_newshub\backend
.\.venv\Scripts\python.exe -c "import pymysql; conn=pymysql.connect(host='localhost', port=3306, user='root', password='<MYSQL_PASSWORD>', charset='utf8mb4'); cur=conn.cursor(); cur.execute('CREATE DATABASE IF NOT EXISTS Deng CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'); cur.execute('SHOW DATABASES'); print([row[0] for row in cur.fetchall()]); cur.close(); conn.close()"
```

MySQL 显示为：

```text
deng
```

说明：

```text
Windows/MySQL 环境下数据库名大小写显示可能会变成小写，这很常见。
```

---

## 当前下一步

先执行迁移建表：

```powershell
cd G:\fastapi_test\ai_newshub\backend
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

确认表建好后，进入下一阶段：

```text
Pydantic Schema
CRUD
Service
Router
main.py 挂载 Router
/docs 调试接口
```

建议按接口文档优先级从认证模块开始：

```text
1. GET /health
2. POST /auth/register
3. POST /auth/login
4. GET /auth/me
```

认证模块推荐开发顺序：

```text
schemas/users.py
crud/users.py
services/auth_service.py
routers/auth.py
app/main.py include_router
```

记住职责划分：

```text
Schema：请求和响应数据结构
CRUD：只负责数据库增删改查
Service：处理业务逻辑，例如密码加密、重复检查、生成 token
Router：定义接口路径，接收请求，调用 Service
main.py：创建 app，并挂载 router
```
