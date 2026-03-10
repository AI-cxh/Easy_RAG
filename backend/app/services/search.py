"""网络搜索服务：提供网络搜索功能"""
from typing import List, Dict, Optional
from tavily import TavilyClient


class SearchService:
    """网络搜索服务类"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化搜索服务

        Args:
            api_key: Tavily API密钥
        """
        self.api_key = api_key
        self.tavily_client = None
        if api_key:
            self.tavily_client = TavilyClient(api_key=api_key)

    async def web_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        执行网络搜索

        Args:
            query: 搜索查询
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.tavily_client:
            return [{
                'title': '搜索服务未配置',
                'snippet': '请设置 SEARCH_API_KEY 环境变量以使用 Tavily 搜索服务',
                'url': '#'
            }]

        try:
            # 使用 Tavily API 进行搜索
            response = self.tavily_client.search(
                query=query,
                max_results=num_results,
                search_depth="basic",
                include_answer=False,
                include_raw_content=False,
                include_images=False
            )

            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('content', ''),
                    'url': result.get('url', '')
                })

            return results

        except Exception as e:
            # 如果搜索失败，返回错误信息
            return [{
                'title': '搜索服务错误',
                'snippet': f'搜索 "{query}" 时遇到错误: {str(e)}。请检查 API 密钥是否正确。',
                'url': '#'
            }]

    async def search_enhanced(
        self,
        query: str,
        num_results: int = 5,
        include_images: bool = False
    ) -> Dict:
        """
        增强搜索功能

        Args:
            query: 搜索查询
            num_results: 返回结果数量
            include_images: 是否包含图片结果

        Returns:
            包含搜索结果的字典
        """
        text_results = await self.web_search(query, num_results)

        return {
            'text_results': text_results,
            'results_count': len(text_results)
        }


# 全局搜索服务实例
async def get_search_service() -> SearchService:
    """获取搜索服务实例"""
    from app.config import settings
    return SearchService(api_key=settings.SEARCH_API_KEY)
