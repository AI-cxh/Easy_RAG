"""聊天API路由"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json

from app.models.database import get_db
from app.models.models import ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse, ChatSessionResponse, ChatSessionListResponse
from app.services.rag import rag_service
from app.services.search import get_search_service


router = APIRouter()


async def stream_response(
    session_id: int,
    response_generator: AsyncGenerator[str, None],
    sources: List[str] | None,
    search_results: List[dict] | None,
    use_web_search: bool,
    db: Session
) -> AsyncGenerator[str, None]:
    """流式发送响应"""
    full_response = ""
    try:
        async for chunk in response_generator:
            full_response += chunk
            # 发送 SSE 格式的数据
            data = {
                "type": "chunk",
                "content": chunk
            }
            yield f"data: {json.dumps(data)}\n\n"
    except Exception as e:
        # 发送错误信息
        error_data = {"type": "error", "message": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"
        return

    # 保存完整的助手消息到数据库
    try:
        assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=full_response)
        db.add(assistant_msg)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save assistant message: {e}")

    # 发送完成信号和元数据
    end_data = {
        "type": "end",
        "session_id": session_id,
        "sources": sources,
        "search_results": search_results if use_web_search else None
    }
    yield f"data: {json.dumps(end_data)}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    聊天接口 - 支持流式响应

    - **message**: 用户消息
    - **session_id**: 可选的会话ID，如果提供则继续已有会话
    - **kb_ids**: 选择的知识库ID列表
    - **use_web_search**: 是否使用网络搜索
    """
    try:
        # 获取或创建会话
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")
        else:
            session = ChatSession(title=request.message[:30] + ("..." if len(request.message) > 30 else ""))
            db.add(session)
            db.commit()
            db.refresh(session)

        # 保存用户消息
        user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
        db.add(user_msg)
        db.commit()

        # 获取聊天历史
        history = db.query(ChatMessage).filter(
            ChatSession.id == session.id,
            ChatMessage.created_at < user_msg.created_at
        ).order_by(ChatMessage.created_at).all()
        chat_history = [{"role": msg.role, "content": msg.content} for msg in history]

        # 从知识库检索上下文
        context = ""
        sources = []
        if request.kb_ids:
            context = rag_service.build_context(request.kb_ids, request.message)
            # 提取来源信息
            if context:
                search_results = await rag_service.embedding_service.search_similar(request.kb_ids, request.message, k=4)
                sources = [doc['metadata'].get('source', '未知') for doc in search_results]

        # 网络搜索
        search_results = None
        if request.use_web_search:
            search_service = await get_search_service()
            search_result = await search_service.web_search(request.message, num_results=5)
            search_results = search_result

        # 生成流式响应
        response_stream = rag_service.stream_generate_response(
            query=request.message,
            context=context,
            search_results=search_results,
            chat_history=chat_history
        )

        # 返回 SSE 响应
        return StreamingResponse(
            stream_response(
                session_id=session.id,
                response_generator=response_stream,
                sources=sources if sources else None,
                search_results=search_results if request.use_web_search else None,
                use_web_search=request.use_web_search,
                db=db
            ),
            media_type="text/event-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")


@router.get("/chat/sessions", response_model=ChatSessionListResponse)
async def get_sessions(db: Session = Depends(get_db)):
    """获取所有聊天会话"""
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
    return ChatSessionListResponse(sessions=sessions)


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """获取指定会话的详细信息"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 获取会话的消息
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    # 构建响应
    session_dict = {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "messages": [
            {
                "id": msg.id,
                "session_id": msg.session_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }
    return ChatSessionResponse(**session_dict)


@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """删除指定会话"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"message": "会话已删除"}
