"""聊天API路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json
import os
import tiktoken

from app.models.database import get_db
from app.models.models import ChatSession, ChatMessage, User, KnowledgeBase, Document, Chunk
from app.models.schemas import (
    ChatRequest, ChatResponse, ChatSessionResponse, ChatSessionListResponse,
    SessionRenameRequest, AgentChatRequest, AgentStepResponse, ChatUploadResponse, DocumentResponse
)
from app.services.rag import rag_service
from app.services.search import get_search_service
from app.services.embedding import embedding_service
from app.services.agent import agent_service
from app.services.auth import get_current_user, require_user
from app.utils.file_parser import FileParser
from app.config import settings


# 初始化上传目录和工具
UPLOAD_DIR = settings.CHROMA_DB_PATH + "/../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """计算文本的token数量"""
    return len(tokenizer.encode(text))


def get_file_type(filename: str) -> str:
    """根据文件扩展名获取文件类型"""
    ext = os.path.splitext(filename.lower())[1]
    type_map = {'.txt': 'text', '.md': 'markdown', '.pdf': 'pdf', '.docx': 'docx'}
    return type_map.get(ext, 'unknown')


def parse_message_metadata(msg: ChatMessage) -> dict:
    """解析消息的extra_data字段"""
    extra_data = {}
    if msg.extra_data:
        try:
            extra_data = json.loads(msg.extra_data)
        except:
            pass
    # 兼容旧数据：如果有 sources 但没有 source_details，则生成 source_details
    if extra_data.get("sources") and not extra_data.get("source_details"):
        if isinstance(extra_data["sources"], list) and extra_data["sources"]:
            # 如果 sources 是字符串列表，转换为简单的 source_details 格式
            if isinstance(extra_data["sources"][0], str):
                extra_data["source_details"] = [
                    {"kb_name": s, "doc_name": s, "content": ""}
                    for s in extra_data["sources"]
                ]
    return extra_data


router = APIRouter()


async def stream_response(
    session_id: int,
    response_generator: AsyncGenerator[str, None],
    sources: List[dict] | None,  # 修改为 dict 列表，包含详细信息
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
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    except Exception as e:
        # 发送错误信息
        error_data = {"type": "error", "message": str(e)}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        return

    # 保存完整的助手消息到数据库
    try:
        # 构建extra_data
        extra_data = {}
        if sources:
            extra_data["source_details"] = sources  # 保存详细的来源信息
        if search_results:
            extra_data["search_results"] = search_results

        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=full_response,
            extra_data=json.dumps(extra_data, ensure_ascii=False) if extra_data else None
        )
        db.add(assistant_msg)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save assistant message: {e}")

    # 发送完成信号和元数据
    # 提取去重的知识库名称列表
    kb_names = []
    for s in (sources or []):
        kb_name = s.get("kb_name", s.get("doc_name", "未知"))
        if kb_name not in kb_names:
            kb_names.append(kb_name)

    end_data = {
        "type": "end",
        "session_id": session_id,
        "sources": kb_names if kb_names else None,
        "source_details": sources,
        "search_results": search_results if use_web_search else None
    }
    yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
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
            # 权限检查
            if session.user_id and session.user_id != user.id and user.role != "admin":
                raise HTTPException(status_code=403, detail="无权访问此会话")
        else:
            session = ChatSession(
                title=request.message[:30] + ("..." if len(request.message) > 30 else ""),
                session_type=request.session_type,
                user_id=user.id
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # 保存用户消息
        user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
        db.add(user_msg)
        db.commit()

        # 获取聊天历史
        history = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id,
            ChatMessage.created_at < user_msg.created_at
        ).order_by(ChatMessage.created_at).all()
        chat_history = [{"role": msg.role, "content": msg.content} for msg in history]

        # 从知识库检索上下文
        context = ""
        source_details = []  # 存储详细的来源信息
        if request.kb_ids:
            context = rag_service.build_context(request.kb_ids, request.message)
            # 提取来源信息（包含详细内容）
            if context:
                search_results = embedding_service.search_similar(request.kb_ids, request.message, k=8)
                # 使用 rerank 服务获取重排序分数
                from app.services.rerank import rerank_service
                if rerank_service.is_enabled():
                    search_results = rerank_service.rerank_sync(request.message, search_results, top_k=4)

                for doc in search_results[:4]:
                    source_details.append({
                        "kb_name": doc['metadata'].get('kb_name', '未知知识库'),
                        "doc_name": doc['metadata'].get('source', '未知文档'),
                        "content": doc['content'][:500] + ("..." if len(doc['content']) > 500 else ""),
                        "rerank_score": doc.get('rerank_score'),
                        "distance": doc.get('distance')
                    })

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
                sources=source_details if source_details else None,
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
async def get_sessions(
    session_type: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """获取所有聊天会话，可选按类型过滤"""
    query = db.query(ChatSession)
    if session_type:
        query = query.filter(ChatSession.session_type == session_type)
    # 非管理员只能看自己的会话
    if user.role != "admin":
        query = query.filter(ChatSession.user_id == user.id)
    sessions = query.order_by(ChatSession.created_at.desc()).all()

    # 构建响应，包含用户名
    session_list = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "title": session.title,
            "session_type": session.session_type,
            "user_id": session.user_id,
            "username": session.user.username if session.user else None,
            "created_at": session.created_at
        }
        session_list.append(ChatSessionResponse(**session_dict, messages=[]))

    return ChatSessionListResponse(sessions=session_list)


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """获取指定会话的详细信息"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 权限检查
    if session.user_id and session.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问此会话")

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
                "created_at": msg.created_at,
                **parse_message_metadata(msg)  # 展开 metadata 中的字段
            }
            for msg in messages
        ]
    }
    return ChatSessionResponse(**session_dict)


@router.delete("/chat/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """删除指定会话"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    # 权限检查
    if session.user_id and session.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除此会话")

    # 查找并删除关联的临时知识库
    temp_kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.session_id == session_id,
        KnowledgeBase.is_temporary == True
    ).first()
    if temp_kb:
        # 删除ChromaDB中的向量数据
        embedding_service.delete_collection(temp_kb.id)
        # 删除数据库记录（会级联删除Document和Chunk）
        db.delete(temp_kb)

    db.delete(session)
    db.commit()
    return {"message": "会话已删除"}


@router.put("/chat/sessions/{session_id}")
async def rename_session(
    session_id: int,
    request: SessionRenameRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """重命名会话"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    # 权限检查
    if session.user_id and session.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权修改此会话")
    session.title = request.title
    db.commit()
    return {"message": "会话已重命名", "id": session_id, "title": request.title}


async def stream_agent_response(
    session_id: int,
    agent_generator: AsyncGenerator[dict, None],
    db: Session
) -> AsyncGenerator[str, None]:
    """流式发送Agent响应"""
    full_response = ""
    thinking_steps = []
    search_results = None
    sources = None
    source_details = None

    try:
        async for event in agent_generator:
            event_type = event.get("type")

            if event_type == "answer":
                # 最终回答内容
                content = event.get("content", "")
                full_response += content
                data = {
                    "type": "chunk",
                    "content": content
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

            elif event_type in ["thought", "tool_call", "tool_result"]:
                # 思考过程
                thinking_steps.append(event)
                data = {
                    "type": event_type,
                    "content": event.get("content", ""),
                    "tool_name": event.get("tool_name"),
                    "tool_args": event.get("tool_args")
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

            elif event_type == "search_data":
                # 搜索结果数据
                search_results = event.get("search_results")
                sources = event.get("sources")
                source_details = event.get("source_details")

            elif event_type == "error":
                # 错误
                error_data = {"type": "error", "message": event.get("content", "未知错误")}
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                return

    except Exception as e:
        error_data = {"type": "error", "message": str(e)}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        return

    # 保存完整的助手消息到数据库
    try:
        # 构建extra_data，保存thinking_steps和搜索结果
        extra_data = {}
        if thinking_steps:
            extra_data["thinking_steps"] = thinking_steps
        if search_results:
            extra_data["search_results"] = search_results
        if sources:
            extra_data["sources"] = sources
        if source_details:
            extra_data["source_details"] = source_details

        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=full_response,
            extra_data=json.dumps(extra_data, ensure_ascii=False) if extra_data else None
        )
        db.add(assistant_msg)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save assistant message: {e}")

    # 发送完成信号
    end_data = {
        "type": "end",
        "session_id": session_id,
        "thinking_steps": thinking_steps if thinking_steps else None,
        "search_results": search_results,
        "sources": sources,
        "source_details": source_details
    }
    yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"


@router.post("/chat/agent")
async def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """
    Agent驱动的聊天接口

    - Agent自主决定是否检索
    - 支持多轮检索和推理
    - 流式返回思考过程
    - kb_ids可选：若提供则限定范围，否则Agent自主选择
    """
    try:
        # 获取或创建会话
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")
            # 权限检查
            if session.user_id and session.user_id != user.id and user.role != "admin":
                raise HTTPException(status_code=403, detail="无权访问此会话")
        else:
            session = ChatSession(
                title=request.message[:30] + ("..." if len(request.message) > 30 else ""),
                session_type="agentic",
                user_id=user.id
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # 保存用户消息
        user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
        db.add(user_msg)
        db.commit()

        # 获取聊天历史
        history = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id,
            ChatMessage.created_at < user_msg.created_at
        ).order_by(ChatMessage.created_at).all()
        chat_history = [{"role": msg.role, "content": msg.content} for msg in history]

        # 执行Agent
        agent_generator = agent_service.run(
            query=request.message,
            chat_history=chat_history,
            kb_ids=request.kb_ids,
            use_web_search=request.use_web_search
        )

        # 返回 SSE 响应
        return StreamingResponse(
            stream_agent_response(
                session_id=session.id,
                agent_generator=agent_generator,
                db=db
            ),
            media_type="text/event-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Agent聊天处理失败: {str(e)}")


@router.post("/chat/upload", response_model=ChatUploadResponse)
async def upload_chat_files(
    files: List[UploadFile] = File(...),
    session_id: int = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """
    聊天文件上传接口 - 创建临时知识库与会话绑定

    - **files**: 上传的文件列表（支持 txt, md, pdf, docx）
    - **session_id**: 会话ID（可选，不传则自动创建新会话）
    """
    try:
        # 获取或创建会话
        if session_id:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")

            # 权限检查
            if session.user_id and session.user_id != user.id and user.role != "admin":
                raise HTTPException(status_code=403, detail="无权访问此会话")
        else:
            # 创建新会话
            session = ChatSession(
                title="文件对话",
                session_type="rag",
                user_id=user.id
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # 验证文件
        if not files:
            raise HTTPException(status_code=400, detail="请上传至少一个文件")

        for file in files:
            if not FileParser.is_supported(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件格式: {file.filename}，仅支持 txt, md, pdf, docx"
                )

        # 查找或创建临时知识库
        temp_kb = db.query(KnowledgeBase).filter(
            KnowledgeBase.session_id == session.id,
            KnowledgeBase.is_temporary == True
        ).first()

        if not temp_kb:
            # 创建新的临时知识库
            temp_kb = KnowledgeBase(
                name=f"临时文档_{session.id}",
                description="聊天会话临时知识库",
                is_temporary=True,
                session_id=session.id,
                user_id=user.id,
                chunk_size=400,  # 限制分块大小以适应嵌入模型的512 token限制
                chunk_overlap=50
            )
            db.add(temp_kb)
            db.commit()
            db.refresh(temp_kb)

            # 创建上传目录
            kb_upload_dir = os.path.join(UPLOAD_DIR, str(temp_kb.id))
            os.makedirs(kb_upload_dir, exist_ok=True)
        else:
            kb_upload_dir = os.path.join(UPLOAD_DIR, str(temp_kb.id))
            os.makedirs(kb_upload_dir, exist_ok=True)

        # 处理上传的文件
        document_responses = []
        for file in files:
            # 保存文件
            file_content = await file.read()
            file_path = await FileParser.save_uploaded_file(
                file_content,
                file.filename,
                kb_upload_dir
            )

            # 解析文件内容
            try:
                text_content = FileParser.extract_text(file_path, file.filename)
            except Exception as e:
                # 清理已保存的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=400, detail=f"文件解析失败 {file.filename}: {str(e)}")

            # 创建文档记录
            doc = Document(
                kb_id=temp_kb.id,
                filename=file.filename,
                file_path=file_path,
                file_size=len(file_content),
                file_type=get_file_type(file.filename),
                chunk_count=0,
                status="processing"
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # 分块并存储向量
            chunks = embedding_service.split_text(
                text_content,
                chunk_size=temp_kb.chunk_size,
                chunk_overlap=temp_kb.chunk_overlap
            )

            # 创建分块记录和元数据
            chunk_records = []
            metadatas = []
            for i, chunk_content in enumerate(chunks):
                chunk_record = Chunk(
                    doc_id=doc.id,
                    content=chunk_content,
                    char_count=len(chunk_content),
                    token_count=count_tokens(chunk_content),
                    enabled=True,
                    sort_order=i
                )
                chunk_records.append(chunk_record)
                metadatas.append({
                    "doc_id": doc.id,
                    "chunk_index": i,
                    "source": file.filename,
                    "kb_name": temp_kb.name,
                    "enabled": True
                })

            # 批量保存分块
            db.add_all(chunk_records)
            db.commit()

            # 嵌入并存储到ChromaDB
            if chunks:
                embedding_service.embed_and_store(temp_kb.id, chunks, metadatas)

            # 更新文档的分块数量
            doc.chunk_count = len(chunks)
            doc.status = "completed"
            db.commit()
            db.refresh(doc)

            # 构建响应
            document_responses.append(DocumentResponse(
                id=doc.id,
                kb_id=doc.kb_id,
                filename=doc.filename,
                file_path=doc.file_path,
                file_size=doc.file_size,
                file_type=doc.file_type,
                chunk_count=doc.chunk_count,
                source=doc.source,
                processing_mode=doc.processing_mode,
                status=doc.status,
                enabled=doc.enabled,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ))

        return ChatUploadResponse(
            session_id=session_id,
            kb_id=temp_kb.id,
            documents=document_responses
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
