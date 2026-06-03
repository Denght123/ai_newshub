# AI NewsHub DATABASE_DESIGN

## 1. 数据库目标

新版本数据库围绕 RAG 知识库设计，不再以分类、标签、选题池为核心。

V1 推荐新增三类表：

```text
daily_digest_runs      记录每次采集任务
knowledge_documents    记录每条入库资讯
rag_chunks             记录可检索的知识片段
```

旧表可以保留：

```text
users
news
topics
categories
tags
```

但旧表不再是新主流程必须依赖的表。

---

## 2. daily_digest_runs

用途：记录每天采集任务的执行状态。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | 任务 ID |
| run_id | varchar(80) | unique, not null | 对外展示的任务编号 |
| digest_date | date | index, not null | 采集归档日期 |
| status | varchar(30) | index, not null | reserved/running/completed/failed |
| message | varchar(500) | nullable | 任务说明 |
| collected_count | int | default 0 | 抓取候选数量 |
| document_count | int | default 0 | 入库文档数量 |
| chunk_count | int | default 0 | 入库 chunk 数量 |
| failed_sources | json | nullable | 失败来源列表 |
| created_by | bigint | FK users.id | 创建人 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

索引：

```text
unique run_id
index digest_date
index status
index created_by
```

---

## 3. knowledge_documents

用途：保存每条可被 RAG 使用的资讯文档。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | 文档 ID |
| title | varchar(300) | not null | 标题 |
| summary | text | nullable | 摘要 |
| content | longtext | nullable | RAG 使用的正文 |
| source_name | varchar(120) | nullable | 来源名称 |
| source_url | varchar(800) | nullable | 来源链接 |
| published_at | datetime | nullable | 原文发布时间 |
| digest_date | date | index, not null | 归档日期 |
| credibility | varchar(30) | index | official/media/community/paper/unknown |
| run_id | varchar(80) | index | 关联采集任务 |
| is_deleted | tinyint | default 0 | 软删除 |
| created_by | bigint | FK users.id | 入库用户 |
| created_at | datetime | not null | 入库时间 |
| updated_at | datetime | not null | 更新时间 |

索引：

```text
index digest_date
index published_at
index credibility
index run_id
index is_deleted
index created_by
```

去重建议：

```text
优先用 source_url 去重；没有 source_url 时，用 digest_date + title 去重。
```

---

## 4. rag_chunks

用途：保存文档切分后的知识片段，用于检索。

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigint | PK | chunk ID |
| document_id | bigint | FK knowledge_documents.id | 所属文档 |
| chunk_index | int | not null | 第几个片段 |
| chunk_text | text | not null | 片段内容 |
| digest_date | date | index, not null | 归档日期 |
| source_url | varchar(800) | nullable | 冗余来源链接，方便引用 |
| embedding | json / longtext | nullable | V1 预留向量字段 |
| embedding_model | varchar(100) | nullable | embedding 模型名 |
| created_at | datetime | not null | 创建时间 |

索引：

```text
index document_id
index digest_date
index chunk_index
```

V1 可以先不写 embedding，先用关键词检索跑通。

---

## 5. chat_sessions

可选表，V1 可以不做。

用途：记录问答会话。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 会话 ID |
| title | varchar(200) | 会话标题 |
| created_by | bigint | 用户 ID |
| created_at | datetime | 创建时间 |

---

## 6. chat_messages

可选表，V1 可以不做。

用途：记录问答消息。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 消息 ID |
| session_id | bigint | 会话 ID |
| role | varchar(20) | user/assistant |
| content | longtext | 消息内容 |
| citations | json | 引用来源 |
| created_at | datetime | 创建时间 |

---

## 7. ORM 开发建议

建议你后续按这个顺序写：

```text
1. models/daily_digest_runs.py
2. models/knowledge_documents.py
3. models/rag_chunks.py
4. schemas/daily_digest.py
5. schemas/knowledge.py
6. schemas/rag_chat.py
7. alembic revision --autogenerate
8. alembic upgrade head
```

注意：

1. 先不要急着上向量库；
2. 先让 MySQL 存文档和 chunk；
3. 先用关键词检索跑通问答；
4. 再补 embedding。
