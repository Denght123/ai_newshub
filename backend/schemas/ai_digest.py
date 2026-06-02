from typing import Literal

from pydantic import BaseModel, Field


class AIDigestRunRequest(BaseModel):
    skill_name: str = Field(default="ai-news-blogger-digest", max_length=100)
    llm_provider: str = Field(default="openai_compatible", max_length=50)
    api_base_url: str = Field(..., max_length=500)
    api_key: str | None = Field(default=None, max_length=1000)
    model: str = Field(default="gpt-4.1-mini", max_length=100)
    time_window_hours: int = Field(default=24, ge=1, le=168)
    max_items: int = Field(default=30, ge=5, le=100)
    source_profile: Literal["balanced", "minimal", "official_first", "community_hot"] = "balanced"
    category_strategy: Literal["match_existing", "fixed", "none"] = "match_existing"
    category_ids: list[int] = Field(default_factory=list)
    auto_create_missing_categories: bool = False
    create_topics: bool = True
    dry_run: bool = True
    prompt_note: str | None = Field(default=None, max_length=1000)


class AIDigestMatchedCategoryResponse(BaseModel):
    id: int
    name: str


class AIDigestPreviewItemResponse(BaseModel):
    title: str
    source_name: str | None = None
    source_url: str | None = None
    matched_category: AIDigestMatchedCategoryResponse | None = None
    importance_score: int | None = None
    heat_score: int | None = None
    one_line_summary: str | None = None


class AIDigestConfigSummaryResponse(BaseModel):
    current_user_id: int
    skill_name: str
    llm_provider: str
    api_base_url: str
    model: str
    time_window_hours: int
    max_items: int
    source_profile: str
    category_strategy: str
    matched_category_count: int
    auto_create_missing_categories: bool
    create_topics: bool
    dry_run: bool


class AIDigestRunResponse(BaseModel):
    run_id: str
    status: str
    message: str
    received_items: int = 0
    created_news_count: int = 0
    created_topic_count: int = 0
    skipped_count: int = 0
    failed_sources: list[str] = Field(default_factory=list)
    preview_items: list[AIDigestPreviewItemResponse] = Field(default_factory=list)
    config_summary: AIDigestConfigSummaryResponse | None = None
