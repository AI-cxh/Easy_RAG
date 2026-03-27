"""
数据迁移脚本：将 ChromaDB 中的分块数据同步到 SQLite

使用方法：
    cd backend
    python scripts/migrate_chunks.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.models.database import SessionLocal, engine, Base
from app.models.models import KnowledgeBase, Document, Chunk
from app.services.embedding import embedding_service
import tiktoken


def count_tokens(text: str) -> int:
    """计算文本的 Token 数"""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    return len(tokenizer.encode(text))


def migrate_chunks():
    """迁移分块数据"""
    db: Session = SessionLocal()

    try:
        print("开始迁移分块数据...")

        # 确保所有表已创建
        Base.metadata.create_all(bind=engine)

        # 获取所有知识库
        knowledge_bases = db.query(KnowledgeBase).all()
        print(f"找到 {len(knowledge_bases)} 个知识库")

        total_chunks = 0
        total_docs = 0

        for kb in knowledge_bases:
            print(f"\n处理知识库: {kb.name} (ID: {kb.id})")

            # 获取该知识库的所有文档
            documents = db.query(Document).filter(Document.kb_id == kb.id).all()

            # 从 ChromaDB 获取所有分块
            try:
                chroma_chunks = embedding_service.get_all_chunks(kb.id)
                print(f"  ChromaDB 中有 {len(chroma_chunks)} 个分块")
            except Exception as e:
                print(f"  无法获取 ChromaDB 数据: {e}")
                continue

            if not chroma_chunks:
                continue

            # 按 doc_id 分组
            chunks_by_doc: dict = {}
            for chunk in chroma_chunks:
                doc_id = chunk['metadata'].get('doc_id')
                if doc_id:
                    if doc_id not in chunks_by_doc:
                        chunks_by_doc[doc_id] = []
                    chunks_by_doc[doc_id].append(chunk)

            # 为每个文档创建分块记录
            for doc in documents:
                # 检查是否已有分块记录
                existing_count = db.query(Chunk).filter(Chunk.doc_id == doc.id).count()
                if existing_count > 0:
                    print(f"  文档 {doc.filename} 已有 {existing_count} 个分块，跳过")
                    continue

                # 获取该文档的分块
                doc_chunks = chunks_by_doc.get(doc.id, [])
                if not doc_chunks:
                    # 尝试通过 source 匹配
                    for chunk in chroma_chunks:
                        source = chunk['metadata'].get('source', '')
                        if source.startswith(doc.filename):
                            if doc.id not in chunks_by_doc:
                                chunks_by_doc[doc.id] = []
                            chunks_by_doc[doc.id].append(chunk)
                    doc_chunks = chunks_by_doc.get(doc.id, [])

                if not doc_chunks:
                    print(f"  文档 {doc.filename} 没有对应的分块数据")
                    continue

                # 创建分块记录
                for i, chunk_data in enumerate(doc_chunks):
                    content = chunk_data['document']
                    char_count = len(content)
                    token_count = count_tokens(content)

                    chunk = Chunk(
                        doc_id=doc.id,
                        content=content,
                        char_count=char_count,
                        token_count=token_count,
                        enabled=True,
                        sort_order=i
                    )
                    db.add(chunk)
                    total_chunks += 1

                # 更新文档的分块数
                doc.chunk_count = len(doc_chunks)
                total_docs += 1
                print(f"  文档 {doc.filename}: 创建了 {len(doc_chunks)} 个分块")

            db.commit()

        print(f"\n迁移完成!")
        print(f"  处理文档: {total_docs}")
        print(f"  创建分块: {total_chunks}")

    except Exception as e:
        print(f"迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def update_existing_fields():
    """更新现有数据的新字段"""
    db: Session = SessionLocal()

    try:
        print("\n更新现有数据的新字段...")

        # 更新知识库
        kbs = db.query(KnowledgeBase).all()
        for kb in kbs:
            if not kb.embedding_model:
                kb.embedding_model = "text-embedding-ada-002"
            if not kb.owner:
                kb.owner = ""
        print(f"  更新了 {len(kbs)} 个知识库")

        # 更新文档
        docs = db.query(Document).all()
        for doc in docs:
            if not doc.source:
                doc.source = "upload"
            if not doc.processing_mode:
                doc.processing_mode = "auto"
            if not doc.status:
                doc.status = "completed"
            if doc.enabled is None:
                doc.enabled = True
            if not doc.file_type:
                ext = doc.filename.split('.').pop().lower() if '.' in doc.filename else ''
                type_map = {'txt': 'text', 'md': 'markdown', 'pdf': 'pdf', 'docx': 'docx'}
                doc.file_type = type_map.get(ext, ext)
        print(f"  更新了 {len(docs)} 个文档")

        db.commit()
        print("字段更新完成!")

    except Exception as e:
        print(f"字段更新失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("知识库管理模块数据迁移脚本")
    print("=" * 50)

    # 先更新字段
    update_existing_fields()

    # 再迁移分块数据
    migrate_chunks()

    print("\n全部完成!")
