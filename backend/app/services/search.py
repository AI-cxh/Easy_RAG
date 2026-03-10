"""网络搜索服务：提供网络搜索功能"""
from typing import List, Dict, Optional
import httpx
from urllib.parse import quote_plus


class SearchService:
    """网络搜索服务类"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化搜索服务

        Args:
            api_key: 可选的搜索API密钥
        """
        self.api_key = api_key
        self.timeout = 10

    async def web_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        执行网络搜索

        Args:
            query: 搜索查询
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        # 目前使用DuckDuckGo API（无需API密钥）
        results = await self._duckduckgo_search(query, num_results)

        return results

    async def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict]:
        """
        使用DuckDuckGo进行搜索

        Args:
            query: 搜索查询
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                results = []
                if 'RelatedTopics' in data:
                    for topic in data['RelatedTopics'][:num_results]:
                        if 'Text' in topic and 'FirstURL' in topic:
                            results.append({
                                'title': topic.get('Text', '').split(' - ')[0][:100],
                                'snippet': topic.get('Text', ''),
                                'url': topic['FirstURL']
                            })
                        elif isinstance(topic, dict) and 'Topics' in topic:
                            for subtopic in topic['Topics'][:int(num_results/2)]:
                                if 'Text' in subtopic and 'FirstURL' in subtopic:
                                    results.append({
                                        'title': subtopic.get('Text', '').split(' - ')[0][:100],
                                        'snippet': subtopic.get('Text', ''),
                                        'url': subtopic['FirstURL']
                                    })

                return results[:num_results]

        except Exception as e:
            # 如果DuckDuckGo失败，返回模拟结果
            return [{
                'title': '搜索服务暂时不可用',
                'snippet': f'搜索 "{query}" 时遇到错误: {str(e)}。这可能是网络连接问题或搜索服务限制。',
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
