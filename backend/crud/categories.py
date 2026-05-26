from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.categories import Category
from models.news import News
from models.topics import Topic
from schemas.categories import CategoryCreateRequest, UpdateCategoryRequest


async def get_category_by_name(name: str, db: AsyncSession):
    stmt = select(Category).where(Category.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_categories(category: CategoryCreateRequest, db: AsyncSession):
    new_category = Category(
        name=category.name,
        description=category.description,
        sort_order=category.sort_order,
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


async def get_categories_list(only_active: bool, db: AsyncSession):
    stmt = select(Category).order_by(Category.sort_order.asc(), Category.id.desc())
    if only_active:
        stmt = stmt.where(Category.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_categories(category_id: int, update_data: UpdateCategoryRequest, db: AsyncSession):
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        return None

    category.name = update_data.name
    category.description = update_data.description
    category.sort_order = update_data.sort_order
    category.is_active = update_data.is_active
    await db.commit()
    await db.refresh(category)
    return category


async def category_has_related_data(category_id: int, db: AsyncSession):
    news_count = await db.scalar(
        select(func.count()).select_from(News).where(
            News.category_id == category_id,
            News.is_deleted == False,
        )
    )
    topic_count = await db.scalar(
        select(func.count()).select_from(Topic).where(
            Topic.category_id == category_id,
            Topic.is_deleted == False,
        )
    )
    return bool(news_count or topic_count)


async def delete_categories(category_id: int, db: AsyncSession):
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        return None

    await db.delete(category)
    await db.commit()
    return category
