from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.ai_digest import create_ai_digest_run_crud, validate_ai_digest_run
from schemas.ai_digest import AIDigestRunRequest, AIDigestRunResponse
from utils.cache import evict_cache
from utils.response import error_response, success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/ai-digest", tags=["ai-digest"])


@router.post("/runs")
@evict_cache(patterns=["cache:news_list:*", "cache:news_detail:*"])
async def create_ai_digest_run(
    run_data: AIDigestRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    validate_message = await validate_ai_digest_run(run_data, db)
    if validate_message:
        return error_response(message=validate_message, code=400, status_code=400)

    run_result = await create_ai_digest_run_crud(
        run_data=run_data,
        db=db,
        current_user_id=current_user_id,
    )
    response_data = AIDigestRunResponse.model_validate(run_result)
    return success_response(data=response_data, message="ai digest run success")
