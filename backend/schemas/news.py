from datetime import datetime

from pydantic import BaseModel, Field


class CreateNewsRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    source_name: str | None = Field(default=None, max_length=100)
    source_url: str | None = Field(default=None, max_length=500)
    summary: str | None = None
    content: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)
    status: str = "unread"
    importance_score: int = Field(default=3, ge=1, le=5)
    heat_score: int = Field(default=3, ge=1, le=5)
    publish_time: datetime | None = None


class UpdateNewsRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    source_name: str | None = Field(default=None, max_length=100)
    source_url: str | None = Field(default=None, max_length=500)
    summary: str | None = None
    content: str | None = None
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)
    status: str = "unread"
    importance_score: int = Field(default=3, ge=1, le=5)
    heat_score: int = Field(default=3, ge=1, le=5)
    publish_time: datetime | None = None


class FavoriteNewsRequest(BaseModel):
    is_favorite: bool


class NewsToTopicRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    angle: str | None = None
    recommended_title: str | None = Field(default=None, max_length=200)
    reason: str | None = None
    target_reader: str | None = Field(default=None, max_length=100)
    category_id: int | None = None
    value_score: int = Field(default=3, ge=1, le=5)
    difficulty_score: int = Field(default=3, ge=1, le=5)
    traffic_score: int = Field(default=3, ge=1, le=5)
    deadline: datetime | None = None


class NewsCategoryResponse(BaseModel):
    id: int
    name: str


class NewsTagResponse(BaseModel):
    id: int
    name: str


class NewsCreatorResponse(BaseModel):
    id: int
    username: str


class NewsListItemResponse(BaseModel):
    id: int
    title: str
    source_name: str | None = None
    category: NewsCategoryResponse | None = None
    tags: list[NewsTagResponse] = Field(default_factory=list)
    status: str
    importance_score: int
    heat_score: int
    is_favorite: bool
    publish_time: datetime | None = None
    created_at: datetime


class NewsDetailResponse(NewsListItemResponse):
    source_url: str | None = None
    summary: str | None = None
    content: str | None = None
    created_by: NewsCreatorResponse | None = None
    updated_at: datetime


class NewsListResponse(BaseModel):
    items: list[NewsListItemResponse]
    total: int
    page: int
    page_size: int
    pages: int


class UpdateNewsResponse(BaseModel):
    id: int
    title: str


class FavoriteNewsResponse(BaseModel):
    id: int
    is_favorite: bool


class NewsToTopicResponse(BaseModel):
    id: int
    news_id: int | None = None
    title: str
    status: str
