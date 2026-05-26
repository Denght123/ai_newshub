from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.news import News
from models.tags import Tag
from models.topics import Topic
from models.users import User
from schemas.news import CreateNewsRequest, NewsToTopicRequest, UpdateNewsRequest


async def get_default_user_id(db: AsyncSession):
    result = await db.execute(select(User).order_by(User.id.asc()).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return user.id


async def create_news_crud(news_info: CreateNewsRequest, db: AsyncSession):
    created_by = await get_default_user_id(db)
    if not created_by:
        return None

    news = News(
        title=news_info.title,
        source_name=news_info.source_name,
        source_url=news_info.source_url,
        summary=news_info.summary,
        content=news_info.content,
        category_id=news_info.category_id,
        status=news_info.status,
        importance_score=news_info.importance_score,
        heat_score=news_info.heat_score,
        publish_time=news_info.publish_time,
        created_by=created_by,
    )

    if news_info.tag_ids:
        stmt = select(Tag).where(Tag.id.in_(news_info.tag_ids))
        result = await db.execute(stmt)
        news.tags = list(result.scalars().all())

    db.add(news)
    await db.commit()

    return await get_news_detail_crud(news.id, db)


async def get_news_list_crud(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    category_id: int | None = None,
    status: str | None = None,
    is_favorite: bool | None = None,
    order_by: str = "created_at",
    order: str = "desc",
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    conditions = [News.is_deleted == False]

    if keyword:
        like_keyword = f"%{keyword}%"
        conditions.append(
            or_(
                News.title.like(like_keyword),
                News.summary.like(like_keyword),
                News.source_name.like(like_keyword),
            )
        )
    if category_id is not None:
        conditions.append(News.category_id == category_id)
    if status:
        conditions.append(News.status == status)
    if is_favorite is not None:
        conditions.append(News.is_favorite == is_favorite)

    total = await db.scalar(select(func.count()).select_from(News).where(*conditions))

    allowed_order_columns = {
        "created_at": News.created_at,
        "publish_time": News.publish_time,
        "importance_score": News.importance_score,
        "heat_score": News.heat_score,
    }
    order_column = allowed_order_columns.get(order_by, News.created_at)

    stmt = (
        select(News)
        .options(selectinload(News.category), selectinload(News.tags))
        .where(*conditions)
    )
    stmt = stmt.order_by(order_column.asc() if order == "asc" else order_column.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total or 0,
        "page": page,
        "page_size": page_size,
        "pages": ((total or 0) + page_size - 1) // page_size if total else 0,
    }


async def get_news_detail_crud(news_id: int, db: AsyncSession):
    stmt = (
        select(News)
        .options(
            selectinload(News.category),
            selectinload(News.tags),
            selectinload(News.creator),
        )
        .where(News.id == news_id, News.is_deleted == False)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_news_crud(news_id: int, news_info: UpdateNewsRequest, db: AsyncSession):
    news = await get_news_detail_crud(news_id, db)
    if not news:
        return None

    news.title = news_info.title
    news.source_name = news_info.source_name
    news.source_url = news_info.source_url
    news.summary = news_info.summary
    news.content = news_info.content
    news.category_id = news_info.category_id
    news.status = news_info.status
    news.importance_score = news_info.importance_score
    news.heat_score = news_info.heat_score
    news.publish_time = news_info.publish_time

    if news_info.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(news_info.tag_ids)))
        news.tags = list(result.scalars().all())
    else:
        news.tags = []

    await db.commit()
    return await get_news_detail_crud(news_id, db)


async def delete_news_crud(news_id: int, db: AsyncSession):
    news = await get_news_detail_crud(news_id, db)
    if not news:
        return None

    news.is_deleted = True
    await db.commit()
    return news


async def update_news_favorite_crud(news_id: int, is_favorite: bool, db: AsyncSession):
    news = await get_news_detail_crud(news_id, db)
    if not news:
        return None

    news.is_favorite = is_favorite
    await db.commit()
    await db.refresh(news)
    return news


async def create_topic_from_news_crud(
    news_id: int,
    topic_info: NewsToTopicRequest,
    db: AsyncSession,
):
    news = await get_news_detail_crud(news_id, db)
    if not news:
        return None

    created_by = await get_default_user_id(db)
    if not created_by:
        return None

    topic = Topic(
        news_id=news.id,
        title=topic_info.title,
        angle=topic_info.angle,
        recommended_title=topic_info.recommended_title,
        reason=topic_info.reason,
        target_reader=topic_info.target_reader,
        category_id=topic_info.category_id or news.category_id,
        value_score=topic_info.value_score,
        difficulty_score=topic_info.difficulty_score,
        traffic_score=topic_info.traffic_score,
        deadline=topic_info.deadline,
        created_by=created_by,
    )
    news.status = "added_to_topic"
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic
