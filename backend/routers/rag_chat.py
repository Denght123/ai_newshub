from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.rag_chat import ask_rag_chat_crud, stream_rag_chat_crud
from schemas.rag_chat import RagChatAskRequest, RagChatAskResponse
from utils.response import success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/rag-chat", tags=["rag-chat"])


# 普通问答接口：适合 Swagger 调试，一次性返回完整 answer。
@router.post("/ask")
async def ask_rag_chat(
    ask_data: RagChatAskRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    # 非流式接口方便 Swagger 调试；真实 RAG 逻辑写在 crud/rag_chat.py。
    result = await ask_rag_chat_crud(ask_data, db, current_user_id)
    response_data = RagChatAskResponse.model_validate(result)
    return success_response(data=response_data)


# 流式问答接口：适合前端聊天页，把回答内容分段推送给浏览器。
@router.post("/stream")
async def stream_rag_chat(
    ask_data: RagChatAskRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    # 这个接口先把流式链路打通，后续你只需要替换生成器里的 LLM 调用。
    generator = stream_rag_chat_crud(ask_data, db, current_user_id)
    return StreamingResponse(generator, media_type="text/event-stream")
