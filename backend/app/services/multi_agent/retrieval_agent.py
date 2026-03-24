"""检索Agent - 负责信息检索"""
from typing import List, Dict, Optional, Any, AsyncGenerator
import time
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType
)
from app.services.tools import knowledge_search, web_search, list_knowledge_bases


class RetrievalAgent(BaseAgent):
    """检索Agent - 负责从知识库和网络搜索相关信息"""

    SYSTEM_PROMPT = """你是一个专业的信息检索Agent。你的职责是：
1. 根据用户问题，从知识库中检索相关文档
2. 必要时进行网络搜索获取最新信息
3. 整理和汇总检索到的信息
4. 返回结构化的检索结果

可用工具：
- list_knowledge_bases: 列出所有可用的知识库
- knowledge_search: 在指定知识库中搜索文档
- web_search: 在网络上搜索信息

工作流程：
1. 首先查看可用的知识库
2. 选择相关的知识库进行检索
3. 如果知识库信息不足，进行网络搜索
4. 整理并返回检索结果

注意：
- 返回的检索结果要清晰、有条理
- 标注信息来源
- 如果没有找到相关信息，明确说明"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        kb_ids: Optional[List[int]] = None,
        use_web_search: bool = True
    ):
        """
        初始化检索Agent

        Args:
            model_name: 使用的模型名称
            temperature: 温度参数
            kb_ids: 默认的知识库ID列表
            use_web_search: 是否启用网络搜索
        """
        tools: List[BaseTool] = [knowledge_search, web_search, list_knowledge_bases]

        super().__init__(
            name="retrieval_agent",
            description="检索Agent，负责从知识库和网络搜索相关信息",
            agent_type=AgentType.RETRIEVAL,
            system_prompt=self.SYSTEM_PROMPT,
            tools=tools,
            model_name=model_name or settings.MODEL_NAME,
            temperature=temperature
        )

        self.kb_ids = kb_ids
        self.use_web_search = use_web_search
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> AgentResult:
        """执行检索任务"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 获取知识库ID
            kb_ids = context.get("kb_ids", self.kb_ids)
            use_web_search = context.get("use_web_search", self.use_web_search)

            # 构建检索查询
            query = task.description

            # 执行知识库检索
            if kb_ids:
                kb_result = knowledge_search.invoke({
                    "kb_ids": kb_ids,
                    "query": query,
                    "top_k": 5
                })
                intermediate_steps.append({
                    "step": "knowledge_search",
                    "query": query,
                    "kb_ids": kb_ids,
                    "result": kb_result[:500] + "..." if len(kb_result) > 500 else kb_result
                })

                # 解析来源
                pattern = r'\[文档\d+\] 来源: ([^\n(]+)'
                matches = re.findall(pattern, kb_result)
                for source in matches:
                    source = source.strip()
                    if source and source not in sources:
                        sources.append(source)

            # 执行网络搜索
            if use_web_search:
                web_result = web_search.invoke({
                    "query": query,
                    "num_results": 5
                })
                intermediate_steps.append({
                    "step": "web_search",
                    "query": query,
                    "result": web_result[:500] + "..." if len(web_result) > 500 else web_result
                })

                # 解析网络搜索结果
                pattern = r'\[搜索结果\d+\] 标题: (.*?)\n链接: (.*?)\n摘要: (.*?)(?=\n\n---|\Z)'
                matches = re.findall(pattern, web_result, re.DOTALL)
                for title, url, snippet in matches:
                    search_results.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "snippet": snippet.strip()
                    })

            # 整理输出
            output = self._format_output(intermediate_steps)

            return AgentResult(
                task_id=task.id,
                agent_name=self.name,
                agent_type=self.agent_type,
                success=True,
                output=output,
                intermediate_steps=intermediate_steps,
                sources=sources,
                search_results=search_results,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_name=self.name,
                agent_type=self.agent_type,
                success=False,
                output="",
                error=str(e),
                execution_time=time.time() - start_time
            )

    async def stream_execute(
        self, task: AgentTask, context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式执行检索任务"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 获取知识库ID
            kb_ids = context.get("kb_ids", self.kb_ids)
            use_web_search = context.get("use_web_search", self.use_web_search)
            query = task.description

            # 发送开始事件
            yield {
                "type": "thought",
                "content": f"开始检索任务: {query}"
            }

            # 如果没有任何信息源，给出提示
            if not kb_ids and not use_web_search:
                yield {
                    "type": "thought",
                    "content": "未指定知识库且未启用网络搜索，将尝试提供通用回答"
                }

            # 执行知识库检索
            if kb_ids:
                yield {
                    "type": "tool_call",
                    "tool_name": "knowledge_search",
                    "content": f"正在知识库 {kb_ids} 中搜索..."
                }

                kb_result = knowledge_search.invoke({
                    "kb_ids": kb_ids,
                    "query": query,
                    "top_k": 5
                })

                intermediate_steps.append({
                    "step": "knowledge_search",
                    "query": query,
                    "kb_ids": kb_ids,
                    "result": kb_result
                })

                # 解析来源
                pattern = r'\[文档\d+\] 来源: ([^\n(]+)'
                matches = re.findall(pattern, kb_result)
                for source in matches:
                    source = source.strip()
                    if source and source not in sources:
                        sources.append(source)

                yield {
                    "type": "tool_result",
                    "tool_name": "knowledge_search",
                    "content": kb_result[:500] + "..." if len(kb_result) > 500 else kb_result
                }

            # 执行网络搜索
            if use_web_search:
                yield {
                    "type": "tool_call",
                    "tool_name": "web_search",
                    "content": "正在网络搜索..."
                }

                web_result = web_search.invoke({
                    "query": query,
                    "num_results": 5
                })

                intermediate_steps.append({
                    "step": "web_search",
                    "query": query,
                    "result": web_result
                })

                # 解析网络搜索结果
                pattern = r'\[搜索结果\d+\] 标题: (.*?)\n链接: (.*?)\n摘要: (.*?)(?=\n\n---|\Z)'
                matches = re.findall(pattern, web_result, re.DOTALL)
                for title, url, snippet in matches:
                    search_results.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "snippet": snippet.strip()
                    })

                yield {
                    "type": "tool_result",
                    "tool_name": "web_search",
                    "content": web_result[:500] + "..." if len(web_result) > 500 else web_result
                }

            # 整理输出
            output = self._format_output(intermediate_steps)

            # 发送结果
            yield {
                "type": "result",
                "result": {
                    "task_id": task.id,
                    "agent_name": self.name,
                    "agent_type": self.agent_type.value,
                    "success": True,
                    "output": output,
                    "intermediate_steps": intermediate_steps,
                    "sources": sources,
                    "search_results": search_results,
                    "execution_time": time.time() - start_time
                }
            }

        except Exception as e:
            import traceback
            yield {
                "type": "error",
                "content": f"检索出错: {str(e)}\n{traceback.format_exc()}"
            }

    def _format_output(self, steps: List[Dict]) -> str:
        """格式化输出"""
        output_parts = []

        for step in steps:
            if step["step"] == "knowledge_search":
                output_parts.append("### 知识库检索结果\n")
                output_parts.append(step["result"])
            elif step["step"] == "web_search":
                output_parts.append("\n### 网络搜索结果\n")
                output_parts.append(step["result"])

        return "\n".join(output_parts) if output_parts else "未找到相关信息"
