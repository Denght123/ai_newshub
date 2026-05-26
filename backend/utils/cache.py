import json
import logging
from functools import wraps
from fastapi import Response
from fastapi.encoders import jsonable_encoder
import redis.asyncio as redis

# 🎯 引入你在 configs 目录下配置好的全局 Redis 连接池
# 💡 以后换到全新项目时，只需将这里改为新项目的连接池导入路径即可
from configs.redis_configs import redis_pool

logger = logging.getLogger("uvicorn")


# =====================================================================
# 🟢 上半场：全自动【读拦截 / 回填】装饰器
# =====================================================================
def cache_response(prefix: str, expire: int = 60):
    """
    🚀 通用路由响应缓存装饰器（高并发读护盾）
    :param prefix: 缓存钥匙前缀（模块名，如 'news'、'dashboard'）
    :param expire: 缓存过期时间（秒），默认 60 秒
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            
            # --- 🧩 步骤 1：广泛依赖过滤，动态生成唯一、防分裂的 CACHE_KEY ---
            generic_dependencies = {
                "db", "session", "current_user", "user", "token", 
                "request", "redis_client", "current_uid", "auth"
            }
            filtered_kwargs = {
                k: v for k, v in kwargs.items() if k not in generic_dependencies
            }
            param_str = ":".join([f"{k}_{v}" for k, v in sorted(filtered_kwargs.items())])
            
            cache_key = f"cache:{prefix}:{func.__name__}"
            if param_str:
                cache_key += f":{param_str}"

            # --- 🧩 步骤 2：从全局池子借出 Redis 客户端 ---
            async with redis.Redis(connection_pool=redis_pool, decode_responses=True) as redis_client:
                
                # ⚔️ 防线一：探测拦截 Redis（缓存命中则光速返回）
                try:
                    cached_data = await redis_client.get(cache_key)
                    if cached_data:
                        logger.info(f"🎉 [Cache Hit] 缓存大命中! Key: {cache_key}")
                        return Response(content=cached_data, media_type="application/json")
                except Exception as err:
                    logger.warning(f"🚨 [Cache Read Error] 读取缓存意外失败: {err}，系统自动降级走数据库")

                # 🛡️ 防线二：缓存未命中，放行执行原路由业务
                response_obj = await func(*args, **kwargs)

                # 📦 防线三：智能识别响应类型，安全回填 Redis
                try:
                    # ✨【安全安检】：只有当 HTTP 状态码为 200 正常成功时，才允许写入缓存！
                    # 彻底杜绝 400、404、500 等错误或异常信息污染、死锁缓存抽屉
                    if hasattr(response_obj, "status_code") and response_obj.status_code == 200:
                        if isinstance(response_obj, Response):
                            raw_json_str = bytes(response_obj.body).decode("utf-8")
                        else:
                            raw_json_str = json.dumps(jsonable_encoder(response_obj))
                        
                        await redis_client.setex(name=cache_key, time=expire, value=raw_json_str)
                        logger.info(f"📝 [Cache Write] 成功将全新数据回填至 Redis! Key: {cache_key}")
                    else:
                        logger.info(f"⚠️ [Cache Skip] 检测到非200正常响应，放弃写入缓存，防止缓存污染")
                        
                except Exception as err:
                    logger.error(f"🚨 [Cache Write Error] 回填缓存数据失败: {err}")

            return response_obj
        return wrapper
    return decorator


# =====================================================================
# 🔴 下半场：全自动【写擦除 / 强制同步】装饰器
# =====================================================================
def evict_cache(patterns: list[str]):
    """
    🧹 通用全自动缓存清除装饰器（数据一致性老缓存终结者）
    :param patterns: 需要模糊匹配并强制销毁的钥匙规则列表（如 ['cache:news:*']）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            
            # 🛡️ 步骤 1：先放行，让路由去执行真实的 MySQL 写操作（增/删/改）
            response_obj = await func(*args, **kwargs)
            
            # 🛡️ 步骤 2：【安全气囊】：只有当 MySQL 写操作完全成功（HTTP状态码为 200 或 201）时，才触发清除
            # 如果接口报错、格式不对、压根没动数据库，直接跳过清除，保障 Redis 性能
            status_code = getattr(response_obj, "status_code", 200)
            if status_code in (200, 201):
                try:
                    async with redis.Redis(connection_pool=redis_pool, decode_responses=True) as redis_client:
                        # 循环前端传进来的每一个模糊清除通配符规则
                        for pattern in patterns:
                            # 🔥【大厂安全标准】：使用 scan_iter 渐进式游标模糊搜寻钥匙
                            # 彻底代替高危、易引发 Redis 内存瞬间卡死崩溃的 redis.keys() 命令
                            async for key in redis_client.scan_iter(match=pattern):
                                await redis_client.delete(key)
                                logger.info(f"🗑️ [Cache Evict] 数据库变更，全自动清洁队已擦除旧缓存: {key}")
                except Exception as err:
                    logger.error(f"🚨 [Cache Evict Error] 尝试自动清除老缓存时发生意外: {err}")
            
            return response_obj
        return wrapper
    return decorator