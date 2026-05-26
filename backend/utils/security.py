import os
from pathlib import Path
from typing import Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

#密码哈希部分
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#JWT 部分
# 从 .env 中读取 JWT 配置，避免把真实密钥硬编码到代码和 Git 历史里
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET is not configured")

#=================核心工具函数，制作真实工牌（生成token）=======================
def create_access_token(user_id:int)->str:
    #接收成功登录的用户id，结合密钥生成一串专属的jwt token字符串
    
    #设置过期时间：当前UTC时间+24小时
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    #组装卡面字典数据（payload载荷）
    to_encode = {
        "sub":str(user_id),
        "exp":expire
    }
    # 利用载荷payload，密钥，和加密算法生成token
    encoded_jwt = jwt.encode(payload = to_encode, key = SECRET_KEY,algorithm = ALGORITHM)
    return encoded_jwt

#=================核心工具函数，验证工牌真伪（验证token）=======================
def verify_access_token(token:str)->int:
    #接收前端传来的token。通过算法验证防伪与过期时间，成功返回user_id，失败则直接raise抛出异常
    try:
        #解密并验签:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        #提取卡面里的用户id，有可能返回一个空值所以写Optional，如果返回空就报错
        user_id:Optional[int] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="凭证无效:未包含有效用户标识"
            )
        
        return int(user_id) 
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期,请重新登录"
        )
    
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的登录凭证"
        )
    

#实例化安全方案
security_scheme = HTTPBearer()
#编写安全守卫，通过安全守卫的user_id，都是通过token校验的user_id
async def jwt_passed_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme))->int:
    #这是一个公共的，可复用的安全卫兵
    #只管拿到请求头中的token，解密验签，通关了就把user_id返回
    token = credentials.credentials
    user_id = verify_access_token(token)
    return user_id
