from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from utils.cache import cache_response, evict_cache
from utils.security import jwt_passed_user_id
from crud.news import (
    create_news_crud,
    create_topic_from_news_crud,
    delete_news_crud,
    get_news_detail_crud,
    get_news_list_crud,
    update_news_crud,
    update_news_favorite_crud,
)
from schemas.news import (
    CreateNewsRequest,
    FavoriteNewsRequest,
    FavoriteNewsResponse,
    NewsCategoryResponse,
    NewsCreatorResponse,
    NewsDetailResponse,
    NewsListItemResponse,
    NewsListResponse,
    NewsTagResponse,
    NewsToTopicRequest,
    NewsToTopicResponse,
    UpdateNewsResponse,
    UpdateNewsRequest,
)
from utils.response import error_response, success_response

router = APIRouter(prefix="/news", tags=["news"])


def news_category_to_response(category):
    if not category:
        return None
    return NewsCategoryResponse(
        id=category.id,
        name=category.name,
    )


def news_tags_to_response(tags):
    return [
        NewsTagResponse(
            id=tag.id,
            name=tag.name,
        )
        for tag in tags
    ]


def news_creator_to_response(creator):
    if not creator:
        return None
    return NewsCreatorResponse(
        id=creator.id,
        username=creator.username,
    )


def news_to_list_response(news):
    return NewsListItemResponse(
        id=news.id,
        title=news.title,
        source_name=news.source_name,
        category=news_category_to_response(news.category),
        tags=news_tags_to_response(news.tags),
        status=news.status,
        importance_score=news.importance_score,
        heat_score=news.heat_score,
        is_favorite=news.is_favorite,
        publish_time=news.publish_time,
        created_at=news.created_at,
    )


def news_to_detail_response(news):
    return NewsDetailResponse(
        id=news.id,
        title=news.title,
        source_name=news.source_name,
        category=news_category_to_response(news.category),
        tags=news_tags_to_response(news.tags),
        status=news.status,
        importance_score=news.importance_score,
        heat_score=news.heat_score,
        is_favorite=news.is_favorite,
        publish_time=news.publish_time,
        created_at=news.created_at,
        source_url=news.source_url,
        summary=news.summary,
        content=news.content,
        created_by=news_creator_to_response(news.creator),
        updated_at=news.updated_at,
    )


@router.post("",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:news_list:*", "cache:news_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def create_news(
    news_info: CreateNewsRequest,
    db: AsyncSession = Depends(get_db),
):
    news_data = await create_news_crud(news_info, db)
    if not news_data:
        return error_response(message="please register a user first", code=400)

    return success_response(data=news_to_detail_response(news_data))


@router.get("",dependencies=[Depends(jwt_passed_user_id)])
@cache_response(prefix="news_list", expire=60)  # 给这个接口加上缓存功能，参数里告诉它这个数据属于 news_list 模块，缓存时效 60 秒
async def get_news_list(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    category_id: int | None = None,
    status: str | None = None,
    is_favorite: bool | None = None,
    order_by: str = "created_at",
    order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    result = await get_news_list_crud(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        category_id=category_id,
        status=status,
        is_favorite=is_favorite,
        order_by=order_by,
        order=order,
    )
    response_data = NewsListResponse(
        items=[news_to_list_response(news) for news in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )
    return success_response(data=response_data)


@router.get("/{news_id}",dependencies=[Depends(jwt_passed_user_id)])
@cache_response(prefix="news_detail", expire=60)  # 给这个接口加上缓存功能，参数里告诉它这个数据属于 news_detail 模块，缓存时效 60 秒
async def get_news_detail(news_id: int, db: AsyncSession = Depends(get_db)):
    news_data = await get_news_detail_crud(news_id, db)
    if not news_data:
        return error_response(message="news not found", code=404, status_code=404)

    return success_response(data=news_to_detail_response(news_data))


@router.put("/{news_id}",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:news_list:*", "cache:news_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def update_news(
    news_id: int,
    news_info: UpdateNewsRequest,
    db: AsyncSession = Depends(get_db),
):
    news_data = await update_news_crud(news_id, news_info, db)
    if not news_data:
        return error_response(message="news not found", code=404, status_code=404)

    response_data = UpdateNewsResponse(
        id=news_data.id,
        title=news_data.title,
    )
    return success_response(data=response_data, message="update success")


@router.delete("/{news_id}",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:news_list:*", "cache:news_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def delete_news(news_id: int, db: AsyncSession = Depends(get_db)):
    news_data = await delete_news_crud(news_id, db)
    if not news_data:
        return error_response(message="news not found", code=404, status_code=404)

    return success_response(message="delete success")


@router.patch("/{news_id}/favorite",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:news_list:*", "cache:news_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def update_news_favorite(
    news_id: int,
    favorite_info: FavoriteNewsRequest,
    db: AsyncSession = Depends(get_db),
):
    news_data = await update_news_favorite_crud(
        news_id,
        favorite_info.is_favorite,
        db,
    )
    if not news_data:
        return error_response(message="news not found", code=404, status_code=404)

    response_data = FavoriteNewsResponse(
        id=news_data.id,
        is_favorite=news_data.is_favorite,
    )
    return success_response(data=response_data)


@router.post("/{news_id}/to-topic",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:news_list:*", "cache:news_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def create_topic_from_news(
    news_id: int,
    topic_info: NewsToTopicRequest,
    db: AsyncSession = Depends(get_db),
):
    topic = await create_topic_from_news_crud(news_id, topic_info, db)
    if not topic:
        return error_response(message="news not found", code=404, status_code=404)

    response_data = NewsToTopicResponse(
        id=topic.id,
        news_id=topic.news_id,
        title=topic.title,
        status=topic.status,
    )
    return success_response(data=response_data)
