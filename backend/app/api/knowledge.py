"""知识库API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import get_db
from app.models.models import KnowledgeBase, Document
from app.models.schemas import (
    KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseWithDocuments,
    KnowledgeBaseListResponse, KnowledgeBaseListItem, KnowledgeBaseStatsResponse, KnowledgeBaseRenameRequest,
    DocumentListResponse
)
from app.services.embedding import embedding_service


router = APIRouter()


@router.get("/knowledge/stats", response_model=KnowledgeBaseStatsResponse)
async def get_knowledge_base_stats(db: Session = Depends(get_db)):
    """获取知识库统计数据"""
    # 知识库总数
    total_kbs = db.query(KnowledgeBase).count()

    # 文档总数
    total_docs = db.query(Document).count()

    # 含文档的知识库数
    kbs_with_docs = db.query(KnowledgeBase).join(Document).distinct().count()

    return KnowledgeBaseStatsResponse(
        total_kbs=total_kbs,
        total_docs=total_docs,
        kbs_with_docs=kbs_with_docs
    )


@router.get("/knowledge", response_model=KnowledgeBaseListResponse)
async def get_knowledge_bases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query("", description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取知识库列表（分页）"""
    query = db.query(KnowledgeBase)

    # 搜索过滤
    if search:
        query = query.filter(KnowledgeBase.name.ilike(f"%{search}%"))

    # 获取总数
    total = query.count()

    # 分页查询，同时获取文档数量
    knowledge_bases = query.order_by(KnowledgeBase.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 为每个知识库添加文档数量
    items = []
    for kb in knowledge_bases:
        doc_count = db.query(Document).filter(Document.kb_id == kb.id).count()
        kb_dict = {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "embedding_model": kb.embedding_model or "text-embedding-ada-002",
            "owner": kb.owner or "",
            "created_at": kb.created_at,
            "updated_at": kb.updated_at,
            "doc_count": doc_count
        }
        items.append(KnowledgeBaseListItem(**kb_dict))

    return KnowledgeBaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/knowledge", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """创建新知识库"""
    # 检查名称是否已存在
    existing = db.query(KnowledgeBase).filter(KnowledgeBase.name == kb_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="知识库名称已存在")

    knowledge_base = KnowledgeBase(
        name=kb_data.name,
        description=kb_data.description,
        chunk_size=kb_data.chunk_size or 1000,
        chunk_overlap=kb_data.chunk_overlap or 200,
        embedding_model=kb_data.embedding_model or "text-embedding-ada-002",
        owner=kb_data.owner or ""
    )
    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)
    return knowledge_base


@router.get("/knowledge/{kb_id}", response_model=KnowledgeBaseWithDocuments)
async def get_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """获取知识库详情（包含文档列表）"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return knowledge_base


@router.delete("/knowledge/{kb_id}")
async def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """删除知识库（包括所有文档和向量数据）"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 删除ChromaDB中的向量数据
    embedding_service.delete_collection(kb_id)

    # 删除数据库记录（会级联删除文档）
    db.delete(knowledge_base)
    db.commit()
    return {"message": "知识库已删除"}


@router.put("/knowledge/{kb_id}")
async def update_knowledge_base(kb_id: int, request: KnowledgeBaseRenameRequest, db: Session = Depends(get_db)):
    """更新知识库信息"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 检查名称是否与其他知识库重复
    existing = db.query(KnowledgeBase).filter(
        KnowledgeBase.name == request.name,
        KnowledgeBase.id != kb_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="知识库名称已存在")

    knowledge_base.name = request.name
    if request.description is not None:
        knowledge_base.description = request.description
    if request.chunk_size is not None:
        knowledge_base.chunk_size = request.chunk_size
    if request.chunk_overlap is not None:
        knowledge_base.chunk_overlap = request.chunk_overlap
    if request.embedding_model is not None:
        knowledge_base.embedding_model = request.embedding_model
    if request.owner is not None:
        knowledge_base.owner = request.owner

    db.commit()
    return {
        "message": "知识库已更新",
        "id": kb_id,
        "name": request.name,
        "description": request.description,
        "chunk_size": knowledge_base.chunk_size,
        "chunk_overlap": knowledge_base.chunk_overlap,
        "embedding_model": knowledge_base.embedding_model,
        "owner": knowledge_base.owner
    }


@router.get("/knowledge/{kb_id}/documents", response_model=DocumentListResponse)
async def get_documents(
    kb_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query("", description="搜索关键词"),
    status: str = Query("", description="状态筛选"),
    db: Session = Depends(get_db)
):
    """获取知识库的文档列表（分页）"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    query = db.query(Document).filter(Document.kb_id == kb_id)

    # 搜索过滤
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    # 状态筛选
    if status:
        query = query.filter(Document.status == status)

    # 获取总数
    total = query.count()

    # 分页查询
    documents = query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return DocumentListResponse(
        items=documents,
        total=total,
        page=page,
        page_size=page_size
    )
