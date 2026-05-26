from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud.news import get_default_user_id
from models.topics import Topic
from schemas.topics import CreateTopicRequest, UpdateTopicRequest


async def create_topic_crud(topic_info: CreateTopicRequest, db: AsyncSession):
    created_by = await get_default_user_id(db)
    if not created_by:
        return None

    topic = Topic(
        news_id=topic_info.news_id,
        title=topic_info.title,
        angle=topic_info.angle,
        recommended_title=topic_info.recommended_title,
        reason=topic_info.reason,
        target_reader=topic_info.target_reader,
        category_id=topic_info.category_id,
        value_score=topic_info.value_score,
        difficulty_score=topic_info.difficulty_score,
        traffic_score=topic_info.traffic_score,
        deadline=topic_info.deadline,
        created_by=created_by,
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


async def get_topics_list_crud(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    status: str | None = None,
    category_id: int | None = None,
    order_by: str = "created_at",
    order: str = "desc",
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    conditions = [Topic.is_deleted == False]

    if keyword:
        like_keyword = f"%{keyword}%"
        conditions.append(
            or_(
                Topic.title.like(like_keyword),
                Topic.angle.like(like_keyword),
                Topic.recommended_title.like(like_keyword),
            )
        )
    if status:
        conditions.append(Topic.status == status)
    if category_id is not None:
        conditions.append(Topic.category_id == category_id)

    total = await db.scalar(select(func.count()).select_from(Topic).where(*conditions))

    allowed_order_columns = {
        "created_at": Topic.created_at,
        "deadline": Topic.deadline,
        "value_score": Topic.value_score,
        "traffic_score": Topic.traffic_score,
        "difficulty_score": Topic.difficulty_score,
    }
    order_column = allowed_order_columns.get(order_by, Topic.created_at)

    stmt = (
        select(Topic)
        .options(selectinload(Topic.category), selectinload(Topic.news))
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


async def get_topic_detail_crud(topic_id: int, db: AsyncSession):
    stmt = (
        select(Topic)
        .options(selectinload(Topic.news), selectinload(Topic.category))
        .where(Topic.id == topic_id, Topic.is_deleted == False)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_topic_crud(topic_id: int, topic_info: UpdateTopicRequest, db: AsyncSession):
    topic = await get_topic_detail_crud(topic_id, db)
    if not topic:
        return None

    topic.title = topic_info.title
    topic.angle = topic_info.angle
    topic.recommended_title = topic_info.recommended_title
    topic.reason = topic_info.reason
    topic.target_reader = topic_info.target_reader
    topic.category_id = topic_info.category_id
    topic.status = topic_info.status
    topic.value_score = topic_info.value_score
    topic.difficulty_score = topic_info.difficulty_score
    topic.traffic_score = topic_info.traffic_score
    topic.deadline = topic_info.deadline
    await db.commit()
    return await get_topic_detail_crud(topic_id, db)


async def delete_topic_crud(topic_id: int, db: AsyncSession):
    topic = await get_topic_detail_crud(topic_id, db)
    if not topic:
        return None

    topic.is_deleted = True
    await db.commit()
    return topic


async def update_topic_status_crud(topic_id: int, status: str, db: AsyncSession):
    topic = await get_topic_detail_crud(topic_id, db)
    if not topic:
        return None

    topic.status = status
    await db.commit()
    await db.refresh(topic)
    return topic
