from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.daily_digest import router as daily_digest_router
from routers.health import router as health_router
from routers.knowledge import router as knowledge_router
from routers.rag_chat import router as rag_chat_router
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
app.include_router(daily_digest_router, prefix=API_PREFIX)
app.include_router(knowledge_router, prefix=API_PREFIX)
app.include_router(rag_chat_router, prefix=API_PREFIX)
app.include_router(health_router, prefix=API_PREFIX)

register_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "AI NewsHub Backend"}
