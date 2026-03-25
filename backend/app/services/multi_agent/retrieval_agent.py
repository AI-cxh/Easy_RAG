"""检索Agent - 负责信息检索"""
from typing import List, Dict, Optional, Any, AsyncGenerator
import time
import re
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType
)
from app.services.tools import knowledge_search, web_search, list_knowledge_bases, get_all_tools
from app.services.mcp_client import mcp_client

logger = logging.getLogger(__name__)


class RetrievalAgent(BaseAgent):
    """检索Agent - 负责从知识库和网络搜索相关信息，支持MCP工具"""

    SYSTEM_PROMPT = """你是一个专业的信息检索Agent。你的职责是：
1. 根据用户问题，从知识库中检索相关文档
2. 必要时进行网络搜索获取最新信息
3. 使用可用的MCP工具执行特定任务
4. 整理和汇总检索到的信息
5. 返回结构化的检索结果

可用工具：
- list_knowledge_bases: 列出所有可用的知识库
- knowledge_search: 在指定知识库中搜索文档
- web_search: 在网络上搜索信息
- 以及其他可用的MCP工具

工作流程：
1. 首先分析用户问题，判断需要使用什么工具
2. 选择相关的知识库进行检索或使用MCP工具
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
        # 获取内置工具
        builtin_tools = get_all_tools()

        # 获取MCP工具
        mcp_tools = mcp_client.get_tools()

        # 合并所有工具
        all_tools: List[BaseTool] = builtin_tools + mcp_tools

        super().__init__(
            name="retrieval_agent",
            description="检索Agent，负责从知识库和网络搜索相关信息",
            agent_type=AgentType.RETRIEVAL,
            system_prompt=self.SYSTEM_PROMPT,
            tools=all_tools,
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

        logger.info(f"RetrievalAgent initialized with {len(builtin_tools)} built-in tools and {len(mcp_tools)} MCP tools")

    def _build_system_prompt_with_context(self, kb_ids: List[int], use_web_search: bool) -> str:
        """构建带有上下文的系统提示词"""
        prompt = self.SYSTEM_PROMPT

        # 添加知识库信息
        if kb_ids:
            prompt += f"\n\n当前可用的知识库ID: {kb_ids}\n你可以使用这些ID进行知识库检索。"

        if not use_web_search:
            prompt += "\n\n注意：网络搜索当前未启用。"

        if not kb_ids and not use_web_search:
            prompt += "\n\n警告：没有可用的知识库，网络搜索也未启用。请尝试使用其他可用工具或直接回答。"

        return prompt

    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> AgentResult:
        """执行检索任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            kb_ids = context.get("kb_ids", self.kb_ids)
            use_web_search = context.get("use_web_search", self.use_web_search)
            query = task.description

            # 构建消息
            system_prompt = self._build_system_prompt_with_context(kb_ids, use_web_search)
            messages = [SystemMessage(content=system_prompt)]
            messages.append(HumanMessage(content=query))

            # 绑定工具到LLM
            llm_with_tools = self.llm.bind_tools(self.tools)

            # 迭代执行
            iteration = 0
            max_iterations = 5

            while iteration < max_iterations:
                iteration += 1
                response = await llm_with_tools.ainvoke(messages)

                if response.tool_calls:
                    messages.append(response)

                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        # 执行工具
                        tool_result = await self._execute_tool(tool_name, tool_args)

                        # 收集搜索结果
                        if tool_name == "knowledge_search":
                            intermediate_steps.append({
                                "step": "knowledge_search",
                                "query": tool_args.get("query", ""),
                                "kb_ids": tool_args.get("kb_ids", []),
                                "result": tool_result
                            })
                            # 解析来源
                            pattern = r'\[文档\d+\] 来源: ([^\n(]+)'
                            for source in re.findall(pattern, tool_result):
                                source = source.strip()
                                if source and source not in sources:
                                    sources.append(source)

                        elif tool_name == "web_search":
                            intermediate_steps.append({
                                "step": "web_search",
                                "query": tool_args.get("query", ""),
                                "result": tool_result
                            })
                            # 解析网络搜索结果
                            pattern = r'\[搜索结果\d+\] 标题: (.*?)\n链接: (.*?)\n摘要: (.*?)(?=\n\n---|\Z)'
                            for title, url, snippet in re.findall(pattern, tool_result, re.DOTALL):
                                search_results.append({
                                    "title": title.strip(),
                                    "url": url.strip(),
                                    "snippet": snippet.strip()
                                })
                        else:
                            # MCP工具或其他工具
                            intermediate_steps.append({
                                "step": tool_name,
                                "args": tool_args,
                                "result": tool_result
                            })

                        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
                else:
                    # 没有工具调用，生成最终输出
                    output = response.content or self._format_output(intermediate_steps)

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

            # 达到最大迭代次数
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
            logger.error(f"RetrievalAgent execute error: {e}", exc_info=True)
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
        """流式执行检索任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            kb_ids = context.get("kb_ids", self.kb_ids)
            use_web_search = context.get("use_web_search", self.use_web_search)
            query = task.description

            # 发送开始事件
            yield {
                "type": "thought",
                "content": f"开始检索任务: {query}"
            }

            # 构建消息
            system_prompt = self._build_system_prompt_with_context(kb_ids, use_web_search)
            messages = [SystemMessage(content=system_prompt)]
            messages.append(HumanMessage(content=query))

            # 绑定工具到LLM
            llm_with_tools = self.llm.bind_tools(self.tools)

            # 迭代执行
            iteration = 0
            max_iterations = 5

            while iteration < max_iterations:
                iteration += 1
                response = await llm_with_tools.ainvoke(messages)

                if response.tool_calls:
                    # 发送思考事件
                    yield {
                        "type": "thought",
                        "content": "正在分析并决定使用工具..."
                    }

                    messages.append(response)

                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        # 发送工具调用事件
                        yield {
                            "type": "tool_call",
                            "tool_name": tool_name,
                            "content": f"调用工具: {tool_name}"
                        }

                        # 执行工具
                        tool_result = await self._execute_tool(tool_name, tool_args)

                        # 收集搜索结果
                        if tool_name == "knowledge_search":
                            intermediate_steps.append({
                                "step": "knowledge_search",
                                "query": tool_args.get("query", ""),
                                "kb_ids": tool_args.get("kb_ids", []),
                                "result": tool_result
                            })
                            pattern = r'\[文档\d+\] 来源: ([^\n(]+)'
                            for source in re.findall(pattern, tool_result):
                                source = source.strip()
                                if source and source not in sources:
                                    sources.append(source)

                        elif tool_name == "web_search":
                            intermediate_steps.append({
                                "step": "web_search",
                                "query": tool_args.get("query", ""),
                                "result": tool_result
                            })
                            pattern = r'\[搜索结果\d+\] 标题: (.*?)\n链接: (.*?)\n摘要: (.*?)(?=\n\n---|\Z)'
                            for title, url, snippet in re.findall(pattern, tool_result, re.DOTALL):
                                search_results.append({
                                    "title": title.strip(),
                                    "url": url.strip(),
                                    "snippet": snippet.strip()
                                })
                        else:
                            intermediate_steps.append({
                                "step": tool_name,
                                "args": tool_args,
                                "result": tool_result
                            })

                        # 发送工具结果事件
                        yield {
                            "type": "tool_result",
                            "tool_name": tool_name,
                            "content": tool_result[:500] + "..." if len(tool_result) > 500 else tool_result
                        }

                        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
                else:
                    # 没有工具调用，生成最终输出
                    output = response.content or self._format_output(intermediate_steps)

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
                    return

            # 达到最大迭代次数，生成输出
            output = self._format_output(intermediate_steps)
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
            logger.error(f"RetrievalAgent stream_execute error: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"检索出错: {str(e)}\n{traceback.format_exc()}"
            }

    async def _execute_tool(self, tool_name: str, tool_args: Dict) -> str:
        """执行工具调用"""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    if hasattr(tool, 'ainvoke'):
                        result = await tool.ainvoke(tool_args)
                    else:
                        result = tool.invoke(tool_args)
                    return str(result)
                except Exception as e:
                    return f"工具执行出错: {str(e)}"
        return f"未找到工具: {tool_name}"

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
            else:
                # 其他工具结果
                output_parts.append(f"\n### {step['step']} 结果\n")
                if isinstance(step.get("result"), str):
                    output_parts.append(step["result"][:500])
                else:
                    output_parts.append(str(step.get("result", ""))[:500])

        return "\n".join(output_parts) if output_parts else "未找到相关信息"
