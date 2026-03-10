"""知识库API路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import KnowledgeBase, Document
from app.models.schemas import KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseWithDocuments, DocumentListResponse
from app.services.embedding import embedding_service


router = APIRouter()


@router.get("", response_model=list[KnowledgeBaseResponse])
async def get_knowledge_bases(db: Session = Depends(get_db)):
    """获取所有知识库列表"""
    knowledge_bases = db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()
    return knowledge_bases


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """创建新知识库"""
    # 检查名称是否已存在
    existing = db.query(KnowledgeBase).filter(KnowledgeBase.name == kb_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="知识库名称已存在")

    knowledge_base = KnowledgeBase(name=kb_data.name, description=kb_data.description)
    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)
    return knowledge_base


@router.get("/{kb_id}", response_model=KnowledgeBaseWithDocuments)
async def get_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """获取知识库详情（包含文档列表）"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return knowledge_base


@router.delete("/{kb_id}")
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


@router.get("/{kb_id}/documents", response_model=DocumentListResponse)
async def get_documents(kb_id: int, db: Session = Depends(get_db)):
    """获取知识库的文档列表"""
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    documents = db.query(Document).filter(Document.kb_id == kb_id).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(documents=documents, total=len(documents))
