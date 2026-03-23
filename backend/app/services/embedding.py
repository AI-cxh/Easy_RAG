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
            metadatas: 元数据列表

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

        # 添加到ChromaDB
        ids = [f"{kb_id}_{i}_{hash(chunk)}" for i, chunk in enumerate(chunks)]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

        return len(chunks)

    def search_similar(self, kb_ids: List[int], query: str, k: int = 4) -> List[dict]:
        """
        在指定知识库中搜索相似文档

        Args:
            kb_ids: 知识库ID列表
            query: 查询文本
            k: 返回结果数量

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
                search_result = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(k, len(collection.get()['ids']) if collection.get()['ids'] else k)
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


# 全局嵌入服务实例
embedding_service = EmbeddingService()
