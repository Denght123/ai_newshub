import json

from fastapi import APIRouter, Depends
import redis
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from utils.cache import cache_response
from configs.db_configs import get_db
from crud.dashboard import get_dashboard_overview_crud
from schemas.dashboard import OverviewResponse
from utils.response import success_response
from configs.redis_configs import get_redis
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger("uvicorn")  # 2. 获取 FastAPI 控制台的黑窗口日志记录器

@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db), redis_client :redis.Redis = Depends(get_redis)):
 
    #定义全局唯一的缓存抽屉钥匙名字
    CACHE_KEY = "dashboard_overview:data"

# =======================第一阶段：拦截探测Redis============================
    try:
        # 去内存抽屉里看有没有数据
        cached_json = await redis_client.get(CACHE_KEY)
        #如果在缓存中找到了数据就直接用
        if cached_json:
            logger.info("成功命中缓存，直接从运行内存直发给前端")
            #核心：用json.loads把存好的死字符串，还原成python字典
            return success_response(data = OverviewResponse.model_validate_json(cached_json),message="success")
    except Exception as err:
        logger.warning(f"redis 获取数据失败，原因 {err}，系统自动降级查MYSQL")


# ========================第二阶段：没有缓存，查询MYSQL============================
    #来到这里说明redis里是空的（初次访问或者缓存过期了）
    overview = await get_dashboard_overview_crud(db)

    overview_response = OverviewResponse.model_validate(overview)
    overview_dict = overview_response.model_dump(mode='json')  # 把pydantic模型还原成python字典


# ==========================第三阶段：把数据写入缓存数据=============================
    try:
    #核心：用json.dumps把python字典，变成纯字符串，才能存到redis里
        serialized_data = json.dumps(overview_dict)

    #存入redis，并强制命令这个抽屉在内存里只能活60s
        await redis_client.setex(name=CACHE_KEY, time=60,value = serialized_data)
        logger.info("成功写入缓存")
    except Exception as err:
        logger.error(f"redis 写入数据失败，原因 {err}")



#返回真数据给前端
    return success_response(data = overview_response,message="success")


# ============================以上是手写redis逻辑训练到路由中的调用，以下是实际工程中的通过复用redis的装饰器调用============================



# @router.get("/overview")
# @cache_response(prefix="dashboard_overview", expire=60)  # 只要在路由上加这个装饰器，就自动拥有了缓存功能，参数里只需要告诉它这个数据属于哪个模块（prefix）和缓存多久（expire）
# async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
#     overview = await get_dashboard_overview_crud(db)

#     overview_response = OverviewResponse.model_validate(overview)
#     return success_response(data = overview_response,message="success")

