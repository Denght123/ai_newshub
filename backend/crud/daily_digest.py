import asyncio
import html
import json
import os
import re
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from typing import TypedDict
from uuid import uuid4
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.daily_digest_runs import DailyDigestRun
from models.knowledge_documents import KnowledgeDocument
from models.rag_chunks import RagChunk
from schemas.daily_digest import DailyDigestRunRequest
from utils.llm_client import call_openai_compatible_chat


class RssSource(TypedDict):
    name: str
    url: str
    credibility: str


class NewsCandidate(TypedDict):
    title: str
    summary: str
    content: str
    source_name: str
    source_url: str | None
    published_at: datetime | None
    credibility: str


class LLMRuntimeConfig(TypedDict):
    api_base_url: str
    api_key: str
    model: str


REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "AI-NewsHub/1.0",
    "Accept": "application/rss+xml, application/atom+xml, text/xml, */*",
}

ARTICLE_HEADERS: dict[str, str] = {
    "User-Agent": "AI-NewsHub/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

RSS_SOURCES: list[RssSource] = [
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "credibility": "high",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "credibility": "medium",
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "credibility": "high",
    },
]

AI_KEYWORDS: list[str] = [
    "ai",
    "artificial intelligence",
    "llm",
    "gpt",
    "openai",
    "claude",
    "gemini",
    "deepmind",
    "hugging face",
    "agent",
    "rag",
    "大模型",
    "人工智能",
    "智能体",
    "知识库",
]

ARTICLE_FETCH_CONCURRENCY = 5
LLM_SUMMARY_CONCURRENCY = 3
LLM_SUMMARY_TIMEOUT_SECONDS = 60
MAX_LLM_SUMMARY_ITEMS_PER_RUN = 6


# 获取本次采集日期：前端传了日期就用前端的，否则默认今天。
def get_digest_date(run_data: DailyDigestRunRequest) -> date:
    return run_data.digest_date or date.today()


# 清洗 RSS 文本：去掉 HTML 标签、转义字符和多余空格。
def clean_text(value: str | None, max_length: int | None = None) -> str | None:
    if not value:
        return None

    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    if max_length and len(text) > max_length:
        return text[:max_length].rstrip()

    return text or None


# 解析 RSS 发布时间：RSS 和 Atom 的时间格式不完全一样，所以这里做两次尝试。
def parse_feed_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return parsedate_to_datetime(value).replace(tzinfo=None)
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except (TypeError, ValueError):
            return None


# 从 XML 节点里取指定子节点的文本，例如 title、summary、description。
def get_child_text(element: Element, names: tuple[str, ...]) -> str | None:
    for child in list(element):
        tag_name = str(child.tag).split("}")[-1]
        if tag_name in names:
            text = clean_text(child.text)
            if text:
                return text
    return None


# 从 RSS item / Atom entry 节点里取文章链接。
def get_child_link(element: Element) -> str | None:
    for child in list(element):
        tag_name = str(child.tag).split("}")[-1]
        if tag_name == "link":
            href = child.attrib.get("href")
            text = clean_text(child.text)
            return href or text
    return None


# 判断资讯是否和 AI 相关：只把相关内容沉淀到知识库里。
def is_ai_related(
    title: str | None,
    summary: str | None,
    source_name: str | None = None,
) -> bool:
    text_parts: list[str] = []
    if title:
        text_parts.append(title)
    if summary:
        text_parts.append(summary)
    if source_name:
        text_parts.append(source_name)

    search_text = " ".join(text_parts).lower()
    for keyword in AI_KEYWORDS:
        if keyword.lower() in search_text:
            return True
    return False


# 把 RSS 原始字段整理成后面入库需要的统一格式。
def build_news_item(
    title: str,
    summary: str | None,
    source_name: str,
    source_url: str | None,
    published_at: datetime | None,
    credibility: str,
) -> NewsCandidate:
    safe_title = clean_text(title, 300) or "Untitled"
    safe_summary = clean_text(summary) or "暂无摘要"

    return {
        "title": safe_title,
        "summary": safe_summary,
        "content": safe_summary,
        "source_name": source_name,
        "source_url": clean_text(source_url, 800),
        "published_at": published_at,
        "credibility": credibility,
    }


# 解析 RSS / Atom XML，把 item / entry 转成 NewsCandidate 列表。
def parse_rss_items(
    feed_text: str | bytes,
    source: RssSource,
    max_items: int,
) -> list[NewsCandidate]:
    if isinstance(feed_text, bytes):
        feed_text = feed_text.decode("utf-8", errors="replace")

    root = ElementTree.fromstring(feed_text)
    entries: list[Element] = []
    for element in root.iter():
        tag_name = str(element.tag).split("}")[-1]
        if tag_name in {"item", "entry"}:
            entries.append(element)

    items: list[NewsCandidate] = []
    for entry in entries:
        title = get_child_text(entry, ("title",))
        source_url = get_child_link(entry)
        summary = get_child_text(entry, ("description", "summary", "content"))
        published_at = parse_feed_datetime(
            get_child_text(entry, ("pubDate", "published", "updated"))
        )

        if not title:
            continue
        if not is_ai_related(title, summary, source["name"]):
            continue

        items.append(
            build_news_item(
                title=title,
                summary=summary,
                source_name=source["name"],
                source_url=source_url,
                published_at=published_at,
                credibility=source["credibility"],
            )
        )

        if len(items) >= max_items:
            break

    return items


# 请求单个 RSS 来源，并把 XML 响应解析成资讯列表。
async def fetch_rss_source(
    client: httpx.AsyncClient,
    source: RssSource,
    max_items: int,
) -> list[NewsCandidate]:
    response = await client.get(source["url"])
    response.raise_for_status()
    return parse_rss_items(response.content, source, max_items)


# 请求多个 RSS 来源：成功的资讯放到 candidates，失败的来源记录到 failed_sources。
async def fetch_ai_news_from_rss(
    max_items: int,
) -> tuple[list[NewsCandidate], list[str]]:
    candidates: list[NewsCandidate] = []
    failed_sources: list[str] = []

    timeout = httpx.Timeout(20.0, connect=8.0)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=REQUEST_HEADERS,
    ) as client:
        per_source_limit = max(1, (max_items + len(RSS_SOURCES) - 1) // len(RSS_SOURCES))
        for source in RSS_SOURCES:
            try:
                source_items = await fetch_rss_source(client, source, per_source_limit)
                candidates.extend(source_items)
            except Exception as err:
                failed_sources.append(f"{source['name']}: {err}")

            if len(candidates) >= max_items:
                break

    return dedupe_news_items(candidates, max_items), failed_sources


# 根据 source_url 请求原文网页 HTML，抓失败时返回 None，不影响 RSS 主流程。
async def fetch_article_html(
    client: httpx.AsyncClient,
    source_url: str,
) -> str | None:
    try:
        response = await client.get(source_url, headers=ARTICLE_HEADERS)
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type.lower():
        return None

    return response.text


# 从网页 HTML 中提取正文：优先找 article/main，再从常见正文容器里挑最长文本。
def extract_article_text(html_text: str) -> str | None:
    soup = BeautifulSoup(html_text, "html.parser")

    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "form", "button", "svg"]):
        tag.decompose()

    candidates: list[str] = []
    main_blocks = soup.find_all(["article", "main"])
    for block in main_blocks:
        text = clean_text(block.get_text(" ", strip=True))
        if text and len(text) >= 200:
            candidates.append(text)

    content_blocks = soup.find_all(
        ["div", "section"],
        class_=re.compile(r"(article|content|post|entry|body|prose|markdown)", re.I),
    )
    for block in content_blocks:
        text = clean_text(block.get_text(" ", strip=True))
        if text and len(text) >= 200:
            candidates.append(text)

    if not candidates:
        paragraphs = []
        for paragraph in soup.find_all("p"):
            text = clean_text(paragraph.get_text(" ", strip=True))
            if text and len(text) >= 30:
                paragraphs.append(text)

        joined_text = "\n\n".join(paragraphs)
        text = clean_text(joined_text)
        if text and len(text) >= 200:
            candidates.append(text)

    if not candidates:
        return None

    article_text = max(candidates, key=len)
    return article_text[:12000].strip()


# 用原文网页正文增强 RSS 资讯：抓到更长正文就替换 content，抓不到就保留 RSS 摘要。
async def enrich_candidate_content(
    item: NewsCandidate,
    client: httpx.AsyncClient,
) -> NewsCandidate:
    source_url = item["source_url"]
    if not source_url:
        return item

    article_html = await fetch_article_html(client, source_url)
    if not article_html:
        return item

    article_text = extract_article_text(article_html)
    if not article_text:
        return item

    if len(article_text) <= len(item["content"]):
        return item

    item["content"] = article_text
    return item


# 批量增强资讯正文：让后面写入 RAG 的内容从“摘要”升级成“原文正文”。
async def enrich_candidate_contents(
    items: list[NewsCandidate],
) -> list[NewsCandidate]:
    timeout = httpx.Timeout(20.0, connect=8.0)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=ARTICLE_HEADERS,
    ) as client:
        semaphore = asyncio.Semaphore(ARTICLE_FETCH_CONCURRENCY)

        async def enrich_with_limit(item: NewsCandidate):
            async with semaphore:
                return await enrich_candidate_content(item, client)

        enriched_items = await asyncio.gather(
            *[enrich_with_limit(item) for item in items]
        )

    return list(enriched_items)


# 获取本次采集要用的大模型配置：优先用前端传入的配置，其次读取 .env。
def get_llm_runtime_config(run_data: DailyDigestRunRequest) -> LLMRuntimeConfig | None:
    api_base_url = (
        run_data.llm_config.api_base_url
        or os.getenv("OPENAI_API_BASE_URL")
        or "https://api.openai.com/v1"
    )
    api_key = run_data.llm_config.api_key or os.getenv("OPENAI_API_KEY")
    model = run_data.llm_config.model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_base_url or not api_key:
        return None

    return {
        "api_base_url": api_base_url,
        "api_key": api_key,
        "model": model,
    }


# 构造采集总结 prompt：让模型把英文原文整理成中文摘要、要点、关键词和选题角度。
def build_digest_summary_messages(item: NewsCandidate) -> list[dict]:
    content = item["content"][:8000]
    system_prompt = (
        "你是 AI NewsHub 的资讯分析助手。"
        "你要把英文或中文 AI 资讯整理成适合中文知识库检索的结构化内容。"
        "请只返回 JSON，不要使用 Markdown 代码块。"
    )
    user_prompt = (
        "请分析下面这条 AI 资讯，并返回 JSON：\n"
        "{\n"
        '  "title_zh": "中文标题",\n'
        '  "summary": "100字以内中文摘要",\n'
        '  "key_points": ["关键要点1", "关键要点2", "关键要点3"],\n'
        '  "keywords": ["关键词1", "关键词2", "关键词3"],\n'
        '  "topic_angles": ["适合写作或提问的角度1", "角度2"],\n'
        '  "chinese_content": "用中文改写原文核心内容，保留事实、数据、产品名和机构名，不要保留英文原文"\n'
        "}\n\n"
        f"标题：{item['title']}\n"
        f"来源：{item['source_name']}\n"
        f"原文内容：{content}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# 从模型返回文本里解析 JSON：模型偶尔会包代码块，这里做一个兼容处理。
def parse_llm_json(text: str) -> dict | None:
    cleaned_text = text.strip()
    cleaned_text = cleaned_text.removeprefix("```json").removeprefix("```").removesuffix("```")
    cleaned_text = cleaned_text.strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        start_index = cleaned_text.find("{")
        end_index = cleaned_text.rfind("}")
        if start_index == -1 or end_index == -1:
            return None

        try:
            return json.loads(cleaned_text[start_index : end_index + 1])
        except json.JSONDecodeError:
            return None


# 从大模型原始响应中取出文本内容。
def get_llm_message_content(response_json: dict) -> str:
    choices = response_json.get("choices") or []
    if not choices:
        return ""

    first_choice = choices[0]
    message = first_choice.get("message") or {}
    return message.get("content") or ""


# 把模型返回的列表字段整理成字符串列表，避免模型偶尔返回字符串时循环出错。
def normalize_text_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


# 判断文本里是否有足够的中文，防止英文原文被误写进中文知识库。
def has_enough_chinese_text(value: str, min_chars: int = 20) -> bool:
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", value or "")
    return len(chinese_chars) >= min_chars


# 判断模型返回的 JSON 是否真的完成了中文化处理。
def is_chinese_summary_data(summary_data: dict) -> bool:
    summary = str(summary_data.get("summary") or "")
    chinese_content = str(summary_data.get("chinese_content") or "")
    combined_text = f"{summary}\n{chinese_content}"

    return (
        has_enough_chinese_text(summary, min_chars=8)
        and has_enough_chinese_text(combined_text, min_chars=35)
    )


# 把模型返回的结构化分析结果拼成适合写入 RAG 的正文。
def build_structured_digest_content(
    item: NewsCandidate,
    summary_data: dict,
) -> tuple[str, str, str]:
    title = str(summary_data.get("title_zh") or item["title"])
    summary = str(summary_data.get("summary") or item["summary"])
    key_points = normalize_text_list(summary_data.get("key_points"))
    keywords = normalize_text_list(summary_data.get("keywords"))
    topic_angles = normalize_text_list(summary_data.get("topic_angles"))
    chinese_content = str(summary_data.get("chinese_content") or summary)

    lines = [
        f"标题：{title}",
        f"来源：{item['source_name']}",
        f"发布日期：{item['published_at'].date() if item['published_at'] else '未知'}",
        f"中文摘要：{summary}",
        "",
        "关键要点：",
    ]

    for point in key_points:
        lines.append(f"- {point}")

    lines.append("")
    lines.append("关键词：")
    lines.append("、".join(str(keyword) for keyword in keywords) if keywords else "暂无")
    lines.append("")
    lines.append("选题/提问角度：")
    for angle in topic_angles:
        lines.append(f"- {angle}")

    lines.append("")
    lines.append("中文正文：")
    lines.append(chinese_content)

    return title, summary, "\n".join(lines)


# 调用大模型加工单条资讯：成功则替换 summary/content，失败就跳过，避免英文原文入库。
async def summarize_candidate_with_llm(
    item: NewsCandidate,
    llm_config: LLMRuntimeConfig,
) -> tuple[NewsCandidate | None, str | None]:
    messages = build_digest_summary_messages(item)

    try:
        response_json = await asyncio.wait_for(
            call_openai_compatible_chat(
                api_base_url=llm_config["api_base_url"],
                api_key=llm_config["api_key"],
                model=llm_config["model"],
                messages=messages,
            ),
            timeout=LLM_SUMMARY_TIMEOUT_SECONDS,
        )
    except Exception as err:
        return None, f"{item['title']} LLM 总结失败，已跳过入库：{err}"

    content = get_llm_message_content(response_json)
    summary_data = parse_llm_json(content)
    if not summary_data:
        return None, f"{item['title']} LLM 返回内容不是可解析 JSON，已跳过入库"

    if not is_chinese_summary_data(summary_data):
        return None, f"{item['title']} LLM 没有返回合格中文内容，已跳过入库"

    title, summary, structured_content = build_structured_digest_content(item, summary_data)
    item["title"] = title
    item["summary"] = summary
    item["content"] = structured_content
    return item, None


# 批量调用大模型加工资讯：没有中文化成功的资讯不会入库，避免 RAG 里混入英文原文。
async def summarize_candidates_with_llm(
    items: list[NewsCandidate],
    run_data: DailyDigestRunRequest,
) -> tuple[list[NewsCandidate], list[str], bool]:
    llm_config = get_llm_runtime_config(run_data)
    if not llm_config:
        return items, ["未配置大模型 API，已跳过 LLM 中文总结"], False

    summarized_items: list[NewsCandidate] = []
    failed_messages: list[str] = []
    items_to_summarize = items[:MAX_LLM_SUMMARY_ITEMS_PER_RUN]
    remaining_items = items[MAX_LLM_SUMMARY_ITEMS_PER_RUN:]
    semaphore = asyncio.Semaphore(LLM_SUMMARY_CONCURRENCY)

    async def summarize_with_limit(item: NewsCandidate):
        async with semaphore:
            return await summarize_candidate_with_llm(item, llm_config)

    summarize_results = await asyncio.gather(
        *[summarize_with_limit(item) for item in items_to_summarize]
    )

    for summarized_item, failed_message in summarize_results:
        if summarized_item:
            summarized_items.append(summarized_item)
        if failed_message:
            failed_messages.append(failed_message)

    if remaining_items:
        failed_messages.append(
            f"本次只对前 {MAX_LLM_SUMMARY_ITEMS_PER_RUN} 条资讯做 LLM 中文总结，其余资讯为避免英文入库，暂未写入知识库"
        )

    return summarized_items, failed_messages, True


# 根据 source_url 或 title 去重，避免同一条资讯被重复写入知识库。
def dedupe_news_items(
    items: list[NewsCandidate],
    max_items: int,
) -> list[NewsCandidate]:
    deduped_items: list[NewsCandidate] = []
    seen_keys: set[str] = set()

    for item in items:
        key = item.get("source_url") or item.get("title")
        if not key:
            continue
        if key in seen_keys:
            continue

        seen_keys.add(key)
        deduped_items.append(item)

        if len(deduped_items) >= max_items:
            break

    return deduped_items


# 每日采集入口：这里只抓真实 RSS，不再使用模拟数据冒充采集结果。
async def fetch_daily_digest_candidates(
    max_items: int,
) -> tuple[list[NewsCandidate], list[str], str]:
    candidates, failed_sources = await fetch_ai_news_from_rss(max_items)

    if candidates:
        enriched_candidates = await enrich_candidate_contents(candidates)
        return enriched_candidates, failed_sources, "已从真实 RSS 来源抓取 AI 资讯，并尝试补充原文正文"

    return candidates, failed_sources, "没有从 RSS 来源抓到可用 AI 资讯"


# 从候选资讯里筛出还没有写入过知识库的新资讯。
async def get_new_candidates(
    candidates: list[NewsCandidate],
    db: AsyncSession,
) -> list[NewsCandidate]:
    new_candidates: list[NewsCandidate] = []

    for item in candidates:
        existing_document_id = await get_existing_document_id(item, db)
        if not existing_document_id:
            new_candidates.append(item)

    return new_candidates


# 把一篇资讯正文切成多个 RAG 片段，后续问答会检索这些片段。
def split_text_to_chunks(text: str, chunk_size: int = 220) -> list[str]:
    clean_content = text.strip()
    if not clean_content:
        return []

    chunks: list[str] = []
    for start_index in range(0, len(clean_content), chunk_size):
        chunks.append(clean_content[start_index : start_index + chunk_size])

    return chunks


# 查询当前资讯是否已经入库：重复采集同一条 RSS 时，避免知识库出现重复数据。
async def get_existing_document(
    item: NewsCandidate,
    db: AsyncSession,
) -> KnowledgeDocument | None:
    if item["source_url"]:
        stmt = select(KnowledgeDocument).where(
            KnowledgeDocument.source_url == item["source_url"],
            KnowledgeDocument.is_deleted.is_(False),
        )
    else:
        stmt = select(KnowledgeDocument).where(
            KnowledgeDocument.title == item["title"],
            KnowledgeDocument.is_deleted.is_(False),
        )

    result = await db.execute(stmt)
    return result.scalars().first()


# 查询当前资讯是否已经入库：只返回 id，给旧调用点保持简单判断。
async def get_existing_document_id(
    item: NewsCandidate,
    db: AsyncSession,
) -> int | None:
    document = await get_existing_document(item, db)
    if not document:
        return None
    return document.id


# 粗略判断一篇文档是否已经是中文整理格式。
def is_chinese_processed_document(document: KnowledgeDocument) -> bool:
    content = document.content or ""
    if "原文正文：" in content:
        return False

    chinese_chars = re.findall(r"[\u4e00-\u9fff]", content)
    chinese_ratio = len(chinese_chars) / max(len(content), 1)

    if "中文摘要：" in content and "中文正文：" in content:
        return chinese_ratio >= 0.25

    return chinese_ratio >= 0.35


# 把已存在的知识库文档转换成 LLM 加工函数可接收的资讯格式。
def document_to_candidate(document: KnowledgeDocument) -> NewsCandidate:
    return {
        "title": document.title,
        "summary": document.summary or "暂无摘要",
        "content": document.content or document.summary or "暂无正文",
        "source_name": document.source_name or "未知来源",
        "source_url": document.source_url,
        "published_at": document.published_at,
        "credibility": document.credibility,
    }


# 删除一篇文档原来的 chunks，再按新的中文 content 重新切片。
async def rebuild_document_chunks(
    document: KnowledgeDocument,
    db: AsyncSession,
) -> int:
    await db.execute(delete(RagChunk).where(RagChunk.document_id == document.id))

    chunk_count = 0
    for chunk_index, chunk_text in enumerate(split_text_to_chunks(document.content or "")):
        chunk = RagChunk(
            document_id=document.id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            digest_date=document.digest_date,
            source_url=document.source_url,
        )
        db.add(chunk)
        chunk_count += 1

    return chunk_count


# 查询最近仍未中文化的知识库文档，用来修复之前已经入库的英文内容。
async def get_recent_unlocalized_documents(
    db: AsyncSession,
    limit: int,
) -> list[KnowledgeDocument]:
    stmt = (
        select(KnowledgeDocument)
        .where(KnowledgeDocument.is_deleted.is_(False))
        .order_by(KnowledgeDocument.created_at.desc())
        .limit(limit * 4)
    )

    result = await db.execute(stmt)
    documents = result.scalars().all()

    unlocalized_documents: list[KnowledgeDocument] = []
    for document in documents:
        if is_chinese_processed_document(document):
            continue

        unlocalized_documents.append(document)
        if len(unlocalized_documents) >= limit:
            break

    return unlocalized_documents


# 用大模型把一篇旧文档更新成中文整理版，并同步重建它的 RAG chunks。
async def localize_document_with_llm(
    document: KnowledgeDocument,
    llm_config: LLMRuntimeConfig,
    db: AsyncSession,
) -> tuple[bool, str | None]:
    candidate = document_to_candidate(document)
    summarized_item, failed_message = await summarize_candidate_with_llm(candidate, llm_config)

    if failed_message:
        return False, failed_message
    if not summarized_item:
        return False, f"{document.title} 未生成中文整理内容"

    document.title = summarized_item["title"]
    document.summary = summarized_item["summary"]
    document.content = summarized_item["content"]
    await rebuild_document_chunks(document, db)

    return True, None


# 对已经入库但仍是英文的旧文档做中文化更新。
async def localize_existing_documents(
    candidates: list[NewsCandidate],
    db: AsyncSession,
    run_data: DailyDigestRunRequest,
) -> tuple[int, list[str]]:
    llm_config = get_llm_runtime_config(run_data)
    if not llm_config:
        return 0, []

    updated_count = 0
    failed_messages: list[str] = []
    handled_document_ids: set[int] = set()

    for item in candidates[:MAX_LLM_SUMMARY_ITEMS_PER_RUN]:
        if updated_count >= MAX_LLM_SUMMARY_ITEMS_PER_RUN:
            break

        document = await get_existing_document(item, db)
        if not document:
            continue
        if document.id in handled_document_ids:
            continue
        if is_chinese_processed_document(document):
            continue

        success, failed_message = await localize_document_with_llm(document, llm_config, db)
        if failed_message:
            failed_messages.append(failed_message)
            continue

        if success:
            updated_count += 1
            handled_document_ids.add(document.id)

    remaining_limit = MAX_LLM_SUMMARY_ITEMS_PER_RUN - updated_count
    if remaining_limit <= 0:
        return updated_count, failed_messages

    recent_documents = await get_recent_unlocalized_documents(db, remaining_limit)
    for document in recent_documents:
        if document.id in handled_document_ids:
            continue

        success, failed_message = await localize_document_with_llm(document, llm_config, db)
        if failed_message:
            failed_messages.append(failed_message)
            continue

        if success:
            updated_count += 1
            handled_document_ids.add(document.id)

    return updated_count, failed_messages


# 把单条资讯写入 knowledge_documents，再把正文切片写入 rag_chunks。
async def save_candidate_to_knowledge_base(
    item: NewsCandidate,
    db: AsyncSession,
    digest_date: date,
    run_id: str,
    current_user_id: int,
) -> tuple[bool, int]:
    existing_document_id = await get_existing_document_id(item, db)
    if existing_document_id:
        return False, 0

    document = KnowledgeDocument(
        title=item["title"],
        summary=item["summary"],
        content=item["content"],
        source_name=item["source_name"],
        source_url=item["source_url"],
        published_at=item["published_at"],
        digest_date=digest_date,
        credibility=item["credibility"],
        run_id=run_id,
        created_by=current_user_id,
    )
    db.add(document)

    # flush 会把 document 先送到数据库，拿到自增 id，但不会真正提交事务。
    await db.flush()

    chunk_count = 0
    chunks = split_text_to_chunks(item["content"])
    for chunk_index, chunk_text in enumerate(chunks):
        chunk = RagChunk(
            document_id=document.id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            digest_date=digest_date,
            source_url=item["source_url"],
        )
        db.add(chunk)
        chunk_count += 1

    return True, chunk_count


# 把候选资讯转成前端预览格式：dry_run 和真正入库后的返回都用它。
def build_preview_items(candidates: list[NewsCandidate]) -> list[dict]:
    preview_items: list[dict] = []

    for item in candidates:
        published_at = item["published_at"]
        preview_items.append(
            {
                "title": item["title"],
                "summary": item["summary"],
                "source_name": item["source_name"],
                "source_url": item["source_url"],
                "published_at": published_at.isoformat() if published_at else None,
                "credibility": item["credibility"],
            }
        )

    return preview_items


# 创建一次每日采集任务：dry_run=True 只预览，dry_run=False 才真正写入知识库。
async def create_daily_digest_run_crud(
    run_data: DailyDigestRunRequest,
    db: AsyncSession,
    current_user_id: int,
) -> dict:
    digest_date = get_digest_date(run_data)
    run_id = f"run-{uuid4().hex[:12]}"
    candidates, failed_sources, collect_message = await fetch_daily_digest_candidates(
        run_data.max_items,
    )

    if run_data.dry_run:
        preview_candidates = candidates
        llm_config = get_llm_runtime_config(run_data)

        if llm_config and candidates:
            preview_candidates, llm_failed_messages, used_llm = await summarize_candidates_with_llm(
                candidates,
                run_data,
            )
            failed_sources.extend(llm_failed_messages)
            if used_llm:
                collect_message += "，dry_run 已生成中文预览，但不会写入数据库"
        elif candidates:
            failed_sources.append("dry_run 未配置大模型 API，仅能预览 RSS 原文，无法转换成中文")

        preview_items = build_preview_items(preview_candidates)
        return {
            "run_id": run_id,
            "status": "preview",
            "digest_date": digest_date,
            "message": f"dry_run=true：本次只预览真实 RSS 结果，不写入数据库。{collect_message}",
            "collected_count": len(candidates),
            "document_count": 0,
            "chunk_count": 0,
            "failed_sources": failed_sources,
            "preview_items": preview_items,
        }

    new_candidates = await get_new_candidates(candidates, db)
    summarized_candidates: list[NewsCandidate] = []
    llm_config = get_llm_runtime_config(run_data)

    if llm_config and new_candidates:
        summarized_candidates, llm_failed_messages, used_llm = await summarize_candidates_with_llm(
            new_candidates,
            run_data,
        )
        failed_sources.extend(llm_failed_messages)
        if used_llm:
            collect_message += "，新入库资讯已完成 LLM 中文摘要加工"
    elif new_candidates:
        failed_sources.append("未配置大模型 API，为避免英文原文入库，本次未写入新资讯")

    localized_existing_count, localize_failed_messages = await localize_existing_documents(
        candidates,
        db,
        run_data,
    )
    failed_sources.extend(localize_failed_messages)
    if localized_existing_count:
        collect_message += f"，已将 {localized_existing_count} 篇旧英文文档更新为中文整理版"

    preview_items = build_preview_items(summarized_candidates)
    status = "completed" if candidates else "empty"
    digest_run = DailyDigestRun(
        run_id=run_id,
        digest_date=digest_date,
        status=status,
        message=collect_message,
        collected_count=len(candidates),
        document_count=0,
        chunk_count=0,
        failed_sources=failed_sources,
        created_by=current_user_id,
    )
    db.add(digest_run)

    document_count = 0
    chunk_count = 0
    for item in summarized_candidates:
        saved_document, saved_chunk_count = await save_candidate_to_knowledge_base(
            item=item,
            db=db,
            digest_date=digest_date,
            run_id=run_id,
            current_user_id=current_user_id,
        )
        if saved_document:
            document_count += 1
        chunk_count += saved_chunk_count

    digest_run.document_count = document_count
    digest_run.chunk_count = chunk_count

    await db.commit()
    await db.refresh(digest_run)

    return {
        "run_id": digest_run.run_id,
        "status": digest_run.status,
        "digest_date": digest_run.digest_date,
        "message": digest_run.message or "success",
        "collected_count": digest_run.collected_count,
        "document_count": digest_run.document_count,
        "chunk_count": digest_run.chunk_count,
        "failed_sources": digest_run.failed_sources or [],
        "preview_items": preview_items,
    }


# 查询每日采集任务列表：给前端展示历史采集记录。
async def get_daily_digest_runs_crud(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    stmt = (
        select(DailyDigestRun)
        .order_by(DailyDigestRun.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    total_stmt = select(func.count()).select_from(DailyDigestRun)

    result = await db.execute(stmt)
    total_result = await db.execute(total_stmt)
    runs = result.scalars().all()
    total = total_result.scalar_one()

    items: list[dict] = []
    for run in runs:
        items.append(
            {
                "run_id": run.run_id,
                "status": run.status,
                "digest_date": run.digest_date,
                "message": run.message or "",
                "collected_count": run.collected_count,
                "document_count": run.document_count,
                "chunk_count": run.chunk_count,
                "failed_sources": run.failed_sources or [],
                "preview_items": [],
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total else 0,
    }
