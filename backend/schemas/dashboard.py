from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class RecentNews(BaseModel):
    id:int
    title:str
    status:str
    created_at:datetime | None = None

    model_config = ConfigDict(from_attributes=True)
    

class OverviewResponse(BaseModel):
    news_total: int = 0
    unread_news_total: int = 0
    favorite_news_total: int = 0

    topic_total: int = 0
    pending_topic_total: int = 0
    writing_topic_total: int = 0
    published_topic_total: int = 0
    recent_news: list[RecentNews] =  Field(default_factory=list)
    recent_topics: list[RecentNews] =  Field(default_factory=list)

# 如果没有传recent_news和recent_topics，则返回空列表
# Field(default_factory=list)