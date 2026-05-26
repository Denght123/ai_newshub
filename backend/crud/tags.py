from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import news_tags
from models.tags import Tag
from schemas.tags import CreateTagsRequest


async def get_tag_by_name(name: str, db: AsyncSession):
    stmt = select(Tag).where(Tag.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_tag(tag_info: CreateTagsRequest, db: AsyncSession):
    new_tag = Tag(name=tag_info.name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag


async def get_tags_lists(db: AsyncSession):
    stmt = select(Tag).order_by(Tag.id.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_tags(tag_id: int, changed_name: CreateTagsRequest, db: AsyncSession):
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        return None

    tag.name = changed_name.name
    await db.commit()
    await db.refresh(tag)
    return tag


async def tag_has_related_news(tag_id: int, db: AsyncSession):
    count = await db.scalar(
        select(func.count()).select_from(news_tags).where(news_tags.c.tag_id == tag_id)
    )
    return bool(count)


async def delete_tags(tag_id: int, db: AsyncSession):
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if not tag:
        return None

    await db.delete(tag)
    await db.commit()
    return tag
