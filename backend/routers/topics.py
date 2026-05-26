from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.topics import (
    create_topic_crud,
    delete_topic_crud,
    get_topic_detail_crud,
    get_topics_list_crud,
    update_topic_crud,
    update_topic_status_crud,
)
from schemas.topics import (
    CreateTopicRequest,
    CreateTopicResponse,
    TopicDetailResponse,
    TopicListItemResponse,
    TopicListResponse,
    UpdateTopicRequest,
    UpdateTopicResponse,
    UpdateTopicStatusRequest,
    UpdateTopicStatusResponse,
)
from utils.cache import cache_response, evict_cache
from utils.response import error_response, success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:topics_list:*", "cache:topic_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def create_topic(topic_info: CreateTopicRequest, db: AsyncSession = Depends(get_db)):
    topic = await create_topic_crud(topic_info, db)
    if not topic:
        return error_response(message="please register a user first", code=400)

    response_data = CreateTopicResponse.model_validate(topic)
    return success_response(data=response_data)


@router.get("",dependencies=[Depends(jwt_passed_user_id)])
@cache_response(prefix="topics_list", expire=60)  # 给这个接口加上缓存功能，参数里告诉它这个数据属于 topics_list 模块，缓存时效 60 秒
async def get_topics_list(
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    status: str | None = None,
    category_id: int | None = None,
    order_by: str = "created_at",
    order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    result = await get_topics_list_crud(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
        category_id=category_id,
        order_by=order_by,
        order=order,
    )
    response_data = TopicListResponse(
        items=[TopicListItemResponse.model_validate(topic) for topic in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )
    return success_response(data=response_data)


@router.get("/{topic_id}",dependencies=[Depends(jwt_passed_user_id)])
@cache_response(prefix="topic_detail", expire=60)
async def get_topic_detail(topic_id: int, db: AsyncSession = Depends(get_db)):
    topic = await get_topic_detail_crud(topic_id, db)
    if not topic:
        return error_response(message="topic not found", code=404, status_code=404)

    response_data = TopicDetailResponse.model_validate(topic)
    return success_response(data=response_data)


@router.put("/{topic_id}",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:topics_list:*", "cache:topic_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def update_topic(
    topic_id: int,
    topic_info: UpdateTopicRequest,
    db: AsyncSession = Depends(get_db),
):
    topic = await update_topic_crud(topic_id, topic_info, db)
    if not topic:
        return error_response(message="topic not found", code=404, status_code=404)

    response_data = UpdateTopicResponse.model_validate(topic)
    return success_response(data=response_data, message="update success")


@router.delete("/{topic_id}",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:topics_list:*", "cache:topic_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def delete_topic(topic_id: int, db: AsyncSession = Depends(get_db)):
    topic = await delete_topic_crud(topic_id, db)
    if not topic:
        return error_response(message="topic not found", code=404, status_code=404)

    return success_response(message="delete success")

@router.patch("/{topic_id}/status",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:topics_list:*", "cache:topic_detail:*"])  # 给这个接口加上缓存清除功能，参数里告诉它需要清除哪些缓存（模糊匹配规则）
async def update_topic_status(
    topic_id: int,
    status_info: UpdateTopicStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    allow_status = {"pending", "selected", "writing", "published", "abandoned"}
    if status_info.status not in allow_status:
        return error_response(message="invalid status", code=400)

    topic = await update_topic_status_crud(topic_id, status_info.status, db)
    if not topic:
        return error_response(message="topic not found", code=404, status_code=404)

    response_data = UpdateTopicStatusResponse.model_validate(topic)
    return success_response(data=response_data)
