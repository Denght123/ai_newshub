from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.tags import (
    create_tag,
    delete_tags,
    get_tag_by_name,
    get_tags_lists,
    tag_has_related_news,
    update_tags,
)
from schemas.tags import CreateTagsRequest, TagsListResponse, TagsResponse
from utils.cache import cache_response, evict_cache
from utils.response import error_response, success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:tags_list:*"])  # 给这个接口加上缓存清除功能，参数里告诉它这个数据属于 tags_list 模块，每当这个接口被调用时，就自动清除 tags_list 模块相关的缓存
async def create_tags(
    tags_info: CreateTagsRequest,
    db: AsyncSession = Depends(get_db),
):
    if await get_tag_by_name(tags_info.name, db):
        return error_response(message = "tag name already exists",code = 409,status_code = 409)

    tag = await create_tag(tags_info, db)
    response_tag =  TagsResponse.model_validate(tag)
    return success_response(data = response_tag,message = "create success")

@router.get("",dependencies=[Depends(jwt_passed_user_id)])
@cache_response(prefix="tags_list", expire=60)  # 给这个接口加上缓存功能，参数里告诉它这个数据属于 tags_list 模块，缓存时效 60 秒
async def get_tags_list(db: AsyncSession = Depends(get_db)):
    tags_list = await get_tags_lists(db)
    response_tags_list = TagsListResponse(
        tags=[
            TagsResponse.model_validate(tag)
            for tag in tags_list
        ]
    )
    return success_response(data = response_tags_list,message="success")


@router.put("/{tag_id}",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:tags_list:*"])  # 给这个接口加上缓存清除功能，参数里告诉它这个数据属于 tags_list 模块，每当这个接口被调用时，就自动清除 tags_list 模块相关的缓存
async def update_tag(
    tag_id: int,
    changed_name: CreateTagsRequest,
    db: AsyncSession = Depends(get_db),
):
    tag = await update_tags(tag_id, changed_name, db)
    if not tag:
        return error_response(message = "tag not found",code = 404,status_code = 404)

    return success_response(message = "update success")


@router.delete("/{tag_id}",dependencies=[Depends(jwt_passed_user_id)])
@evict_cache(patterns=["cache:tags_list:*"])  # 给这个接口加上缓存清除功能，参数里告诉它这个数据属于 tags_list 模块，每当这个接口被调用时，就自动清除 tags_list 模块相关的缓存
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    if await tag_has_related_news(tag_id, db):
        return error_response(message="tag has related news",code = 400,status_code = 400)

    tag = await delete_tags(tag_id, db)
    if not tag:
        return error_response(message = "tag not found",code = 404,status_code = 404)

    return success_response(message = "delete success",data = None)
