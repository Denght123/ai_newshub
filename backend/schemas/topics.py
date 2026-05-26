from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateTopicRequest(BaseModel):
    news_id: int | None = None
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


class UpdateTopicRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    angle: str | None = None
    recommended_title: str | None = Field(default=None, max_length=200)
    reason: str | None = None
    target_reader: str | None = Field(default=None, max_length=100)
    category_id: int | None = None
    status: str = "pending"
    value_score: int = Field(default=3, ge=1, le=5)
    difficulty_score: int = Field(default=3, ge=1, le=5)
    traffic_score: int = Field(default=3, ge=1, le=5)
    deadline: datetime | None = None


class UpdateTopicStatusRequest(BaseModel):
    status: str


class TopicCategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TopicNewsResponse(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class CreateTopicResponse(BaseModel):
    id: int
    title: str
    status: str
    value_score: int
    difficulty_score: int
    traffic_score: int

    model_config = ConfigDict(from_attributes=True)


class TopicListItemResponse(BaseModel):
    id: int
    title: str
    recommended_title: str | None = None
    status: str
    value_score: int
    difficulty_score: int
    traffic_score: int
    deadline: datetime | None = None
    category: TopicCategoryResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicDetailResponse(TopicListItemResponse):
    news: TopicNewsResponse | None = None
    angle: str | None = None
    reason: str | None = None
    target_reader: str | None = None
    updated_at: datetime


class TopicListResponse(BaseModel):
    items: list[TopicListItemResponse]
    total: int
    page: int
    page_size: int
    pages: int


class UpdateTopicResponse(BaseModel):
    id: int
    title: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class UpdateTopicStatusResponse(BaseModel):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
