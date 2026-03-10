"""RAG核心服务：负责检索增强生成"""
from typing import List, Optional, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

from app.config import settings
from app.services.embedding import embedding_service


class RAGService:
    """RAG服务类"""

    def __init__(self):
        """初始化RAG服务"""
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

    def build_context(self, kb_ids: List[int], query: str) -> str:
        """
        从知识库构建上下文

        Args:
            kb_ids: 知识库ID列表
            query: 查询文本

        Returns:
            上下文字符串
        """
        if not kb_ids:
            return ""

        similar_docs = embedding_service.search_similar(kb_ids, query, k=4)

        if not similar_docs:
            return ""

        context_parts = []
        for i, doc in enumerate(similar_docs, 1):
            source_name = doc['metadata'].get('source', '未知来源')
            context_parts.append(f"[文档{i}] 来源: {source_name}\n内容: {doc['content']}")

        return "\n\n---\n\n".join(context_parts)

    def generate_response(
        self,
        query: str,
        context: str,
        search_results: Optional[List[Dict]] = None,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        """
        生成响应

        Args:
            query: 用户查询
            context: 知识库上下文
            search_results: 网络搜索结果
            chat_history: 聊天历史

        Returns:
            生成的响应
        """
        # 构建系统提示词
        system_prompt = """你是一个智能助手，帮助用户回答问题。请根据提供的上下文和搜索结果来回答问题。

回答要求：
1. 如果上下文中有相关信息，优先使用上下文中的信息
2. 如果上下文中没有相关信息，可以结合搜索结果来回答
3. 如果上下文和搜索结果都没有相关信息，请诚实地告诉用户你无法从提供的信息中找到答案
4. 回答要清晰、准确、有条理
5. 引用来源时，请注明信息来源
6. 不要编造信息

上下文信息：
{context}"""

        if search_results:
            system_prompt += "\n\n网络搜索结果：\n{search_results}"

        # 构建消息列表
        messages = [SystemMessage(content=system_prompt.format(
            context=context if context else "无上下文信息",
            search_results=self._format_search_results(search_results) if search_results else "无搜索结果"
        ))]

        # 添加聊天历史
        if chat_history:
            for msg in chat_history[-6:]:  # 只保留最近3轮对话
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(SystemMessage(content=msg['content']))

        # 添加当前查询
        messages.append(HumanMessage(content=query))

        # 生成响应
        response = self.llm.invoke(messages)
        return response.content

    def _format_search_results(self, search_results: List[Dict]) -> str:
        """格式化搜索结果"""
        if not search_results:
            return "无搜索结果"

        formatted = []
        for i, result in enumerate(search_results, 1):
            formatted.append(f"[搜索结果{i}] 标题: {result.get('title', '未知')}\n链接: {result.get('url', '')}\n摘要: {result.get('snippet', '')}")

        return "\n\n---\n\n".join(formatted)


# 全局RAG服务实例
rag_service = RAGService()
