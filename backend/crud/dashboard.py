from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News
from models.topics import Topic


async def get_dashboard_overview_crud(db: AsyncSession):
    news_total = await db.scalar(
        select(func.count()).select_from(News).where(News.is_deleted == False)
    )
    unread_news_total = await db.scalar(
        select(func.count()).select_from(News).where(
            News.is_deleted == False,
            News.status == "unread",
        )
    )
    favorite_news_total = await db.scalar(
        select(func.count()).select_from(News).where(
            News.is_deleted == False,
            News.is_favorite == True,
        )
    )

    topic_total = await db.scalar(
        select(func.count()).select_from(Topic).where(Topic.is_deleted == False)
    )
    pending_topic_total = await db.scalar(
        select(func.count()).select_from(Topic).where(
            Topic.is_deleted == False,
            Topic.status == "pending",
        )
    )
    writing_topic_total = await db.scalar(
        select(func.count()).select_from(Topic).where(
            Topic.is_deleted == False,
            Topic.status == "writing",
        )
    )
    published_topic_total = await db.scalar(
        select(func.count()).select_from(Topic).where(
            Topic.is_deleted == False,
            Topic.status == "published",
        )
    )

    recent_news_result = await db.execute(
        select(News)
        .where(News.is_deleted == False)
        .order_by(News.created_at.desc())
        .limit(5)
    )
    recent_topics_result = await db.execute(
        select(Topic)
        .where(Topic.is_deleted == False)
        .order_by(Topic.created_at.desc())
        .limit(5)
    )

    return {
        "news_total": news_total or 0,
        "unread_news_total": unread_news_total or 0,
        "favorite_news_total": favorite_news_total or 0,
        "topic_total": topic_total or 0,
        "pending_topic_total": pending_topic_total or 0,
        "writing_topic_total": writing_topic_total or 0,
        "published_topic_total": published_topic_total or 0,
        "recent_news": recent_news_result.scalars().all(),
        "recent_topics": recent_topics_result.scalars().all(),
    }
