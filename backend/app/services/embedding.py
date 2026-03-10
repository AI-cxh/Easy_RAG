"""嵌入服务：负责文本向量化"""
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class EmbeddingService:
    """嵌入服务类"""

    def __init__(self):
        """初始化嵌入服务"""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

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

    def split_text(self, text: str) -> List[str]:
        """将文本分割成块"""
        return self.text_splitter.split_text(text)

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

        collection = self.get_or_create_collection(kb_id)

        # 生成嵌入向量
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
