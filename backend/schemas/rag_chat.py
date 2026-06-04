from datetime import date

from pydantic import BaseModel, Field


class RagChatAskRequest(BaseModel):
    session_id: int | None = None
    question: str = Field(..., min_length=1, max_length=1000)
    date_from: date | None = None
    date_to: date | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class RagCitationResponse(BaseModel):
    document_id: int | None = None
    title: str
    source_name: str | None = None
    source_url: str | None = None
    digest_date: date | None = None


class MatchedChunkResponse(BaseModel):
    chunk_id: int | None = None
    document_id: int | None = None
    chunk_text: str
    score: float | None = None


class RagChatAskResponse(BaseModel):
    session_id: int | None = None
    session_title: str | None = None
    answer: str
    citations: list[RagCitationResponse] = Field(default_factory=list)
    matched_chunks: list[MatchedChunkResponse] = Field(default_factory=list)


class RagChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str


class RagChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    metadata: dict | None = None
    created_at: str


class RagChatSessionDetailResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    messages: list[RagChatMessageResponse] = Field(default_factory=list)
