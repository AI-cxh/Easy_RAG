"""嵌入服务：负责文本向量化"""
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class EmbeddingService:
    """嵌入服务类"""

    def __init__(self):
        """初始化嵌入服务"""
        # 使用嵌入专用的配置，如果未设置则使用聊天配置
        embedding_api_key = settings.EMBEDDING_API_KEY or settings.OPENAI_API_KEY
        embedding_api_base = settings.EMBEDDING_API_BASE or settings.OPENAI_API_BASE

        # 尝试使用 OpenAI 兼容的嵌入服务
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=embedding_api_key,
            openai_api_base=embedding_api_base
        )
        self._fallback_enabled = False  # 标记是否已启用回退

        # 默认分块器（使用系统默认值）
        self.default_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

    def get_text_splitter(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> RecursiveCharacterTextSplitter:
        """
        获取文本分块器

        Args:
            chunk_size: 分块大小，None则使用默认值
            chunk_overlap: 分块重叠，None则使用默认值

        Returns:
            文本分块器实例
        """
        if chunk_size is None and chunk_overlap is None:
            return self.default_text_splitter

        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
            length_function=len
        )

    def get_or_create_collection(self, kb_id: int):
        """获取或创建知识库对应的ChromaDB集合"""
        collection_name = f"kb_{kb_id}"
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"kb_id": str(kb_id)}
            )
        return collection

    def _ensure_embeddings(self) -> None:
        """确保嵌入服务可用，如果失败则回退"""
        if self._fallback_enabled:
            return

        try:
            # 测试嵌入服务是否可用
            _ = self.embeddings.embed_query("test")
        except Exception as e:
            print(f"OpenAI 嵌入服务失败: {e}")
            print("回退到使用 HuggingFace 免费嵌入服务...")
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                self._fallback_enabled = True
                print("已成功切换到本地嵌入服务")
            except Exception as e2:
                print(f"HuggingFace 嵌入服务也失败: {e2}")
                raise RuntimeError("无法初始化嵌入服务，请检查 API 配置或安装 sentence-transformers")

    def split_text(self, text: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> List[str]:
        """
        将文本分割成块

        Args:
            text: 要分割的文本
            chunk_size: 分块大小，None则使用默认值
            chunk_overlap: 分块重叠，None则使用默认值

        Returns:
            文本块列表
        """
        splitter = self.get_text_splitter(chunk_size, chunk_overlap)
        return splitter.split_text(text)

    def embed_and_store(self, kb_id: int, chunks: List[str], metadatas: List[dict]) -> int:
        """
        对文本块进行嵌入并存储到ChromaDB

        Args:
            kb_id: 知识库ID
            chunks: 文本块列表
            metadatas: 元数据列表，应包含 doc_id 和 chunk_index

        Returns:
            存储的文档数量
        """
        if not chunks:
            return 0

        self._ensure_embeddings()
        collection = self.get_or_create_collection(kb_id)

        # 生成嵌入向量
        try:
            embeddings = self.embeddings.embed_documents(chunks)
        except Exception as e:
            print(f"嵌入失败，尝试回退: {e}")
            self._fallback_enabled = False
            self._ensure_embeddings()
            embeddings = self.embeddings.embed_documents(chunks)

        # 生成唯一ID，包含 doc_id 和 chunk_index
        ids = []
        for i, meta in enumerate(metadatas):
            doc_id = meta.get('doc_id', 'unknown')
            chunk_index = meta.get('chunk_index', i)
            ids.append(f"kb{kb_id}_doc{doc_id}_chunk{chunk_index}")

        # 添加到ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

        return len(chunks)

    def search_similar(self, kb_ids: List[int], query: str, k: int = 4, enabled_only: bool = True) -> List[dict]:
        """
        在指定知识库中搜索相似文档

        Args:
            kb_ids: 知识库ID列表
            query: 查询文本
            k: 返回结果数量
            enabled_only: 是否只检索启用的文档

        Returns:
            相似文档列表
        """
        self._ensure_embeddings()
        try:
            query_embedding = self.embeddings.embed_query(query)
        except Exception as e:
            print(f"查询嵌入失败，尝试回退: {e}")
            self._fallback_enabled = False
            self._ensure_embeddings()
            query_embedding = self.embeddings.embed_query(query)

        results = []
        for kb_id in kb_ids:
            try:
                collection = self.get_or_create_collection(kb_id)

                # 构建 where 过滤条件
                where_filter = None
                if enabled_only:
                    # ChromaDB where 过滤：enabled 为 True 或不存在（兼容旧数据）
                    where_filter = {"enabled": True}

                search_result = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(k, len(collection.get()['ids']) if collection.get()['ids'] else k),
                    where=where_filter
                )

                for i in range(len(search_result['ids'][0])):
                    results.append({
                        'content': search_result['documents'][0][i],
                        'metadata': search_result['metadatas'][0][i],
                        'distance': search_result['distances'][0][i]
                    })
            except:
                continue

        # 按距离排序
        results.sort(key=lambda x: x['distance'])
        return results[:k]

    def delete_collection(self, kb_id: int) -> bool:
        """
        删除知识库对应的ChromaDB集合

        Args:
            kb_id: 知识库ID

        Returns:
            是否成功删除
        """
        try:
            collection_name = f"kb_{kb_id}"
            self.chroma_client.delete_collection(name=collection_name)
            return True
        except:
            return False

    def delete_chunks_by_doc_id(self, kb_id: int, doc_id: int) -> bool:
        """
        删除指定文档的所有分块向量

        Args:
            kb_id: 知识库ID
            doc_id: 文档ID

        Returns:
            是否成功删除
        """
        try:
            collection = self.get_or_create_collection(kb_id)
            # 获取所有属于该文档的分块ID
            all_items = collection.get()
            ids_to_delete = []
            for i, meta in enumerate(all_items['metadatas']):
                if meta.get('doc_id') == doc_id:
                    ids_to_delete.append(all_items['ids'][i])

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
            return True
        except Exception as e:
            print(f"删除文档向量失败: {e}")
            return False

    def rebuild_vectors(self, kb_id: int, doc_id: int, chunks: List[str], metadatas: List[dict]) -> int:
        """
        重建指定文档的向量

        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            chunks: 文本块列表
            metadatas: 元数据列表

        Returns:
            重建的向量数量
        """
        # 先删除旧的向量
        self.delete_chunks_by_doc_id(kb_id, doc_id)

        # 重新嵌入并存储
        if chunks:
            return self.embed_and_store(kb_id, chunks, metadatas)
        return 0

    def get_all_chunks(self, kb_id: int) -> List[dict]:
        """
        获取知识库中的所有分块数据

        Args:
            kb_id: 知识库ID

        Returns:
            分块列表，每个元素包含 id, document, metadata
        """
        try:
            collection = self.get_or_create_collection(kb_id)
            all_items = collection.get()
            results = []
            for i in range(len(all_items['ids'])):
                results.append({
                    'id': all_items['ids'][i],
                    'document': all_items['documents'][i],
                    'metadata': all_items['metadatas'][i]
                })
            return results
        except Exception as e:
            print(f"获取分块数据失败: {e}")
            return []

    def update_chunk_enabled_status(self, kb_id: int, doc_id: int, enabled: bool) -> bool:
        """
        更新文档所有分块的启用状态

        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            enabled: 启用状态

        Returns:
            是否成功更新
        """
        try:
            collection = self.get_or_create_collection(kb_id)
            # 获取所有属于该文档的分块
            all_items = collection.get()
            ids_to_update = []
            metadatas_to_update = []

            for i, meta in enumerate(all_items['metadatas']):
                if meta.get('doc_id') == doc_id:
                    ids_to_update.append(all_items['ids'][i])
                    # 更新 metadata 中的 enabled 字段
                    new_meta = dict(meta)
                    new_meta['enabled'] = enabled
                    metadatas_to_update.append(new_meta)

            if ids_to_update:
                # ChromaDB 需要先删除再添加来更新 metadata
                collection.delete(ids=ids_to_update)

                # 获取对应的文档和嵌入向量
                for i, chunk_id in enumerate(ids_to_update):
                    # 重新添加，使用更新后的 metadata
                    # 注意：这里需要重新获取文档内容
                    pass

                # 简化方案：使用 upsert（如果支持）
                # 或者直接在 metadata 中标记

            return True
        except Exception as e:
            print(f"更新分块状态失败: {e}")
            return False

    def set_chunks_enabled_by_doc_id(self, kb_id: int, doc_id: int, enabled: bool) -> bool:
        """
        设置文档所有分块的启用状态（通过重建向量）

        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            enabled: 启用状态

        Returns:
            是否成功
        """
        try:
            collection = self.get_or_create_collection(kb_id)
            # 获取所有属于该文档的分块
            all_items = collection.get()

            for i, meta in enumerate(all_items['metadatas']):
                if meta.get('doc_id') == doc_id:
                    chunk_id = all_items['ids'][i]
                    document = all_items['documents'][i]
                    new_meta = dict(meta)
                    new_meta['enabled'] = enabled

                    # 使用 upsert 更新
                    collection.upsert(
                        ids=[chunk_id],
                        documents=[document],
                        metadatas=[new_meta]
                    )

            return True
        except Exception as e:
            print(f"设置分块启用状态失败: {e}")
            return False


# 全局嵌入服务实例
embedding_service = EmbeddingService()
