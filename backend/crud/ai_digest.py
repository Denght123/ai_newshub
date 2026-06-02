import asyncio
import html
import json
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from uuid import uuid4
from xml.etree import ElementTree

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.categories import Category
from models.news import News
from schemas.ai_digest import AIDigestRunRequest
from utils.llm_client import call_openai_compatible_chat


REQUEST_HEADERS = {
    "User-Agent": "AI-NewsHub/1.0",
    "Accept": "application/rss+xml, application/atom+xml, application/json, text/html, */*",
}

AI_KEYWORDS = (
    "ai",
    "artificial intelligence",
    "llm",
    "large language model",
    "gpt",
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepmind",
    "deepseek",
    "qwen",
    "kimi",
    "agent",
    "agents",
    "copilot",
    "hugging face",
    "transformer",
    "diffusion",
    "multimodal",
    "大模型",
    "人工智能",
    "智能体",
    "通义",
    "豆包",
    "智谱",
    "文心",
    "混元",
)


def get_ai_digest_api_key(run_data: AIDigestRunRequest):
    return (
        run_data.api_key
        or os.getenv("AI_DIGEST_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or ""
    ).strip()


def clean_text(value: str | None, max_length: int | None = None):
    if not value:
        return None

    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if max_length and len(text) > max_length:
        return text[:max_length].rstrip()
    return text or None


def parse_datetime(value: str | None):
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_ai_related(title: str | None, summary: str | None, source_name: str | None = None):
    haystack = " ".join(
        text for text in [title, summary, source_name] if text
    ).lower()
    return any(keyword in haystack for keyword in AI_KEYWORDS)


def get_child_text(element, names: tuple[str, ...]):
    for child in list(element):
        tag_name = child.tag.split("}")[-1]
        if tag_name in names:
            text = clean_text(child.text)
            if text:
                return text
    return None


def get_child_link(element):
    for child in list(element):
        tag_name = child.tag.split("}")[-1]
        if tag_name == "link":
            href = child.attrib.get("href")
            text = clean_text(child.text)
            return href or text
    return None


def build_raw_item(
    title: str,
    url: str | None,
    source_name: str,
    content: str | None = None,
    source_type: str | None = None,
    region: str | None = None,
    published_at: datetime | None = None,
    raw_signals: dict | None = None,
):
    return {
        "title": clean_text(title, 200),
        "url": clean_text(url, 500),
        "source_name": clean_text(source_name, 100),
        "source_type": source_type,
        "region": region,
        "published_at": published_at.isoformat() if published_at else None,
        "content": clean_text(content, 800),
        "raw_signals": raw_signals or {},
    }


def parse_feed_items(feed_text: str | bytes, source: dict, since_time: datetime, max_items: int):
    root = ElementTree.fromstring(feed_text)
    entries = [
        element
        for element in root.iter()
        if element.tag.split("}")[-1] in {"item", "entry"}
    ]

    items = []
    for entry in entries:
        title = get_child_text(entry, ("title",))
        url = get_child_link(entry)
        summary = get_child_text(entry, ("description", "summary", "content", "encoded"))
        published_at = parse_datetime(
            get_child_text(entry, ("pubDate", "published", "updated"))
        )

        if not title:
            continue
        if published_at and published_at < since_time:
            continue
        if not is_ai_related(title, summary, source["name"]):
            continue

        items.append(
            build_raw_item(
                title=title,
                url=url,
                source_name=source["name"],
                content=summary,
                source_type=source["source_type"],
                region=source["region"],
                published_at=published_at,
            )
        )
        if len(items) >= max_items:
            break

    return items


def build_feed_sources(source_profile: str):
    official_sources = [
        {
            "name": "OpenAI News",
            "url": "https://openai.com/news/rss.xml",
            "source_type": "official",
            "region": "overseas",
        },
        {
            "name": "Google AI Blog",
            "url": "https://blog.google/technology/ai/rss/",
            "source_type": "official",
            "region": "overseas",
        },
        {
            "name": "AWS Machine Learning Blog",
            "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
            "source_type": "official",
            "region": "overseas",
        },
        {
            "name": "Hugging Face Blog",
            "url": "https://huggingface.co/blog/feed.xml",
            "source_type": "official",
            "region": "global",
        },
    ]
    media_sources = [
        {
            "name": "TechCrunch AI",
            "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "source_type": "media",
            "region": "overseas",
        },
        {
            "name": "The Verge AI",
            "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "source_type": "media",
            "region": "overseas",
        },
    ]

    if source_profile == "minimal":
        return [official_sources[0], official_sources[1], media_sources[0]]
    if source_profile == "official_first":
        return official_sources + media_sources[:1]
    if source_profile == "community_hot":
        return media_sources
    return official_sources + media_sources


async def fetch_feed_source(client: httpx.AsyncClient, source: dict, since_time: datetime, max_items: int):
    response = await client.get(source["url"])
    response.raise_for_status()
    return parse_feed_items(response.content, source, since_time, max_items)


async def fetch_hacker_news(client: httpx.AsyncClient, since_time: datetime, max_items: int):
    queries = ["AI", "LLM", "OpenAI", "Claude", "Gemini", "agent"]
    items = []
    failed_sources = []

    for query in queries:
        try:
            response = await client.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "tags": "story",
                    "numericFilters": f"created_at_i>{int(since_time.timestamp())}",
                    "hitsPerPage": max(3, min(max_items, 10)),
                },
            )
            response.raise_for_status()
            data = response.json()
        except Exception as err:
            failed_sources.append(f"Hacker News {query}: {err}")
            continue

        for hit in data.get("hits", []):
            title = hit.get("title") or hit.get("story_title")
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if not title or not is_ai_related(title, url, "Hacker News"):
                continue

            items.append(
                build_raw_item(
                    title=title,
                    url=url,
                    source_name="Hacker News",
                    content=hit.get("story_text"),
                    source_type="community",
                    region="global",
                    published_at=parse_datetime(hit.get("created_at")),
                    raw_signals={
                        "points": hit.get("points"),
                        "comments": hit.get("num_comments"),
                        "hn_object_id": hit.get("objectID"),
                    },
                )
            )
            if len(items) >= max_items:
                return items, failed_sources

    return items, failed_sources


async def fetch_github_repositories(client: httpx.AsyncClient, since_time: datetime, max_items: int):
    since_date = since_time.date().isoformat()
    queries = [
        f"llm pushed:>={since_date} stars:>100",
        f"agent pushed:>={since_date} stars:>100",
        f"rag pushed:>={since_date} stars:>100",
        f"mcp pushed:>={since_date} stars:>50",
    ]
    items = []
    failed_sources = []

    for query in queries:
        try:
            response = await client.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": max(3, min(max_items, 10)),
                },
            )
            response.raise_for_status()
            data = response.json()
        except Exception as err:
            failed_sources.append(f"GitHub Search {query}: {err}")
            continue

        for repo in data.get("items", []):
            full_name = repo.get("full_name")
            description = repo.get("description")
            if not full_name or not is_ai_related(full_name, description, "GitHub"):
                continue

            items.append(
                build_raw_item(
                    title=f"{full_name} repository activity",
                    url=repo.get("html_url"),
                    source_name="GitHub Search",
                    content=description,
                    source_type="open_source",
                    region="global",
                    published_at=parse_datetime(repo.get("pushed_at")),
                    raw_signals={
                        "stars": repo.get("stargazers_count"),
                        "forks": repo.get("forks_count"),
                        "created_at": repo.get("created_at"),
                        "pushed_at": repo.get("pushed_at"),
                    },
                )
            )
            if len(items) >= max_items:
                return items, failed_sources

    return items, failed_sources


async def fetch_arxiv_papers(client: httpx.AsyncClient, since_time: datetime, max_items: int):
    response = await client.get(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": "cat:cs.AI OR cat:cs.CL OR cat:cs.LG",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max(5, min(max_items, 20)),
        },
    )
    response.raise_for_status()

    source = {
        "name": "arXiv",
        "source_type": "paper",
        "region": "global",
    }
    return parse_feed_items(response.content, source, since_time, max_items)


async def run_source_fetch(source_name: str, fetcher):
    try:
        result = await fetcher()
    except Exception as err:
        return [], [f"{source_name}: {err}"]

    if isinstance(result, tuple):
        return result
    return result, []


def dedupe_raw_items(raw_items: list[dict], max_items: int):
    deduped_items = []
    seen_keys = set()

    for item in raw_items:
        title = item.get("title")
        if not title:
            continue

        key = item.get("url") or re.sub(r"\W+", "", title.lower())
        if key in seen_keys:
            continue

        seen_keys.add(key)
        deduped_items.append(item)
        if len(deduped_items) >= max_items:
            break

    return deduped_items


async def fetch_ai_digest_raw_items(run_data: AIDigestRunRequest):
    since_time = datetime.now(timezone.utc) - timedelta(hours=run_data.time_window_hours)
    source_limit = max(3, min(run_data.max_items, 15))
    tasks = []

    timeout = httpx.Timeout(15.0, connect=8.0)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=REQUEST_HEADERS,
    ) as client:
        for source in build_feed_sources(run_data.source_profile):
            tasks.append(
                run_source_fetch(
                    source["name"],
                    lambda source=source: fetch_feed_source(
                        client,
                        source,
                        since_time,
                        source_limit,
                    ),
                )
            )

        if run_data.source_profile in {"balanced", "minimal", "community_hot"}:
            tasks.append(
                run_source_fetch(
                    "Hacker News",
                    lambda: fetch_hacker_news(client, since_time, source_limit),
                )
            )

        if run_data.source_profile in {"balanced", "minimal", "community_hot"}:
            tasks.append(
                run_source_fetch(
                    "GitHub Search",
                    lambda: fetch_github_repositories(client, since_time, source_limit),
                )
            )

        if run_data.source_profile in {"balanced", "official_first"}:
            tasks.append(
                run_source_fetch(
                    "arXiv",
                    lambda: fetch_arxiv_papers(client, since_time, source_limit),
                )
            )

        fetch_results = await asyncio.gather(*tasks)

    raw_items = []
    failed_sources = []
    for items, failures in fetch_results:
        raw_items.extend(items)
        failed_sources.extend(failures)

    return dedupe_raw_items(raw_items, run_data.max_items), failed_sources


def build_ai_digest_messages(
    raw_items: list[dict],
    categories: list[Category],
    run_data: AIDigestRunRequest,
):
    category_options = [
        {
            "id": category.id,
            "name": category.name,
        }
        for category in categories
    ]

    if run_data.category_strategy == "none":
        category_rule = "matched_category 必须返回 null。"
    elif run_data.category_strategy == "fixed":
        category_rule = "matched_category 必须使用 categories 中唯一的分类。"
    else:
        category_rule = "matched_category 只能从 categories 里选择；没有合适分类时返回 null。"

    user_content = {
        "task": "把 raw_items 中的 AI 资讯整理成 preview_items。",
        "rules": [
            "必须只返回 JSON 数组，不要返回 Markdown，不要返回解释文字。",
            "只保留真实、有来源、适合 AI 资讯内容创作的条目。",
            "title 必须改写成简体中文标题。",
            "importance_score 和 heat_score 必须是 1 到 5 的整数。",
            category_rule,
            "不要编造 source_url，只能使用 raw_items 里已有的 url；原始数据没有 URL 时返回 null。",
            "one_line_summary 用一句中文概括，不要超过 80 字。",
        ],
        "user_note": run_data.prompt_note,
        "source_profile": run_data.source_profile,
        "categories": category_options,
        "raw_items": raw_items,
        "output_item_format": {
            "title": "中文标题",
            "source_name": "来源名称",
            "source_url": "来源链接或 null",
            "matched_category": {"id": "分类ID", "name": "分类名称"},
            "importance_score": "1-5",
            "heat_score": "1-5",
            "one_line_summary": "一句话摘要",
        },
    }

    return [
        {
            "role": "system",
            "content": (
                "你是 AI 资讯整理助手，擅长根据 ai-news-blogger-digest 工作流，"
                "将多源原始资讯去重、筛选、评分、分类，并输出适合中文内容创作的结构化 JSON。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(user_content, ensure_ascii=False),
        },
    ]


def extract_json_array(text: str):
    content = text.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    start = content.find("[")
    end = content.rfind("]")
    if start != -1 and end != -1 and end > start:
        content = content[start : end + 1]

    return json.loads(content)


def clamp_score(value, default: int = 3):
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = default
    return min(max(score, 1), 5)


def normalize_matched_category(raw_category, categories: list[Category]):
    if not raw_category:
        return None

    category_id = raw_category.get("id")
    category_name = raw_category.get("name")
    category_map = {category.id: category for category in categories}

    try:
        category_id = int(category_id)
    except (TypeError, ValueError):
        category_id = None

    if category_id in category_map:
        category = category_map[category_id]
        return {
            "id": category.id,
            "name": category.name,
        }

    for category in categories:
        if category.name == category_name:
            return {
                "id": category.id,
                "name": category.name,
            }

    return None


def normalize_source_url(source_url, allowed_urls: set[str]):
    source_url = clean_text(source_url, 500)
    if not source_url:
        return None
    if source_url not in allowed_urls:
        return None
    return source_url


def normalize_preview_items(raw_preview_items, categories: list[Category], raw_items: list[dict]):
    if not isinstance(raw_preview_items, list):
        return []

    allowed_urls = {item["url"] for item in raw_items if item.get("url")}
    preview_items = []

    for item in raw_preview_items:
        if not isinstance(item, dict):
            continue

        title = clean_text(item.get("title"), 200)
        if not title:
            continue

        preview_items.append(
            {
                "title": title,
                "source_name": clean_text(item.get("source_name"), 100),
                "source_url": normalize_source_url(item.get("source_url"), allowed_urls),
                "matched_category": normalize_matched_category(
                    item.get("matched_category"),
                    categories,
                ),
                "importance_score": clamp_score(item.get("importance_score")),
                "heat_score": clamp_score(item.get("heat_score")),
                "one_line_summary": clean_text(item.get("one_line_summary"), 500),
            }
        )

    return preview_items


def build_config_summary(
    run_data: AIDigestRunRequest,
    current_user_id: int,
    categories: list[Category],
):
    return {
        "current_user_id": current_user_id,
        "skill_name": run_data.skill_name,
        "llm_provider": run_data.llm_provider,
        "api_base_url": run_data.api_base_url,
        "model": run_data.model,
        "time_window_hours": run_data.time_window_hours,
        "max_items": run_data.max_items,
        "source_profile": run_data.source_profile,
        "category_strategy": run_data.category_strategy,
        "matched_category_count": len(categories),
        "auto_create_missing_categories": run_data.auto_create_missing_categories,
        "create_topics": run_data.create_topics,
        "dry_run": run_data.dry_run,
    }


async def get_ai_digest_categories(run_data: AIDigestRunRequest, db: AsyncSession):
    if run_data.category_strategy == "none":
        return []

    stmt = select(Category).where(Category.is_active == True)
    if run_data.category_ids:
        stmt = stmt.where(Category.id.in_(run_data.category_ids))
    stmt = stmt.order_by(Category.sort_order.asc(), Category.id.desc())

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def validate_ai_digest_run(run_data: AIDigestRunRequest, db: AsyncSession):
    if not get_ai_digest_api_key(run_data):
        return "api_key is required"

    if run_data.category_strategy == "fixed" and len(run_data.category_ids) != 1:
        return "fixed category strategy requires exactly one category"

    if run_data.category_strategy != "none" and run_data.category_ids:
        categories = await get_ai_digest_categories(run_data, db)
        existing_ids = {category.id for category in categories}
        missing_ids = [
            category_id
            for category_id in run_data.category_ids
            if category_id not in existing_ids
        ]
        if missing_ids:
            return f"category ids not found or inactive: {missing_ids}"

    return None


async def create_news_from_preview_items(
    preview_items: list[dict],
    db: AsyncSession,
    current_user_id: int,
):
    created_count = 0
    skipped_count = 0

    for item in preview_items:
        title = item.get("title")
        source_url = item.get("source_url")

        if source_url:
            stmt = select(News.id).where(
                News.is_deleted == False,
                News.source_url == source_url,
            )
        else:
            stmt = select(News.id).where(
                News.is_deleted == False,
                News.title == title,
            )

        existing_news_id = await db.scalar(stmt.limit(1))
        if existing_news_id:
            skipped_count += 1
            continue

        matched_category = item.get("matched_category")
        category_id = matched_category["id"] if matched_category else None

        news = News(
            title=title,
            source_name=item.get("source_name"),
            source_url=source_url,
            summary=item.get("one_line_summary"),
            content=item.get("one_line_summary"),
            category_id=category_id,
            status="unread",
            importance_score=item.get("importance_score") or 3,
            heat_score=item.get("heat_score") or 3,
            created_by=current_user_id,
        )
        db.add(news)
        created_count += 1

    if created_count:
        await db.commit()

    return created_count, skipped_count


async def create_ai_digest_run_crud(
    run_data: AIDigestRunRequest,
    db: AsyncSession,
    current_user_id: int,
):
    categories = await get_ai_digest_categories(run_data, db)
    config_summary = build_config_summary(run_data, current_user_id, categories)
    raw_items, failed_sources = await fetch_ai_digest_raw_items(run_data)

    if not raw_items:
        return {
            "run_id": f"failed-{uuid4().hex[:12]}",
            "status": "failed",
            "message": "没有抓取到可用的 AI 资讯候选，请稍后重试或切换来源策略",
            "received_items": 0,
            "created_news_count": 0,
            "created_topic_count": 0,
            "skipped_count": 0,
            "failed_sources": failed_sources,
            "preview_items": [],
            "config_summary": config_summary,
        }

    try:
        messages = build_ai_digest_messages(raw_items, categories, run_data)
        llm_response = await call_openai_compatible_chat(
            api_base_url=run_data.api_base_url,
            api_key=get_ai_digest_api_key(run_data),
            model=run_data.model,
            messages=messages,
        )
        content = llm_response["choices"][0]["message"]["content"]
        raw_preview_items = extract_json_array(content)
        preview_items = normalize_preview_items(raw_preview_items, categories, raw_items)
    except Exception as err:
        return {
            "run_id": f"failed-{uuid4().hex[:12]}",
            "status": "failed",
            "message": f"AI 模型调用或解析失败：{err}",
            "received_items": len(raw_items),
            "created_news_count": 0,
            "created_topic_count": 0,
            "skipped_count": len(raw_items),
            "failed_sources": failed_sources + ["llm_chat_completion"],
            "preview_items": [],
            "config_summary": config_summary,
        }

    if not preview_items:
        return {
            "run_id": f"failed-{uuid4().hex[:12]}",
            "status": "failed",
            "message": "AI 模型没有返回可用的预览资讯",
            "received_items": len(raw_items),
            "created_news_count": 0,
            "created_topic_count": 0,
            "skipped_count": len(raw_items),
            "failed_sources": failed_sources + ["empty_llm_preview_items"],
            "preview_items": [],
            "config_summary": config_summary,
        }

    created_news_count = 0
    duplicated_count = 0
    if not run_data.dry_run:
        created_news_count, duplicated_count = await create_news_from_preview_items(
            preview_items,
            db,
            current_user_id,
        )

    skipped_count = max(len(raw_items) - len(preview_items), 0) + duplicated_count
    message = "AI 抓取整理完成，当前仅返回预览数据"
    if not run_data.dry_run:
        message = f"AI 抓取整理完成，已写入 {created_news_count} 条资讯"

    return {
        "run_id": f"run-{uuid4().hex[:12]}",
        "status": "completed",
        "message": message,
        "received_items": len(raw_items),
        "created_news_count": created_news_count,
        "created_topic_count": 0,
        "skipped_count": skipped_count,
        "failed_sources": failed_sources,
        "preview_items": preview_items,
        "config_summary": config_summary,
    }
