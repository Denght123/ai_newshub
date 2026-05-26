from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.categories import router as categories_router
from routers.dashboard import router as dashboard_router
from routers.health import router as health_router
from routers.news import router as news_router
from routers.tags import router as tags_router
from routers.topics import router as topics_router
from utils.exception_handlers import register_exception_handlers

app = FastAPI(title="AI NewsHub Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(categories_router, prefix=API_PREFIX)
app.include_router(tags_router, prefix=API_PREFIX)
app.include_router(news_router, prefix=API_PREFIX)
app.include_router(topics_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(health_router, prefix=API_PREFIX)

register_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "AI NewsHub Backend"}
