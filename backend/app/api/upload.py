"""文件上传API路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
import os

from app.models.database import get_db
from app.models.models import KnowledgeBase, Document, Chunk
from app.models.schemas import DocumentResponse, DocumentListResponse, DocumentUpdateRequest
from app.utils.file_parser import FileParser
from app.services.embedding import embedding_service
from app.config import settings
import tiktoken


router = APIRouter()
UPLOAD_DIR = settings.CHROMA_DB_PATH + "/../uploads"

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化 tiktoken 编码器
tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """计算文本的 Token 数"""
    return len(tokenizer.encode(text))


def get_file_type(filename: str) -> str:
    """获取文件类型"""
    ext = os.path.splitext(filename.lower())[1]
    type_map = {
        '.txt': 'text',
        '.md': 'markdown',
        '.pdf': 'pdf',
        '.docx': 'docx'
    }
    return type_map.get(ext, 'unknown')


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

        # 获取文件大小和类型
        file_size = file_parser.get_file_size(file_path)
        file_type = get_file_type(file.filename)

        # 保存文档记录
        document = Document(
            kb_id=kb_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            chunk_count=len(chunks),
            source="upload",
            processing_mode="auto",
            status="completed",
            enabled=True
        )
        db.add(document)
        db.flush()  # 获取 document.id

        # 准备元数据 - 包含 doc_id 和 enabled
        metadatas = [
            {
                "source": f"{file.filename}[{i+1}]",
                "doc_id": document.id,
                "chunk_index": i,
                "enabled": True
            }
            for i in range(len(chunks))
        ]

        # 嵌入并存储到 ChromaDB
        embedding_service.embed_and_store(kb_id, chunks, metadatas)

        # 保存分块到数据库
        for i, chunk_content in enumerate(chunks):
            char_count = len(chunk_content)
            token_count = count_tokens(chunk_content)
            chunk = Chunk(
                doc_id=document.id,
                content=chunk_content,
                char_count=char_count,
                token_count=token_count,
                enabled=True,
                sort_order=i
            )
            db.add(chunk)

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

    删除文档记录、关联的分块和文件
    """
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    try:
        # 删除文件
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # 删除关联的分块（级联删除会自动处理）
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


@router.put("/upload/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(doc_id: int, request: DocumentUpdateRequest, db: Session = Depends(get_db)):
    """更新文档信息"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    if request.filename is not None:
        document.filename = request.filename
    if request.source is not None:
        document.source = request.source
    if request.enabled is not None:
        document.enabled = request.enabled

    db.commit()
    db.refresh(document)
    return document


@router.put("/upload/documents/{doc_id}/toggle", response_model=DocumentResponse)
async def toggle_document(doc_id: int, db: Session = Depends(get_db)):
    """切换文档启用状态"""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    new_enabled = not document.enabled
    document.enabled = new_enabled

    # 同步更新所有分块的启用状态
    db.query(Chunk).filter(Chunk.doc_id == doc_id).update({"enabled": new_enabled})

    db.commit()
    db.refresh(document)

    # 同步更新 ChromaDB 中的 metadata
    embedding_service.set_chunks_enabled_by_doc_id(document.kb_id, doc_id, new_enabled)

    return document
