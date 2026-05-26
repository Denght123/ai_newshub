from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6, max_length=72)

class UserInfoResponse(BaseModel):
    id:int
    username:str
    email:str
    nickname:str | None = None
    role:str
    is_active:bool

    #让pydantic可以从orm中获取响应的字段信息
    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    access_token: str
    token_type:str
    user: UserInfoResponse

    model_config = ConfigDict(from_attributes=True)

# class LoginResponse(UserInfoResponse):
#     access_token: str
#     token_type:str


class GetUserResponse(UserInfoResponse):
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)