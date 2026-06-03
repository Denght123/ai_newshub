from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.daily_digest import create_daily_digest_run_crud, get_daily_digest_runs_crud
from schemas.daily_digest import (
    DailyDigestRunListResponse,
    DailyDigestRunRequest,
    DailyDigestRunResponse,
)
from utils.response import success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/daily-digest", tags=["daily-digest"])


# 创建每日采集任务：前端点击“开始采集”时会走这里。
@router.post("/runs")
async def create_daily_digest_run(
    run_data: DailyDigestRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    # 路由层只负责接收参数和返回响应；真实抓取逻辑写在 crud/daily_digest.py。
    result = await create_daily_digest_run_crud(run_data, db, current_user_id)
    response_data = DailyDigestRunResponse.model_validate(result)
    return success_response(data=response_data)


# 查询采集任务历史：前端后续可以用它展示最近跑过哪些采集。
@router.get("/runs")
async def get_daily_digest_runs(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    result = await get_daily_digest_runs_crud(db, page, page_size)
    response_data = DailyDigestRunListResponse.model_validate(result)
    return success_response(data=response_data)
