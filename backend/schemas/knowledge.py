from datetime import date, datetime

from pydantic import BaseModel, Field


class KnowledgeChunkResponse(BaseModel):
    id: int
    chunk_index: int
    chunk_text: str


class KnowledgeDocumentListItemResponse(BaseModel):
    id: int
    title: str
    summary: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    published_at: datetime | None = None
    digest_date: date
    credibility: str = "unknown"


class KnowledgeDocumentDetailResponse(KnowledgeDocumentListItemResponse):
    content: str | None = None
    chunks: list[KnowledgeChunkResponse] = Field(default_factory=list)


class KnowledgeDocumentListResponse(BaseModel):
    items: list[KnowledgeDocumentListItemResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
    pages: int = 0
