# 开发模式：返回详细错误信息
# 生产模式：不要把 traceback 返回给前端
import traceback

from fastapi import HTTPException, Request,status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.response import error_response


DEBUG_MODE = True

#处理HTTPexceptipon异常:
# Request表示http这一次请求对象，里面有很多信息，比如：
# request.url 请求地址     request.method 请求方法    request.headers 请求头    request.query_params 请求参数
# exc: 这次捕获到的异常对象
async def http_exception_handler(request:Request,exc:HTTPException):
    return error_response(
        message = exc.detail,
        code = exc.status_code,
        status_code = exc.status_code,
        data = None
    )


#处理请求参数校验异常（例如必传字段没传，字段类型不对）
async def validation_exception_handler(request:Request,exc:RequestValidationError):

    error_data = None
    # 如果在开发者模式
    if DEBUG_MODE:
        error_data = {
            "error_type":"RequestValidationError",
            "errors":exc.errors(),
            "body":exc.body,
            "path":str(request.url)
        }

    return error_response(
        message = "请求参数校验失败",
        code = status.HTTP_422_UNPROCESSABLE_ENTITY,
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
        data = error_data
    )


#处理数据库完整性结束错误（例如：唯一约束，外键约束，非空约束）
async def integrity_error_handler(request:Request,exc:IntegrityError):
    error_msg = str(exc.orig)

    if "Duplicate entry" in error_msg:
        detail =  "数据已存在"
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"

    error_data = None

    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_msg": error_msg,
            "path": str(request.url)
        }

    return error_response(
        message = detail,
        code = status.HTTP_409_CONFLICT,
        status_code = status.HTTP_409_CONFLICT,
        data = error_data
    )


#处理SQLalchemy数据库错误
async def sqlalchemy_error_handler(request:Request,exc:SQLAlchemyError):
    error_data = None

    if DEBUG_MODE:
        error_data = {
            "error_type":type(exc).__name__,
            "error msg":str(exc),
            "traceback":traceback.format_exc(),
            "path":str(request.url)
        }

    return error_response(
        message = "数据库操作失败，请稍后重试",
        code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data = error_data
    )

#处理所有未捕获的异常
async def general_exception_handler(request:Request,exc:Exception):
    error_data = None

    if DEBUG_MODE:
        error_data = {
            "error_type":type(exc).__name__,
            "error_msg":str(exc),
            "traceback":traceback.format_exc(),
            "path":str(request.url)
        }
    
    return error_response(
        message = "服务器内部错误，请稍后重试",
        code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data = error_data
    )
    