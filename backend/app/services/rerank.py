"""重排序服务：对检索结果进行二次排序"""
import httpx
from typing import List, Dict, Optional
from app.config import settings


class RerankService:
    """重排序服务类"""

    def __init__(self):
        """初始化重排序服务"""
        self.model = settings.RERANK_MODEL
        self.api_key = settings.RERANK_API_KEY
        self.api_base = settings.RERANK_API_BASE

    def is_enabled(self) -> bool:
        """检查重排序服务是否启用"""
        return self.api_key is not None and self.api_base is not None

    async def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 4
    ) -> List[Dict]:
        """
        对文档进行重排序

        Args:
            query: 查询文本
            documents: 文档列表，每个文档包含 content 和 metadata
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        if not self.is_enabled():
            return documents[:top_k]

        if not documents:
            return []

        # 提取文档内容
        doc_texts = [doc['content'] for doc in documents]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/rerank",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "query": query,
                        "documents": doc_texts,
                        "top_n": min(top_k, len(documents)),
                        "return_documents": False
                    }
                )
                response.raise_for_status()
                result = response.json()

            # 根据重排序结果重新组织文档
            reranked_docs = []
            for item in result.get('results', []):
                index = item.get('index', 0)
                relevance_score = item.get('relevance_score', 0.0)
                if 0 <= index < len(documents):
                    doc = documents[index].copy()
                    doc['rerank_score'] = relevance_score
                    reranked_docs.append(doc)

            return reranked_docs[:top_k]

        except Exception as e:
            print(f"重排序失败: {e}")
            # 失败时返回原始排序的前 top_k 个
            return documents[:top_k]

    def rerank_sync(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 4
    ) -> List[Dict]:
        """
        同步版本的重排序方法

        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回的文档数量

        Returns:
            重排序后的文档列表
        """
        if not self.is_enabled():
            return documents[:top_k]

        if not documents:
            return []

        doc_texts = [doc['content'] for doc in documents]

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.api_base}/rerank",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "query": query,
                        "documents": doc_texts,
                        "top_n": min(top_k, len(documents)),
                        "return_documents": False
                    }
                )
                response.raise_for_status()
                result = response.json()

            reranked_docs = []
            for item in result.get('results', []):
                index = item.get('index', 0)
                relevance_score = item.get('relevance_score', 0.0)
                if 0 <= index < len(documents):
                    doc = documents[index].copy()
                    doc['rerank_score'] = relevance_score
                    reranked_docs.append(doc)

            return reranked_docs[:top_k]

        except Exception as e:
            print(f"重排序失败: {e}")
            return documents[:top_k]


# 全局重排序服务实例
rerank_service = RerankService()
