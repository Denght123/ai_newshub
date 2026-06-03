import asyncio
import json
import os
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.knowledge_documents import KnowledgeDocument
from models.rag_chunks import RagChunk
from schemas.rag_chat import RagChatAskRequest
from utils.llm_client import call_openai_compatible_chat, stream_openai_compatible_chat


# 从用户问题里提取用于检索的关键词。
def extract_question_keywords(question: str):
    keywords = []

    # 提取英文、数字关键词，例如 RAG、OpenAI、API、Agent。
    english_words = re.findall(r"[A-Za-z0-9]+", question.lower())
    for word in english_words:
        if len(word) >= 2 and word not in keywords:
            keywords.append(word)

    # 中文没有空格，先用一组常见 AI 术语做简单匹配。
    known_terms = [
        "大模型",
        "知识库",
        "检索",
        "资讯",
        "问答",
        "智能体",
        "自动化",
        "模型",
    ]
    for term in known_terms:
        if term in question and term not in keywords:
            keywords.append(term)

    return keywords


# 计算 chunk 和问题的匹配分数，分数越高越应该排在前面。
def calculate_match_score(keywords: list[str], chunk: RagChunk, document: KnowledgeDocument):
    score = 0
    search_text = ""
    search_text += chunk.chunk_text or ""
    search_text += " "
    search_text += document.title or ""
    search_text += " "
    search_text += document.summary or ""
    search_text = search_text.lower()

    for keyword in keywords:
        if keyword.lower() in search_text:
            score += 1

    return score


# 把命中的 chunk 整理成前端需要的 matched_chunks 格式。
def build_matched_chunk(chunk: RagChunk, score: float):
    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "chunk_text": chunk.chunk_text,
        "score": score,
    }


# 把知识文档整理成前端需要的引用来源格式。
def build_citation(document: KnowledgeDocument):
    return {
        "document_id": document.id,
        "title": document.title,
        "source_name": document.source_name,
        "source_url": document.source_url,
        "digest_date": document.digest_date,
    }


# 读取大模型运行配置：没有 API Key 时返回 None，调用方会走本地兜底回答。
def get_llm_runtime_config():
    api_key = os.getenv("OPENAI_API_KEY")
    api_base_url = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        return None

    return {
        "api_key": api_key,
        "api_base_url": api_base_url,
        "model": model,
    }


# 根据用户问题和日期范围，从 rag_chunks 表里检索相关知识片段。
async def retrieve_rag_chunks(ask_data: RagChatAskRequest, db: AsyncSession):
    keywords = extract_question_keywords(ask_data.question)

    stmt = (
        select(RagChunk, KnowledgeDocument)
        .join(KnowledgeDocument, RagChunk.document_id == KnowledgeDocument.id)
        .where(KnowledgeDocument.is_deleted.is_(False))
    )

    if ask_data.date_from:
        stmt = stmt.where(RagChunk.digest_date >= ask_data.date_from)

    if ask_data.date_to:
        stmt = stmt.where(RagChunk.digest_date <= ask_data.date_to)

    # V1 先不做向量检索，先取出日期范围内的 chunk，再在 Python 里算简单分数。
    stmt = stmt.order_by(RagChunk.created_at.desc()).limit(200)
    result = await db.execute(stmt)
    rows = result.all()

    scored_rows = []
    for chunk, document in rows:
        score = calculate_match_score(keywords, chunk, document)
        if not keywords or score > 0:
            scored_rows.append(
                {
                    "chunk": chunk,
                    "document": document,
                    "score": score,
                }
            )

    scored_rows.sort(key=lambda item: item["score"], reverse=True)
    return scored_rows[: ask_data.top_k]


# 根据检索到的 chunk，拼成发给大模型的 prompt。
def build_rag_messages(question: str, matched_rows: list[dict]):
    context_lines = []
    for index, item in enumerate(matched_rows, start=1):
        document = item["document"]
        chunk = item["chunk"]
        context_lines.append(
            f"{index}. 标题：{document.title}\n"
            f"日期：{document.digest_date}\n"
            f"来源：{document.source_name or '未知来源'}\n"
            f"内容：{chunk.chunk_text}"
        )

    context_text = "\n\n".join(context_lines)

    system_prompt = (
        "你是 AI NewsHub 的知识库问答助手。"
        "你只能根据用户知识库资料回答，不要编造资料外的信息。"
        "如果资料不足，请直接说明资料不足。"
        "默认使用中文回答，表达要清晰、简洁。"
    )
    user_prompt = f"知识库资料：\n{context_text}\n\n用户问题：{question}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# 从 OpenAI-compatible 接口返回值中取出回答文本。
def get_answer_from_llm_response(response_json: dict):
    choices = response_json.get("choices") or []
    if not choices:
        return ""

    first_choice = choices[0]
    message = first_choice.get("message") or {}
    return message.get("content") or ""


# 没有配置大模型时，用命中的知识片段生成一个朴素回答，保证接口先跑通。
def build_fallback_answer(question: str, matched_rows: list[dict]):
    if not matched_rows:
        return "我没有在当前知识库里检索到相关资料。你可以先运行每日采集，或扩大日期范围后再问。"

    lines = ["我先根据知识库里命中的资料给你一个简要回答："]
    for index, item in enumerate(matched_rows, start=1):
        document = item["document"]
        chunk = item["chunk"]
        lines.append(f"{index}. {document.title}：{chunk.chunk_text}")

    lines.append("以上回答来自本地 RAG 知识库，未调用外部大模型。")
    return "\n".join(lines)


# 调用大模型生成回答；如果没有配置环境变量，就退回到本地朴素回答。
async def build_rag_answer(question: str, matched_rows: list[dict]):
    llm_config = get_llm_runtime_config()

    if not llm_config:
        return build_fallback_answer(question, matched_rows)

    messages = build_rag_messages(question, matched_rows)
    try:
        response_json = await call_openai_compatible_chat(
            api_base_url=llm_config["api_base_url"],
            api_key=llm_config["api_key"],
            model=llm_config["model"],
            messages=messages,
        )
    except Exception as err:
        fallback_answer = build_fallback_answer(question, matched_rows)
        return f"{fallback_answer}\n\n大模型调用失败，已使用本地知识库兜底回答：{err}"

    answer = get_answer_from_llm_response(response_json)

    if not answer:
        return build_fallback_answer(question, matched_rows)

    return answer


# 把 RAG 命中结果整理成引用和命中片段，普通接口和流式接口都会用。
def build_rag_sources(matched_rows: list[dict]):
    citations = []
    matched_chunks = []
    used_document_ids = set()

    for item in matched_rows:
        chunk = item["chunk"]
        document = item["document"]
        score = item["score"]

        matched_chunks.append(build_matched_chunk(chunk, score))

        if document.id not in used_document_ids:
            citations.append(build_citation(document))
            used_document_ids.add(document.id)

    return citations, matched_chunks


# 从 OpenAI-compatible 流式 JSON 中取出增量文本。
def get_stream_delta_content(data: str):
    try:
        chunk_json = json.loads(data)
    except json.JSONDecodeError:
        return ""

    choices = chunk_json.get("choices") or []
    if not choices:
        return ""

    delta = choices[0].get("delta") or {}
    return delta.get("content") or ""


# 把一段文本按小块切开，作为没有真流式时的稳定兜底。
async def yield_text_as_sse(answer: str):
    chunk_size = 20
    for index in range(0, len(answer), chunk_size):
        part = answer[index : index + chunk_size]
        payload = {"type": "delta", "content": part}
        yield f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
        await asyncio.sleep(0.04)


# 普通 RAG 问答：检索知识库 chunk，然后一次性返回完整回答。
async def ask_rag_chat_crud(
    ask_data: RagChatAskRequest,
    db: AsyncSession,
    current_user_id: int,
):
    matched_rows = await retrieve_rag_chunks(ask_data, db)
    answer = await build_rag_answer(ask_data.question, matched_rows)
    citations, matched_chunks = build_rag_sources(matched_rows)

    return {
        "answer": answer,
        "citations": citations,
        "matched_chunks": matched_chunks,
    }


# 流式 RAG 问答：有大模型配置时走真流式，没有配置或失败时走本地兜底流式。
async def stream_rag_chat_crud(
    ask_data: RagChatAskRequest,
    db: AsyncSession,
    current_user_id: int,
):
    matched_rows = await retrieve_rag_chunks(ask_data, db)
    citations, matched_chunks = build_rag_sources(matched_rows)
    llm_config = get_llm_runtime_config()

    if llm_config:
        messages = build_rag_messages(ask_data.question, matched_rows)
        sent_content = False
        try:
            async for data in stream_openai_compatible_chat(
                api_base_url=llm_config["api_base_url"],
                api_key=llm_config["api_key"],
                model=llm_config["model"],
                messages=messages,
            ):
                content = get_stream_delta_content(data)
                if content:
                    sent_content = True
                    payload = {"type": "delta", "content": content}
                    yield f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
            if not sent_content:
                fallback_answer = build_fallback_answer(ask_data.question, matched_rows)
                fallback_answer += "\n\n流式大模型没有返回正式内容，已使用本地知识库兜底回答。"
                async for event in yield_text_as_sse(fallback_answer):
                    yield event
        except Exception as err:
            fallback_answer = build_fallback_answer(ask_data.question, matched_rows)
            fallback_answer += f"\n\n流式大模型调用失败，已使用本地知识库兜底回答：{err}"
            async for event in yield_text_as_sse(fallback_answer):
                yield event
    else:
        fallback_answer = build_fallback_answer(ask_data.question, matched_rows)
        async for event in yield_text_as_sse(fallback_answer):
            yield event

    done_payload = {
        "type": "done",
        "citations": citations,
        "matched_chunks": matched_chunks,
    }
    yield f"data: {json.dumps(done_payload, ensure_ascii=False, default=str)}\n\n"
