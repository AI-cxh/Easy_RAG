"""Agent工具定义：提供知识库检索、网络搜索等工具"""
from typing import List, Dict, Optional
from langchain_core.tools import tool

from app.services.embedding import embedding_service
from app.services.rerank import rerank_service
from app.services.search import SearchService


@tool
def knowledge_search(kb_ids: List[int], query: str, top_k: int = 4) -> str:
    """
    在指定知识库中搜索相关文档。

    当需要从知识库中检索信息时使用此工具。
    返回与查询最相关的文档内容。

    Args:
        kb_ids: 知识库ID列表，指定要搜索的知识库
        query: 搜索查询文本
        top_k: 返回结果数量，默认为4

    Returns:
        格式化的搜索结果字符串，包含文档内容和来源信息
    """
    if not kb_ids:
        return "错误：未指定知识库ID。请先选择要搜索的知识库。"

    try:
        # 检索更多文档用于重排序
        retrieve_k = 8 if rerank_service.is_enabled() else top_k
        similar_docs = embedding_service.search_similar(kb_ids, query, k=retrieve_k)

        if not similar_docs:
            return f"在知识库中未找到与 '{query}' 相关的内容。"

        # 重排序
        if rerank_service.is_enabled():
            similar_docs = rerank_service.rerank_sync(query, similar_docs, top_k=top_k)

        # 格式化结果
        results = []
        for i, doc in enumerate(similar_docs[:top_k], 1):
            source = doc['metadata'].get('source', '未知来源')
            rerank_info = f" (相关度: {doc.get('rerank_score', 0):.3f})" if 'rerank_score' in doc else ""
            results.append(f"[文档{i}] 来源: {source}{rerank_info}\n内容: {doc['content']}")

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"知识库搜索出错: {str(e)}"


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    在网络上搜索信息。

    当需要从互联网获取最新信息或知识库中没有相关信息时使用此工具。
    使用Tavily搜索引擎进行搜索。

    Args:
        query: 搜索查询文本
        num_results: 返回结果数量，默认为5

    Returns:
        格式化的搜索结果字符串，包含标题、链接和摘要
    """
    from app.config import settings

    try:
        search_service = SearchService(api_key=settings.SEARCH_API_KEY)

        # 使用同步方式调用（在工具中我们需要同步结果）
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # 如果在异步环境中，创建新线程执行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    search_service.web_search(query, num_results)
                )
                results = future.result()
        else:
            results = asyncio.run(search_service.web_search(query, num_results))

        if not results:
            return f"网络搜索未找到与 '{query}' 相关的结果。"

        # 格式化结果
        formatted = []
        for i, result in enumerate(results, 1):
            title = result.get('title', '未知')
            url = result.get('url', '')
            snippet = result.get('snippet', '')
            formatted.append(f"[搜索结果{i}] 标题: {title}\n链接: {url}\n摘要: {snippet}")

        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        return f"网络搜索出错: {str(e)}"


@tool
def list_knowledge_bases() -> str:
    """
    列出所有可用的知识库。

    当需要了解有哪些知识库可供搜索时使用此工具。
    返回知识库ID和名称列表，帮助选择合适的知识库进行检索。

    Returns:
        格式化的知识库列表字符串
    """
    from app.models.database import SessionLocal
    from app.models.models import KnowledgeBase

    try:
        db = SessionLocal()
        try:
            knowledge_bases = db.query(KnowledgeBase).all()

            if not knowledge_bases:
                return "当前没有可用的知识库。请先创建知识库并上传文档。"

            results = ["可用知识库列表："]
            for kb in knowledge_bases:
                doc_count = len(kb.documents) if hasattr(kb, 'documents') else 0
                results.append(f"- ID: {kb.id}, 名称: {kb.name}, 文档数: {doc_count}")

            return "\n".join(results)

        finally:
            db.close()

    except Exception as e:
        return f"获取知识库列表出错: {str(e)}"


@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取当前时间。

    当用户询问当前时间、日期或需要知道现在是什么时候时使用此工具。

    Args:
        timezone: 时区名称，默认为 Asia/Shanghai（中国标准时间）
                  常用时区：Asia/Shanghai, UTC, America/New_York, Europe/London

    Returns:
        当前时间的格式化字符串，包含日期、时间和星期
    """
    from datetime import datetime
    try:
        import pytz
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
    except ImportError:
        # 如果没有安装 pytz，使用本地时间
        now = datetime.now()
    except Exception:
        # 时区无效时使用本地时间
        now = datetime.now()

    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[now.weekday()]

    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')} {weekday} (时区: {timezone})"


@tool
def get_document_details(doc_id: int) -> str:
    """
    获取指定文档的详细信息。

    当需要查看特定文档的内容或元数据时使用此工具。

    Args:
        doc_id: 文档ID

    Returns:
        文档的详细信息，包括文件名、大小、块数量等
    """
    from app.models.database import SessionLocal
    from app.models.models import Document

    try:
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()

            if not doc:
                return f"未找到ID为 {doc_id} 的文档。"

            info = [
                f"文档ID: {doc.id}",
                f"文件名: {doc.filename}",
                f"知识库ID: {doc.kb_id}",
                f"文件大小: {doc.file_size or 0} 字节",
                f"分块数量: {doc.chunk_count}",
                f"创建时间: {doc.created_at}"
            ]

            return "\n".join(info)

        finally:
            db.close()

    except Exception as e:
        return f"获取文档详情出错: {str(e)}"


def get_all_tools():
    """获取所有可用的Agent工具"""
    return [
        knowledge_search,
        web_search,
        list_knowledge_bases,
        get_document_details,
        get_current_time
    ]
