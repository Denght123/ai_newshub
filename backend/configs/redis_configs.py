import logging

import redis.asyncio as redis
import os
from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()  # 从 .env 文件加载环境变量

#1.定义Redis服务器的连接参数
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")  # Redis服务器的URL，包含主机、端口和数据库编号

logger = logging.getLogger("uvicorn")

#2.建立一个全局常驻的连接池
redis_pool = redis.ConnectionPool.from_url(REDIS_URL,decode_responses=True)

#编写供 FastAPI 随时借用连接的“快递员函数”，跟get_db一样，都是一个连接函数
async def get_redis() -> AsyncGenerator[redis.Redis, None]:  # 函数返回一个异步生成器
    client = redis.Redis(connection_pool=redis_pool)  # 创建一个Redis客户端对象
    try:
        yield client  # 返回客户端对象
    finally:
        await client.aclose()  # 在函数退出时关闭连接