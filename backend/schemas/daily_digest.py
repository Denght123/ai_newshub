from datetime import date

from pydantic import BaseModel, Field


class LLMConfigRequest(BaseModel):
    # 前端可以临时传模型配置；生产环境建议后端优先读取 .env。
    api_base_url: str | None = Field(default=None, max_length=500)
    api_key: str | None = Field(default=None, max_length=1000)
    model: str | None = Field(default=None, max_length=100)


class DailyDigestRunRequest(BaseModel):
    digest_date: date | None = None
    max_items: int = Field(default=30, ge=1, le=100)
    dry_run: bool = True
    llm_config: LLMConfigRequest = Field(default_factory=LLMConfigRequest)


class DailyDigestPreviewItemResponse(BaseModel):
    title: str
    summary: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    published_at: str | None = None
    credibility: str = "unknown"


class DailyDigestRunResponse(BaseModel):
    run_id: str
    status: str
    digest_date: date
    message: str
    collected_count: int = 0
    document_count: int = 0
    chunk_count: int = 0
    failed_sources: list[str] = Field(default_factory=list)
    preview_items: list[DailyDigestPreviewItemResponse] = Field(default_factory=list)


class DailyDigestRunListResponse(BaseModel):
    items: list[DailyDigestRunResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
    pages: int = 0
