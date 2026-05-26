from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#通用成功响应
def success_response(data:Any = None,message:str = "success"):
    content = {
        "code":200,
        "message":message,
        "data":data
    }

    return JSONResponse(content = jsonable_encoder(content))

#通用失败响应
def error_response(
    data: Any = None,
    message: str = "error",
    code: int = 400,
    status_code: int = 400,
):
    content = {
        "code": code,
        "message": message,
        "data": data,
    }

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
    )