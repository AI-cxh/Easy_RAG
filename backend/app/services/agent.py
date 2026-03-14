"""Agent服务：负责智能体驱动的RAG流程"""
from typing import List, Dict, Optional, AsyncGenerator, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool

from app.config import settings
from app.services.tools import get_all_tools
from app.services.mcp_client import mcp_client


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
        if self._initialized:
            return

        # 加载MCP工具
        mcp_tools = mcp_client.get_tools()
        self.tools = self._builtin_tools + mcp_tools
        self._initialized = True

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
5. 综合多方面信息给出准确回答

工作流程：
1. 首先分析用户问题，判断是否需要检索外部信息
2. 如果问题简单或属于常识，可以直接回答
3. 如果需要专业知识或特定信息，使用工具进行检索
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
- 可以多次调用 knowledge_search 检索不同知识库""")

        if use_web_search:
            tool_instructions.append("""
网络搜索指南：
- 使用 web_search 在网络上搜索最新信息
- 适合查询实时信息、新闻、技术文档等""")

        if tool_instructions:
            base_prompt += "\n" + "\n".join(tool_instructions)

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
                        tool_result = await self._execute_tool(tool_name, tool_args)

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
                    return

            except Exception as e:
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

    async def _execute_tool(self, tool_name: str, tool_args: Dict) -> str:
        """
        执行工具调用

        Args:
            tool_name: 工具名称
            tool_args: 工具参数

        Returns:
            工具执行结果字符串
        """
        # 查找对应的工具
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    # 执行工具
                    result = tool.invoke(tool_args)
                    return str(result)
                except Exception as e:
                    return f"工具执行出错: {str(e)}"

        return f"未找到工具: {tool_name}"

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
