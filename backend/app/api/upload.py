"""文件上传API路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os

from app.models.database import get_db
from app.models.models import KnowledgeBase, Document
from app.models.schemas import DocumentResponse
from app.utils.file_parser import FileParser
from app.services.embedding import embedding_service
from app.config import settings


router = APIRouter()
UPLOAD_DIR = settings.CHROMA_DB_PATH + "/../uploads"

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/{kb_id}", response_model=DocumentResponse)
async def upload_file(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传文件到指定知识库

    支持的文件格式: .txt, .md, .pdf, .docx

    - **kb_id**: 知识库ID
    - **file**: 要上传的文件
    """
    # 检查知识库是否存在
    knowledge_base = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 检查文件格式
    if not FileParser.is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file.filename}。支持的格式: .txt, .md, .pdf, .docx"
        )

    try:
        # 保存文件
        file_content = await file.read()
        file_parser = FileParser()
        file_path = await file_parser.save_uploaded_file(
            file_content, file.filename, UPLOAD_DIR
        )

        # 提取文本
        text = file_parser.extract_text(file_path, file.filename)

        # 分块 - 使用知识库的分块设置
        chunks = embedding_service.split_text(
            text,
            chunk_size=knowledge_base.chunk_size,
            chunk_overlap=knowledge_base.chunk_overlap
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="无法从文件中提取有效文本")

        # 准备元数据
        metadatas = [{"source": f"{file.filename}[{i//10+1}]"} for i in range(len(chunks))]

        # 嵌入并存储
        chunk_count = embedding_service.embed_and_store(kb_id, chunks, metadatas)

        # 获取文件大小
        file_size = file_parser.get_file_size(file_path)

        # 保存文档记录
        document = Document(
            kb_id=kb_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            chunk_count=chunk_count
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # 清理已保存的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.delete("/upload/documents/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """
    删除文档

    删除文档记录和文件
    """
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    try:
        # 删除文件
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # 注意：ChromaDB中的向量数据暂时不删除，需要在重构ChromaDB时实现

        # 删除数据库记录
        kb_id = document.kb_id
        db.delete(document)
        db.commit()

        # 如果知识库没有文档了，重新创建向量集合
        remaining_docs = db.query(Document).filter(Document.kb_id == kb_id).count()
        if remaining_docs == 0:
            embedding_service.delete_collection(kb_id)

        return {"message": "文档已删除"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文档删除失败: {str(e)}")
