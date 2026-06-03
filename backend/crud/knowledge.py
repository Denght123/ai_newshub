from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.knowledge_documents import KnowledgeDocument


# 根据前端传来的筛选参数，统一生成 SQLAlchemy 查询条件。
def build_knowledge_filters(digest_date: date | None = None, keyword: str | None = None):
    filters = [KnowledgeDocument.is_deleted == False]

    if digest_date:
        filters.append(KnowledgeDocument.digest_date == digest_date)

    if keyword:
        like_keyword = f"%{keyword}%"
        filters.append(
            or_(
                KnowledgeDocument.title.like(like_keyword),
                KnowledgeDocument.summary.like(like_keyword),
                KnowledgeDocument.content.like(like_keyword),
                KnowledgeDocument.source_name.like(like_keyword),
            )
        )

    return filters


# 把 ORM 对象转换成列表页需要的响应数据。
def knowledge_document_to_list_item(document: KnowledgeDocument):
    return {
        "id": document.id,
        "title": document.title,
        "summary": document.summary,
        "source_name": document.source_name,
        "source_url": document.source_url,
        "published_at": document.published_at,
        "digest_date": document.digest_date,
        "credibility": document.credibility,
    }


# 把 ORM 对象转换成详情页需要的响应数据，包括正文和 RAG chunks。
def knowledge_document_to_detail(document: KnowledgeDocument):
    chunks = []
    for chunk in sorted(document.chunks, key=lambda item: item.chunk_index):
        chunks.append(
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
            }
        )

    return {
        "id": document.id,
        "title": document.title,
        "summary": document.summary,
        "source_name": document.source_name,
        "source_url": document.source_url,
        "published_at": document.published_at,
        "digest_date": document.digest_date,
        "credibility": document.credibility,
        "content": document.content,
        "chunks": chunks,
    }


# 查询知识库文档列表：支持日期筛选、关键词搜索和分页。
async def get_knowledge_documents_crud(
    db: AsyncSession,
    digest_date: date | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 10,
):
    filters = build_knowledge_filters(digest_date, keyword)
    offset_count = (page - 1) * page_size

    total_stmt = select(func.count()).select_from(KnowledgeDocument).where(*filters)
    list_stmt = (
        select(KnowledgeDocument)
        .where(*filters)
        .order_by(KnowledgeDocument.created_at.desc())
        .offset(offset_count)
        .limit(page_size)
    )

    total_result = await db.execute(total_stmt)
    list_result = await db.execute(list_stmt)

    total = total_result.scalar_one()
    documents = list_result.scalars().all()
    items = [knowledge_document_to_list_item(document) for document in documents]
    pages = (total + page_size - 1) // page_size if total else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


# 查询知识库文档详情：根据 document_id 查询单条文档，并提前加载它的 chunks。
async def get_knowledge_document_detail_crud(
    document_id: int,
    db: AsyncSession,
):
    stmt = (
        select(KnowledgeDocument)
        .options(selectinload(KnowledgeDocument.chunks))
        .where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.is_deleted == False,
        )
    )

    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        return None

    return knowledge_document_to_detail(document)
