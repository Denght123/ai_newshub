#注册全局异常处理器

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.exception import general_exception_handler, http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, validation_exception_handler



def register_exception_handlers(app):
    #FastAPI主动抛出的http异常
    app.add_exception_handler(HTTPException,http_exception_handler)

    #请求参数异常，比如字段缺失，类型错误
    app.add_exception_handler(RequestValidationError,validation_exception_handler)

    #数据库完整性约束异常，比如唯一约束，外键约束
    app.add_exception_handler(IntegrityError,integrity_error_handler)

    #SQLAlchemy其他数据库异常
    app.add_exception_handler(SQLAlchemyError,sqlalchemy_error_handler)

    #所有未捕获异常，兜底处理
    app.add_exception_handler(Exception,general_exception_handler)