import asyncio
import json
import math
import os
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import datetime
from typing import Any, TypedDict, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.knowledge_documents import KnowledgeDocument
from models.rag_chat_messages import RagChatMessage
from models.rag_chat_sessions import RagChatSession
from models.rag_chunks import RagChunk
from schemas.rag_chat import RagChatAskRequest
import utils.llm_client as llm_client


class LLMRuntimeConfig(TypedDict):
    api_key: str
    api_base_url: str
    model: str


class EmbeddingRuntimeConfig(TypedDict):
    api_key: str
    api_base_url: str
    model: str


class RagMatchedRow(TypedDict):
    chunk: RagChunk
    document: KnowledgeDocument
    score: float


JsonDict = dict[str, Any]
ChatCall = Callable[..., Awaitable[object]]
StreamChatCall = Callable[..., AsyncIterator[str]]
EmbeddingCall = Callable[..., Awaitable[list[list[float]]]]


# 从 llm_client 模块里获取普通调用函数，避免 Pylance 对模块属性产生误报。
def get_chat_call() -> ChatCall:
    return cast(ChatCall, getattr(llm_client, "call_openai_compatible_chat"))


# 从 llm_client 模块里获取流式调用函数，避免 Pylance 对模块属性产生误报。
def get_stream_chat_call() -> StreamChatCall:
    return cast(StreamChatCall, getattr(llm_client, "stream_openai_compatible_chat"))


# 从 llm_client 模块里获取 embedding 函数，用于语义向量检索。
def get_embedding_call() -> EmbeddingCall:
    return cast(EmbeddingCall, getattr(llm_client, "call_openai_compatible_embeddings"))


# 用用户问题生成会话标题，方便左侧历史列表展示。
def build_session_title(question: str) -> str:
    title = re.sub(r"\s+", " ", question).strip()
    if len(title) > 28:
        return f"{title[:28]}..."
    return title or "新的 AI 问答"


# 把会话 ORM 对象整理成前端列表需要的格式。
def chat_session_to_dict(session: RagChatSession) -> JsonDict:
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }


# 把消息 ORM 对象整理成前端聊天记录需要的格式。
def chat_message_to_dict(message: RagChatMessage) -> JsonDict:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "metadata": message.message_metadata,
        "created_at": message.created_at.isoformat(),
    }


# 查询当前用户的一条会话；查不到或已删除时返回 None。
async def get_user_chat_session(
    session_id: int | None,
    db: AsyncSession,
    current_user_id: int,
) -> RagChatSession | None:
    if not session_id:
        return None

    stmt = select(RagChatSession).where(
        RagChatSession.id == session_id,
        RagChatSession.user_id == current_user_id,
        RagChatSession.is_deleted.is_(False),
    )
    result = await db.execute(stmt)
    return result.scalars().first()


# 获取已有会话；如果前端没有传 session_id，就根据本次问题创建新会话。
async def get_or_create_chat_session(
    ask_data: RagChatAskRequest,
    db: AsyncSession,
    current_user_id: int,
) -> RagChatSession:
    session = await get_user_chat_session(ask_data.session_id, db, current_user_id)
    if session:
        return session

    session = RagChatSession(
        user_id=current_user_id,
        title=build_session_title(ask_data.question),
    )
    db.add(session)
    await db.flush()
    return session


# 往会话里追加一条消息。
async def add_chat_message(
    db: AsyncSession,
    session_id: int,
    current_user_id: int,
    role: str,
    content: str,
    metadata: JsonDict | None = None,
) -> RagChatMessage:
    message = RagChatMessage(
        session_id=session_id,
        user_id=current_user_id,
        role=role,
        content=content,
        message_metadata=metadata,
    )
    db.add(message)
    return message


# 更新会话更新时间，让最近有新问答的会话排在历史列表前面。
def touch_chat_session(session: RagChatSession) -> None:
    session.updated_at = datetime.now()


# 从用户问题里提取用于检索的关键词。
def extract_question_keywords(question: str) -> list[str]:
    keywords: list[str] = []

    # 提取英文、数字关键词，例如 RAG、OpenAI、API、Agent。
    english_words = cast(list[str], re.findall(r"[A-Za-z0-9]+", question.lower()))
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
def calculate_match_score(
    keywords: list[str],
    chunk: RagChunk,
    document: KnowledgeDocument,
) -> float:
    score = 0.0
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
def build_matched_chunk(chunk: RagChunk, score: float) -> JsonDict:
    return {
        "chunk_id": chunk.id,
        "document_id": chunk.document_id,
        "chunk_text": chunk.chunk_text,
        "score": score,
    }


# 把知识文档整理成前端需要的引用来源格式。
def build_citation(document: KnowledgeDocument) -> JsonDict:
    return {
        "document_id": document.id,
        "title": document.title,
        "source_name": document.source_name,
        "source_url": document.source_url,
        "digest_date": document.digest_date,
    }


# 读取大模型运行配置：没有 API Key 时返回 None，调用方会走本地兜底回答。
def get_llm_runtime_config() -> LLMRuntimeConfig | None:
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


# 读取 embedding 模型配置：默认复用聊天模型的 OpenAI-compatible base url 和 key。
def get_embedding_runtime_config() -> EmbeddingRuntimeConfig | None:
    api_key = os.getenv("OPENAI_EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base_url = (
        os.getenv("OPENAI_EMBEDDING_API_BASE_URL")
        or os.getenv("OPENAI_API_BASE_URL")
        or "https://api.openai.com/v1"
    )
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    if not api_key:
        return None

    return {
        "api_key": api_key,
        "api_base_url": api_base_url,
        "model": model,
    }


# 把数据库 JSON 里的 embedding 转成 float 列表，格式不对就返回 None。
def normalize_embedding(value: object) -> list[float] | None:
    if not isinstance(value, list):
        return None

    raw_items = cast(list[object], value)
    embedding: list[float] = []
    for item in raw_items:
        if not isinstance(item, int | float):
            return None
        embedding.append(float(item))

    return embedding or None


# 计算两个向量的余弦相似度，越接近 1 代表语义越接近。
def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0

    dot = 0.0
    left_square_sum = 0.0
    right_square_sum = 0.0

    for left_value, right_value in zip(left, right):
        dot += left_value * right_value
        left_square_sum += left_value * left_value
        right_square_sum += right_value * right_value

    left_norm = math.sqrt(left_square_sum)
    right_norm = math.sqrt(right_square_sum)
    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


# 调用 embedding 模型，把用户问题转成查询向量；失败时返回 None，后续走关键词兜底。
async def create_query_embedding(question: str) -> list[float] | None:
    embedding_config = get_embedding_runtime_config()
    if not embedding_config:
        return None

    try:
        embedding_call = get_embedding_call()
        embeddings = await embedding_call(
            api_base_url=embedding_config["api_base_url"],
            api_key=embedding_config["api_key"],
            model=embedding_config["model"],
            texts=[question],
        )
    except Exception:
        return None

    if not embeddings:
        return None

    return embeddings[0]


# 对旧数据做懒加载补向量：第一次问答命中旧 chunk 时，顺手把 embedding 补进数据库。
async def backfill_missing_embeddings(
    rows: list[tuple[RagChunk, KnowledgeDocument]],
    db: AsyncSession,
    limit: int = 80,
) -> None:
    embedding_config = get_embedding_runtime_config()
    if not embedding_config:
        return

    missing_chunks: list[RagChunk] = []
    for chunk, _document in rows:
        if normalize_embedding(chunk.embedding) and chunk.embedding_model == embedding_config["model"]:
            continue
        if not chunk.chunk_text:
            continue

        missing_chunks.append(chunk)
        if len(missing_chunks) >= limit:
            break

    if not missing_chunks:
        return

    try:
        embedding_call = get_embedding_call()
        embeddings = await embedding_call(
            api_base_url=embedding_config["api_base_url"],
            api_key=embedding_config["api_key"],
            model=embedding_config["model"],
            texts=[chunk.chunk_text for chunk in missing_chunks],
        )
    except Exception:
        return

    for chunk, embedding in zip(missing_chunks, embeddings):
        chunk.embedding = embedding
        chunk.embedding_model = embedding_config["model"]

    await db.flush()
    await db.commit()


# 根据用户问题和日期范围，从 rag_chunks 表里检索相关知识片段。
async def retrieve_rag_chunks(
    ask_data: RagChatAskRequest,
    db: AsyncSession,
) -> list[RagMatchedRow]:
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
    rows = cast(list[tuple[RagChunk, KnowledgeDocument]], result.all())
    query_embedding = await create_query_embedding(ask_data.question)

    if query_embedding:
        await backfill_missing_embeddings(rows, db)

    scored_rows: list[RagMatchedRow] = []
    for chunk, document in rows:
        keyword_score = calculate_match_score(keywords, chunk, document)
        chunk_embedding = normalize_embedding(chunk.embedding)

        if query_embedding and chunk_embedding:
            semantic_score = cosine_similarity(query_embedding, chunk_embedding)
            keyword_bonus = min(keyword_score * 0.03, 0.12)
            score = semantic_score + keyword_bonus
            should_keep = score >= 0.18
        else:
            score = keyword_score
            should_keep = not keywords or keyword_score > 0

        if should_keep:
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
def build_rag_messages(
    question: str,
    matched_rows: list[RagMatchedRow],
) -> list[dict[str, str]]:
    context_lines: list[str] = []
    for index, item in enumerate(matched_rows, start=1):
        document = item["document"]
        chunk = item["chunk"]
        context_line = (
            f"{index}. 标题：{document.title}\n"
            + f"日期：{document.digest_date}\n"
            + f"来源：{document.source_name or '未知来源'}\n"
            + f"内容：{chunk.chunk_text}"
        )
        context_lines.append(context_line)

    context_text = "\n\n".join(context_lines)

    system_prompt = (
        "你是 AI NewsHub 的知识库问答助手。"
        + "你只能根据用户知识库资料回答，不要编造资料外的信息。"
        + "如果资料不足，请直接说明资料不足。"
        + "默认使用中文回答，表达要清晰、简洁。"
    )
    user_prompt = f"知识库资料：\n{context_text}\n\n用户问题：{question}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# 从 OpenAI-compatible 接口返回值中取出回答文本。
def get_answer_from_llm_response(response_json: object) -> str:
    if not isinstance(response_json, dict):
        return ""

    response_data = cast(JsonDict, response_json)
    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    choices_data = cast(list[object], choices)
    first_choice = choices_data[0]
    if not isinstance(first_choice, dict):
        return ""

    first_choice_data = cast(JsonDict, first_choice)
    message = first_choice_data.get("message")
    if not isinstance(message, dict):
        return ""

    message_data = cast(JsonDict, message)
    content = message_data.get("content")
    if not isinstance(content, str):
        return ""

    return content


# 没有配置大模型时，用命中的知识片段生成一个朴素回答，保证接口先跑通。
def build_fallback_answer(question: str, matched_rows: list[RagMatchedRow]) -> str:
    _ = question

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
async def build_rag_answer(question: str, matched_rows: list[RagMatchedRow]) -> str:
    llm_config = get_llm_runtime_config()

    if not llm_config:
        return build_fallback_answer(question, matched_rows)

    messages = build_rag_messages(question, matched_rows)
    try:
        chat_call = get_chat_call()
        response_json = await chat_call(
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
def build_rag_sources(
    matched_rows: list[RagMatchedRow],
) -> tuple[list[JsonDict], list[JsonDict]]:
    citations: list[JsonDict] = []
    matched_chunks: list[JsonDict] = []
    used_document_ids: set[int] = set()

    for item in matched_rows:
        chunk = item["chunk"]
        document = item["document"]
        score = item["score"]

        matched_chunks.append(build_matched_chunk(chunk, score))

        if document.id not in used_document_ids:
            citations.append(build_citation(document))
            used_document_ids.add(document.id)

    return citations, matched_chunks


# 查询当前用户的会话列表，左侧历史栏会使用它。
async def get_rag_chat_sessions_crud(
    db: AsyncSession,
    current_user_id: int,
) -> list[JsonDict]:
    stmt = (
        select(RagChatSession)
        .where(
            RagChatSession.user_id == current_user_id,
            RagChatSession.is_deleted.is_(False),
        )
        .order_by(RagChatSession.updated_at.desc())
        .limit(80)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return [chat_session_to_dict(session) for session in sessions]


# 查询当前用户的某个会话详情，包括消息列表。
async def get_rag_chat_session_detail_crud(
    session_id: int,
    db: AsyncSession,
    current_user_id: int,
) -> JsonDict | None:
    session = await get_user_chat_session(session_id, db, current_user_id)
    if not session:
        return None

    stmt = (
        select(RagChatMessage)
        .where(
            RagChatMessage.session_id == session.id,
            RagChatMessage.user_id == current_user_id,
        )
        .order_by(RagChatMessage.created_at.asc(), RagChatMessage.id.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return {
        **chat_session_to_dict(session),
        "messages": [chat_message_to_dict(message) for message in messages],
    }


# 软删除当前用户的某个会话；消息保留在库里，避免误删不可恢复。
async def delete_rag_chat_session_crud(
    session_id: int,
    db: AsyncSession,
    current_user_id: int,
) -> bool:
    session = await get_user_chat_session(session_id, db, current_user_id)
    if not session:
        return False

    session.is_deleted = True
    touch_chat_session(session)
    await db.commit()
    return True


# 从 OpenAI-compatible 流式 JSON 中取出增量文本。
def get_stream_delta_content(data: str) -> str:
    try:
        chunk_json = cast(object, json.loads(data))
    except json.JSONDecodeError:
        return ""

    if not isinstance(chunk_json, dict):
        return ""
    chunk_json_data = cast(JsonDict, chunk_json)

    choices = chunk_json_data.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    choices_data = cast(list[object], choices)

    first_choice = choices_data[0]
    if not isinstance(first_choice, dict):
        return ""
    first_choice_data = cast(JsonDict, first_choice)

    delta = first_choice_data.get("delta")
    if not isinstance(delta, dict):
        return ""
    delta_data = cast(JsonDict, delta)

    content = delta_data.get("content")
    if not isinstance(content, str):
        return ""

    return content


# 把一段文本按小块切开，作为没有真流式时的稳定兜底。
async def yield_text_as_sse(answer: str) -> AsyncIterator[str]:
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
) -> JsonDict:
    session = await get_or_create_chat_session(ask_data, db, current_user_id)
    matched_rows = await retrieve_rag_chunks(ask_data, db)
    answer = await build_rag_answer(ask_data.question, matched_rows)
    citations, matched_chunks = build_rag_sources(matched_rows)
    metadata = {
        "citations": citations,
        "matched_chunks": matched_chunks,
    }

    await add_chat_message(
        db=db,
        session_id=session.id,
        current_user_id=current_user_id,
        role="user",
        content=ask_data.question,
    )
    await add_chat_message(
        db=db,
        session_id=session.id,
        current_user_id=current_user_id,
        role="assistant",
        content=answer,
        metadata=metadata,
    )
    touch_chat_session(session)
    await db.commit()

    return {
        "session_id": session.id,
        "session_title": session.title,
        "answer": answer,
        "citations": citations,
        "matched_chunks": matched_chunks,
    }


# 流式 RAG 问答：有大模型配置时走真流式，没有配置或失败时走本地兜底流式。
async def stream_rag_chat_crud(
    ask_data: RagChatAskRequest,
    db: AsyncSession,
    current_user_id: int,
) -> AsyncIterator[str]:
    session = await get_or_create_chat_session(ask_data, db, current_user_id)
    await add_chat_message(
        db=db,
        session_id=session.id,
        current_user_id=current_user_id,
        role="user",
        content=ask_data.question,
    )
    touch_chat_session(session)
    await db.commit()

    matched_rows = await retrieve_rag_chunks(ask_data, db)
    citations, matched_chunks = build_rag_sources(matched_rows)
    llm_config = get_llm_runtime_config()
    answer_parts: list[str] = []

    if llm_config:
        messages = build_rag_messages(ask_data.question, matched_rows)
        sent_content = False
        try:
            stream_chat_call = get_stream_chat_call()
            async for data in stream_chat_call(
                api_base_url=llm_config["api_base_url"],
                api_key=llm_config["api_key"],
                model=llm_config["model"],
                messages=messages,
            ):
                content = get_stream_delta_content(data)
                if content:
                    sent_content = True
                    answer_parts.append(content)
                    payload = {"type": "delta", "content": content}
                    yield f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
            if not sent_content:
                fallback_answer = build_fallback_answer(ask_data.question, matched_rows)
                fallback_answer += "\n\n流式大模型没有返回正式内容，已使用本地知识库兜底回答。"
                answer_parts.append(fallback_answer)
                async for event in yield_text_as_sse(fallback_answer):
                    yield event
        except Exception as err:
            fallback_answer = build_fallback_answer(ask_data.question, matched_rows)
            fallback_answer += f"\n\n流式大模型调用失败，已使用本地知识库兜底回答：{err}"
            answer_parts.append(fallback_answer)
            async for event in yield_text_as_sse(fallback_answer):
                yield event
    else:
        fallback_answer = build_fallback_answer(ask_data.question, matched_rows)
        answer_parts.append(fallback_answer)
        async for event in yield_text_as_sse(fallback_answer):
            yield event

    answer = "".join(answer_parts)
    metadata = {
        "citations": citations,
        "matched_chunks": matched_chunks,
    }
    await add_chat_message(
        db=db,
        session_id=session.id,
        current_user_id=current_user_id,
        role="assistant",
        content=answer,
        metadata=metadata,
    )
    touch_chat_session(session)
    await db.commit()

    done_payload = {
        "type": "done",
        "session_id": session.id,
        "session_title": session.title,
        "citations": citations,
        "matched_chunks": matched_chunks,
    }
    yield f"data: {json.dumps(done_payload, ensure_ascii=False, default=str)}\n\n"
