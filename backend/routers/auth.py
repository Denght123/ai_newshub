from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response import error_response, success_response
from configs.db_configs import get_db
from crud.auth import (
    get_me_user,
    get_user_by_email,
    get_user_by_username,
    login_user,
    register_user,
)
from schemas.auth import GetUserResponse, LoginRequest, LoginResponse, RegisterRequest, UserInfoResponse
from utils.security import jwt_passed_user_id,create_access_token,verify_access_token
router = APIRouter(prefix="/auth", tags=["auth"])



#用户注册模块
@router.post("/register")
async def register(auth_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(auth_data.username, db):
        return error_response(message = "username already exists",code=409,status_code=409)
    if await get_user_by_email(auth_data.email, db):
        return error_response(message = "email already exists",code=409,status_code=409)

    user_data = await register_user(
        auth_data.username,
        auth_data.email,
        auth_data.password,
        db,
    )
    #封装响应数据
    response_data = UserInfoResponse.model_validate(user_data)

    return success_response(data = response_data,message = "register success")

#用户登录模块
@router.post("/login")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await login_user(login_data.username_or_email, login_data.password, db)
    if not user:
        return error_response(message = "login failed")
    if not user.is_active:
        return error_response(message = "login failed")
    
    #利用写好的create_access_token方法，生成token
    real_token = create_access_token(user_id = user.id)
    
    #封装好相应给前端
    response_data = LoginResponse(
        access_token=real_token,
        token_type="bearer",
        user =UserInfoResponse.model_validate(user) 
        )
    return success_response(data = response_data,message="login success")

#获取当前用户信息
@router.get("/me")
async def get_current_user_info(user_id:int =  Depends(jwt_passed_user_id), db: AsyncSession = Depends(get_db)):
    #这个接口已经被安全上锁，只有当安全员jwt_passed_user_id验证牌子通过时，才会把解密送出的整数user_id送到这里
    user_info = await get_me_user(user_id, db)
    if not user_info:
        return error_response(message = "user not found")

    response_data = GetUserResponse.model_validate(user_info)
    return success_response(data = response_data,message = "get user info success")
