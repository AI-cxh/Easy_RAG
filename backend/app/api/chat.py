"""聊天API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.models import ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse, ChatSessionResponse, ChatSessionListResponse
from app.services.rag import rag_service
from app.services.search import get_search_service


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    聊天接口

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

        # 获取聊天历史
        history = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
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

        # 生成响应
        response = rag_service.generate_response(
            query=request.message,
            context=context,
            search_results=search_results,
            chat_history=chat_history
        )

        # 保存助手消息
        assistant_msg = ChatMessage(session_id=session.id, role="assistant", content=response)
        db.add(assistant_msg)
        db.commit()

        return ChatResponse(
            response=response,
            session_id=session.id,
            sources=sources if sources else None,
            search_results=search_results if request.use_web_search else None
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")


@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_sessions(db: Session = Depends(get_db)):
    """获取所有聊天会话"""
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
    return ChatSessionListResponse(sessions=sessions)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """获取指定会话的详细信息"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """删除指定会话"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"message": "会话已删除"}
