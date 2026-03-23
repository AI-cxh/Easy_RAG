"""Agent服务：负责智能体驱动的RAG流程"""
from typing import List, Dict, Optional, AsyncGenerator, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel
import json
import logging

from app.config import settings
from app.services.tools import get_all_tools
from app.services.mcp_client import mcp_client

logger = logging.getLogger(__name__)


class AgentService:
    """Agent服务类 - 管理智能体的执行循环"""

    def __init__(self):
        """初始化Agent服务"""
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        self._builtin_tools = get_all_tools()
        self.tools: List[BaseTool] = self._builtin_tools.copy()
        self._initialized = False

    async def initialize(self) -> None:
        """异步初始化，加载MCP工具"""
        # 加载MCP工具
        mcp_tools = mcp_client.get_tools()

        # 转换MCP工具为有效的StructuredTool
        valid_mcp_tools = []
        for tool in mcp_tools:
            try:
                # 检查工具schema是否需要修复
                if hasattr(tool, 'args_schema') and isinstance(tool.args_schema, dict):
                    schema = tool.args_schema
                    # 如果type不是object，需要修复
                    if schema.get('type') != 'object':
                        # 创建一个空的Pydantic模型作为args_schema
                        class EmptyArgs(BaseModel):
                            pass

                        # 创建一个新的StructuredTool包装
                        async def make_wrapper(original_tool):
                            async def wrapper(*args, **kwargs):
                                if hasattr(original_tool, 'ainvoke'):
                                    return await original_tool.ainvoke(*args, **kwargs)
                                return original_tool.invoke(*args, **kwargs)
                            return wrapper

                        wrapped_tool = StructuredTool(
                            name=tool.name,
                            description=getattr(tool, 'description', '') or f"MCP tool: {tool.name}",
                            func=lambda **kwargs: None,  # 占位符
                            coroutine=make_wrapper(tool),
                            args_schema=EmptyArgs
                        )
                        valid_mcp_tools.append(wrapped_tool)
                        logger.info(f"Wrapped MCP tool '{tool.name}' with fixed schema")
                    else:
                        valid_mcp_tools.append(tool)
                else:
                    # 没有args_schema或已经是正确类型，直接使用
                    valid_mcp_tools.append(tool)
            except Exception as e:
                logger.warning(f"Error processing MCP tool '{tool.name}': {e}")
                # 尝试直接添加
                valid_mcp_tools.append(tool)

        self.tools = self._builtin_tools + valid_mcp_tools
        self._initialized = True

        logger.info(f"Agent initialized with {len(self._builtin_tools)} built-in tools and {len(valid_mcp_tools)} MCP tools")

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具（内置+MCP）"""
        return self.tools

    def _build_system_prompt(self, has_kb: bool = True, use_web_search: bool = True) -> str:
        """
        构建Agent系统提示词

        Args:
            has_kb: 是否有知识库可用
            use_web_search: 是否启用网络搜索

        Returns:
            系统提示词字符串
        """
        base_prompt = """你是一个智能助手，能够自主决定如何回答用户的问题。

你的能力：
1. 分析用户问题的意图和需求
2. 自主决定是否需要检索知识库
3. 自主选择检索哪些知识库
4. 进行网络搜索获取最新信息
5. 使用可用的MCP工具执行特定任务
6. 综合多方面信息给出准确回答

工作流程：
1. 首先分析用户问题，判断需要使用什么工具
2. 如果问题简单或属于常识，可以直接回答
3. 如果需要专业知识或特定信息，优先使用合适的工具
4. 分析检索结果，判断是否需要更多信息
5. 综合所有信息，生成最终回答

回答要求：
- 回答要清晰、准确、有条理
- 引用来源时，请注明信息来源
- 不要编造信息
- 如果无法找到答案，请诚实告知"""

        tool_instructions = []

        if has_kb:
            tool_instructions.append("""
知识库检索指南：
- 使用 list_knowledge_bases 查看可用的知识库
- 使用 knowledge_search 在指定知识库中搜索相关文档
- 可以多次调用 knowledge_search 检索不同知识库
- 适用于查询知识库中存储的专业文档和信息""")

        if use_web_search:
            tool_instructions.append("""
网络搜索指南：
- 使用 web_search 在网络上搜索最新信息
- 适合查询实时信息、新闻、技术文档等
- 当知识库中没有相关信息时使用""")

        # 添加MCP工具说明
        mcp_tools_info = []
        try:
            for tool in self.tools[len(self._builtin_tools):]:  # 只获取MCP工具
                tool_desc = getattr(tool, 'description', '') or f"工具: {tool.name}"
                if tool_desc:
                    tool_desc = str(tool_desc)[:100]
                else:
                    tool_desc = f"工具: {tool.name}"
                mcp_tools_info.append(f"- {tool.name}: {tool_desc}")
        except Exception as e:
            # 如果获取MCP工具信息失败，记录但不中断
            import logging
            logging.warning(f"Failed to get MCP tool info: {e}")

        if mcp_tools_info:
            tool_instructions.append(f"""
MCP工具（可用）：
{chr(10).join(mcp_tools_info)}
根据问题需要，可以使用上述MCP工具来执行特定任务""")

        if tool_instructions:
            base_prompt += "\n\n" + "\n".join(tool_instructions)

        return base_prompt

    async def run(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None,
        kb_ids: Optional[List[int]] = None,
        use_web_search: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        执行Agent循环，流式返回结果

        Args:
            query: 用户查询
            chat_history: 聊天历史
            kb_ids: 可用的知识库ID列表（可选）
            use_web_search: 是否启用网络搜索

        Yields:
            包含事件类型和内容的字典
        """
        # 构建系统提示词
        has_kb = bool(kb_ids)
        system_prompt = self._build_system_prompt(has_kb, use_web_search)

        # 构建消息列表
        messages = [SystemMessage(content=system_prompt)]

        # 添加知识库信息
        if kb_ids:
            kb_info = f"\n当前可用的知识库ID: {kb_ids}\n你可以使用这些ID进行知识库检索。"
            messages.append(SystemMessage(content=kb_info))

        # 添加聊天历史
        if chat_history:
            for msg in chat_history[-6:]:  # 只保留最近3轮对话
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))

        # 添加当前查询
        messages.append(HumanMessage(content=query))

        # 绑定工具到LLM
        llm_with_tools = self.llm.bind_tools(self.tools)

        # 收集搜索结果
        collected_search_results = []
        collected_sources = []

        # 迭代执行
        iteration = 0
        max_iterations = settings.AGENT_MAX_ITERATIONS

        while iteration < max_iterations:
            iteration += 1

            try:
                # 调用LLM
                response = await llm_with_tools.ainvoke(messages)

                # 检查是否有工具调用
                if response.tool_calls:
                    # 发送思考过程
                    yield {
                        "type": "thought",
                        "content": f"正在分析问题并决定使用工具..."
                    }

                    # 添加AI消息到历史
                    messages.append(response)

                    # 执行每个工具调用
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        # 发送工具调用事件
                        yield {
                            "type": "tool_call",
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "content": f"调用工具: {tool_name}"
                        }

                        # 执行工具
                        tool_result, search_data = await self._execute_tool_with_data(tool_name, tool_args)

                        # 收集搜索结果
                        if search_data:
                            if search_data.get("type") == "web_search":
                                collected_search_results.extend(search_data.get("results", []))
                            elif search_data.get("type") == "knowledge_search":
                                collected_sources.extend(search_data.get("sources", []))

                        # 发送工具结果事件
                        yield {
                            "type": "tool_result",
                            "tool_name": tool_name,
                            "content": tool_result[:500] + "..." if len(tool_result) > 500 else tool_result
                        }

                        # 添加工具结果到消息历史
                        messages.append(ToolMessage(
                            content=tool_result,
                            tool_call_id=tool_call["id"]
                        ))

                else:
                    # 没有工具调用，生成最终回答
                    # 流式输出最终回答
                    async for chunk in self.llm.astream(messages):
                        if chunk.content:
                            yield {
                                "type": "answer",
                                "content": chunk.content
                            }

                    # 发送收集到的搜索结果
                    if collected_search_results or collected_sources:
                        yield {
                            "type": "search_data",
                            "search_results": collected_search_results if collected_search_results else None,
                            "sources": list(set(collected_sources)) if collected_sources else None
                        }
                    return

            except Exception as e:
                import logging
                logging.error(f"Agent execution error: {e}", exc_info=True)
                yield {
                    "type": "error",
                    "content": f"Agent执行出错: {str(e)}"
                }
                return

        # 达到最大迭代次数
        yield {
            "type": "error",
            "content": "达到最大迭代次数，请简化问题或稍后重试。"
        }

    async def _execute_tool_with_data(self, tool_name: str, tool_args: Dict) -> Tuple[str, Optional[Dict]]:
        """
        执行工具调用并返回结果和额外数据

        Args:
            tool_name: 工具名称
            tool_args: 工具参数

        Returns:
            (工具执行结果字符串, 额外数据字典)
        """
        # 查找对应的工具
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    # 执行工具 - 优先使用异步调用
                    if hasattr(tool, 'ainvoke'):
                        result = await tool.ainvoke(tool_args)
                    else:
                        result = tool.invoke(tool_args)

                    # 解析搜索结果
                    search_data = None
                    if tool_name == "web_search":
                        search_data = self._parse_web_search_result(str(result))
                    elif tool_name == "knowledge_search":
                        search_data = self._parse_knowledge_search_result(str(result))

                    return str(result), search_data
                except Exception as e:
                    return f"工具执行出错: {str(e)}", None

        return f"未找到工具: {tool_name}", None

    def _parse_web_search_result(self, result: str) -> Dict:
        """解析网络搜索结果，提取结构化数据"""
        search_results = []
        # 解析格式: [搜索结果1] 标题: xxx\n链接: xxx\n摘要: xxx
        import re
        pattern = r'\[搜索结果\d+\] 标题: (.*?)\n链接: (.*?)\n摘要: (.*?)(?=\n\n---|\Z)'
        matches = re.findall(pattern, result, re.DOTALL)

        for title, url, snippet in matches:
            search_results.append({
                "title": title.strip(),
                "url": url.strip(),
                "snippet": snippet.strip()
            })

        return {"type": "web_search", "results": search_results}

    def _parse_knowledge_search_result(self, result: str) -> Dict:
        """解析知识库搜索结果，提取来源"""
        sources = []
        # 解析格式: [文档1] 来源: xxx
        import re
        pattern = r'\[文档\d+\] 来源: ([^\n(]+)'
        matches = re.findall(pattern, result)

        for source in matches:
            source = source.strip()
            if source and source not in sources:
                sources.append(source)

        return {"type": "knowledge_search", "sources": sources}

    async def run_simple(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        """
        简单模式运行 - 只流式输出最终回答

        Args:
            query: 用户查询
            chat_history: 聊天历史

        Yields:
            生成的响应文本块
        """
        # 构建消息列表
        messages = [SystemMessage(content=self._build_system_prompt(False, False))]

        # 添加聊天历史
        if chat_history:
            for msg in chat_history[-6:]:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))

        # 添加当前查询
        messages.append(HumanMessage(content=query))

        # 流式生成响应
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content


# 全局Agent服务实例
agent_service = AgentService()
