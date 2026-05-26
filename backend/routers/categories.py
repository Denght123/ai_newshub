from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.categories import (
    category_has_related_data,
    create_categories,
    delete_categories,
    get_categories_list,
    get_category_by_name,
    update_categories,
)
from schemas.categories import CategoryCreateRequest, CreateCategoryResponse, UpdateCategoryRequest
from utils.response import error_response, success_response
from utils.security import create_access_token, jwt_passed_user_id,verify_access_token
router = APIRouter(prefix="/categories", tags=["categories"])


def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
    }


@router.post("",dependencies = [Depends(jwt_passed_user_id)])
async def create_category(
    category_data: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    if await get_category_by_name(category_data.name, db):
        return error_response("category name already exists",code=404,status_code=404)

    category = await create_categories(category_data, db)
    response_category = CreateCategoryResponse.model_validate(category)
    return success_response(data =  response_category,message="create success") 

@router.get("",dependencies=[Depends(jwt_passed_user_id)])
async def get_categories(
    only_active: bool = False,
    db: AsyncSession = Depends(get_db),
):
    categories_list = await get_categories_list(only_active, db)
    response_data = [
        CreateCategoryResponse.model_validate(category_to_dict(category))
        for category in categories_list
    ]
    return success_response(data = response_data,message="get success")

@router.put("/{category_id}",dependencies = [Depends(jwt_passed_user_id)])
async def update_category(
    category_id: int,
    update_data: UpdateCategoryRequest,
    db: AsyncSession = Depends(get_db),
):
    category = await update_categories(category_id, update_data, db)
    if not category:
        return error_response(message="category not found",code=404,status_code=404)

    return success_response(message="update success")

@router.delete("/{category_id}",dependencies = [Depends(jwt_passed_user_id)])
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    if await category_has_related_data(category_id, db):
        return error_response(message="category has related data",code=409,status_code=409 )

    category = await delete_categories(category_id, db)
    if not category:
        return error_response(message="category not found",code=404,status_code=404)

    return success_response(message="delete success",data = None)
