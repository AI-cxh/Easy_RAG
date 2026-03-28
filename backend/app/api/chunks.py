"""分块管理API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List as ListType

from app.models.database import get_db
from app.models.models import Document, Chunk, KnowledgeBase, User
from app.models.schemas import (
    ChunkResponse, ChunkListResponse, ChunkCreate, ChunkUpdate, ChunkBatchRequest
)
from app.services.embedding import embedding_service
from app.services.auth import get_current_user, require_user
import tiktoken


router = APIRouter()

# 初始化 tiktoken 编码器
tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """计算文本的 Token 数"""
    return len(tokenizer.encode(text))


def check_doc_permission(document: Document, user: User, db: Session) -> KnowledgeBase:
    """检查文档权限，返回知识库"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == document.kb_id).first()
    if knowledge_base and user.role != "admin" and knowledge_base.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问此文档")
    return knowledge_base


@router.get("/chunks/{doc_id}", response_model=ChunkListResponse)
async def get_chunks(
    doc_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    enabled: bool = Query(None, description="启用状态筛选"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """获取文档的分块列表（分页）"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 权限检查
    check_doc_permission(document, user, db)

    query = db.query(Chunk).filter(Chunk.doc_id == doc_id)

    # 状态筛选
    if enabled is not None:
        query = query.filter(Chunk.enabled == enabled)

    # 获取总数
    total = query.count()

    # 分页查询
    chunks = query.order_by(Chunk.sort_order).offset((page - 1) * page_size).limit(page_size).all()

    return ChunkListResponse(
        items=chunks,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/chunks/{doc_id}", response_model=ChunkResponse)
async def create_chunk(
    doc_id: int,
    chunk_data: ChunkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """新建分块"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 权限检查
    check_doc_permission(document, user, db)

    # 获取当前最大排序号
    max_order = db.query(Chunk).filter(Chunk.doc_id == doc_id).count()

    char_count = len(chunk_data.content)
    token_count = count_tokens(chunk_data.content)

    chunk = Chunk(
        doc_id=doc_id,
        content=chunk_data.content,
        char_count=char_count,
        token_count=token_count,
        enabled=True,
        sort_order=max_order
    )
    db.add(chunk)

    # 更新文档的分块数
    document.chunk_count = db.query(Chunk).filter(Chunk.doc_id == doc_id).count() + 1

    db.commit()
    db.refresh(chunk)

    # 同步到向量库
    kb_id = document.kb_id
    metadatas = [{
        "source": f"{document.filename}[new]",
        "doc_id": doc_id,
        "chunk_index": chunk.sort_order,
        "enabled": True
    }]
    embedding_service.embed_and_store(kb_id, [chunk_data.content], metadatas)

    return chunk


@router.put("/chunks/{chunk_id}", response_model=ChunkResponse)
async def update_chunk(
    chunk_id: int,
    chunk_data: ChunkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """编辑分块"""
    chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="分块不存在")

    document = db.query(Document).filter(Document.id == chunk.doc_id).first()
    # 权限检查
    check_doc_permission(document, user, db)

    if chunk_data.content is not None:
        chunk.content = chunk_data.content
        chunk.char_count = len(chunk_data.content)
        chunk.token_count = count_tokens(chunk_data.content)

        # 更新向量库中的内容
        kb_id = document.kb_id
        metadatas = [{
            "source": f"{document.filename}[edit]",
            "doc_id": chunk.doc_id,
            "chunk_index": chunk.sort_order,
            "enabled": chunk.enabled
        }]
        embedding_service.rebuild_vectors(kb_id, chunk.doc_id, [chunk_data.content], metadatas)

    if chunk_data.enabled is not None:
        chunk.enabled = chunk_data.enabled
        # 同步更新 ChromaDB 中的 enabled 状态
        embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, chunk.doc_id, chunk_data.enabled)

    db.commit()
    db.refresh(chunk)
    return chunk


@router.delete("/chunks/{chunk_id}")
async def delete_chunk(
    chunk_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """删除分块"""
    chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="分块不存在")

    document = db.query(Document).filter(Document.id == chunk.doc_id).first()
    # 权限检查
    check_doc_permission(document, user, db)
    kb_id = document.kb_id

    db.delete(chunk)

    # 更新文档的分块数
    document.chunk_count = db.query(Chunk).filter(Chunk.doc_id == chunk.doc_id).count() - 1

    db.commit()

    # 从向量库中删除
    embedding_service.delete_chunks_by_doc_id(kb_id, chunk.doc_id)

    return {"message": "分块已删除"}


@router.put("/chunks/{chunk_id}/toggle", response_model=ChunkResponse)
async def toggle_chunk(
    chunk_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """切换分块启用状态"""
    chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="分块不存在")

    document = db.query(Document).filter(Document.id == chunk.doc_id).first()
    # 权限检查
    check_doc_permission(document, user, db)

    new_enabled = not chunk.enabled
    chunk.enabled = new_enabled
    db.commit()
    db.refresh(chunk)

    # 同步更新 ChromaDB
    if document:
        embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, chunk.doc_id, new_enabled)

    return chunk


@router.post("/chunks/batch-enable")
async def batch_enable_chunks(
    request: ChunkBatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """批量启用分块"""
    chunks = db.query(Chunk).filter(Chunk.id.in_(request.chunk_ids)).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="未找到分块")

    # 权限检查
    for chunk in chunks:
        document = db.query(Document).filter(Document.id == chunk.doc_id).first()
        if document:
            check_doc_permission(document, user, db)

    for chunk in chunks:
        chunk.enabled = True

    db.commit()

    # 同步更新 ChromaDB（按文档分组）
    doc_ids = set(chunk.doc_id for chunk in chunks)
    for doc_id in doc_ids:
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, doc_id, True)

    return {"message": f"已启用 {len(chunks)} 个分块"}


@router.post("/chunks/batch-disable")
async def batch_disable_chunks(
    request: ChunkBatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """批量禁用分块"""
    chunks = db.query(Chunk).filter(Chunk.id.in_(request.chunk_ids)).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="未找到分块")

    # 权限检查
    for chunk in chunks:
        document = db.query(Document).filter(Document.id == chunk.doc_id).first()
        if document:
            check_doc_permission(document, user, db)

    for chunk in chunks:
        chunk.enabled = False

    db.commit()

    # 同步更新 ChromaDB（按文档分组）
    doc_ids = set(chunk.doc_id for chunk in chunks)
    for doc_id in doc_ids:
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, doc_id, False)

    return {"message": f"已禁用 {len(chunks)} 个分块"}


@router.post("/chunks/enable-all/{doc_id}")
async def enable_all_chunks(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """全量启用文档的所有分块"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 权限检查
    check_doc_permission(document, user, db)

    db.query(Chunk).filter(Chunk.doc_id == doc_id).update({"enabled": True})
    db.commit()

    # 同步更新 ChromaDB
    embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, doc_id, True)

    count = db.query(Chunk).filter(Chunk.doc_id == doc_id).count()
    return {"message": f"已启用 {count} 个分块"}


@router.post("/chunks/disable-all/{doc_id}")
async def disable_all_chunks(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """全量禁用文档的所有分块"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 权限检查
    check_doc_permission(document, user, db)

    db.query(Chunk).filter(Chunk.doc_id == doc_id).update({"enabled": False})
    db.commit()

    # 同步更新 ChromaDB
    embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, doc_id, False)

    count = db.query(Chunk).filter(Chunk.doc_id == doc_id).count()
    return {"message": f"已禁用 {count} 个分块"}


@router.post("/chunks/rebuild-vectors/{doc_id}")
async def rebuild_vectors(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    """重建文档的向量"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 权限检查
    check_doc_permission(document, user, db)

    # 获取所有启用的分块
    chunks = db.query(Chunk).filter(Chunk.doc_id == doc_id, Chunk.enabled == True).order_by(Chunk.sort_order).all()

    if not chunks:
        return {"message": "没有启用的分块需要重建"}

    kb_id = document.kb_id

    # 准备数据
    chunk_contents = [chunk.content for chunk in chunks]
    metadatas = [{
        "source": f"{document.filename}[{i+1}]",
        "doc_id": doc_id,
        "chunk_index": i
    } for i in range(len(chunks))]

    # 重建向量
    count = embedding_service.rebuild_vectors(kb_id, doc_id, chunk_contents, metadatas)

    return {"message": f"已重建 {count} 个向量"}
