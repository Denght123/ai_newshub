from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.knowledge import get_knowledge_document_detail_crud, get_knowledge_documents_crud
from schemas.knowledge import KnowledgeDocumentDetailResponse, KnowledgeDocumentListResponse
from utils.response import success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# 知识库列表接口：接收日期、关键词、分页参数，再交给 crud 查询。
@router.get("/documents")
async def get_knowledge_documents(
    digest_date: date | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    # 真实查询逻辑写在 crud/knowledge.py，这里只做接口参数转发。
    result = await get_knowledge_documents_crud(db, digest_date, keyword, page, page_size)
    response_data = KnowledgeDocumentListResponse.model_validate(result)
    return success_response(data=response_data)


# 知识库详情接口：根据文档 id 查询正文和它切出来的 RAG 片段。
@router.get("/documents/{document_id}")
async def get_knowledge_document_detail(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    result = await get_knowledge_document_detail_crud(document_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="knowledge document not found")

    response_data = KnowledgeDocumentDetailResponse.model_validate(result)
    return success_response(data=response_data)
