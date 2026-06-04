from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_configs import get_db
from crud.rag_chat import (
    ask_rag_chat_crud,
    delete_rag_chat_session_crud,
    get_rag_chat_session_detail_crud,
    get_rag_chat_sessions_crud,
    stream_rag_chat_crud,
)
from schemas.rag_chat import (
    RagChatAskRequest,
    RagChatAskResponse,
    RagChatSessionDetailResponse,
    RagChatSessionResponse,
)
from utils.response import success_response
from utils.security import jwt_passed_user_id

router = APIRouter(prefix="/rag-chat", tags=["rag-chat"])


# 查询当前用户的聊天会话列表。
@router.get("/sessions")
async def get_rag_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    result = await get_rag_chat_sessions_crud(db, current_user_id)
    response_data = [RagChatSessionResponse.model_validate(item) for item in result]
    return success_response(data=response_data)


# 查询某个聊天会话详情，包括历史消息。
@router.get("/sessions/{session_id}")
async def get_rag_chat_session_detail(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    result = await get_rag_chat_session_detail_crud(session_id, db, current_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="chat session not found")

    response_data = RagChatSessionDetailResponse.model_validate(result)
    return success_response(data=response_data)


# 删除某个聊天会话。
@router.delete("/sessions/{session_id}")
async def delete_rag_chat_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(jwt_passed_user_id),
):
    deleted = await delete_rag_chat_session_crud(session_id, db, current_user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="chat session not found")

    return success_response(data=None, message="deleted")


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
