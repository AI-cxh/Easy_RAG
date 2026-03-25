"""写作Agent - 负责组织语言生成最终回答"""
from typing import Dict, Optional, Any, AsyncGenerator, List
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType
)
from app.services.tools import get_all_tools
from app.services.mcp_client import mcp_client


class WritingAgent(BaseAgent):
    """写作Agent - 负责组织语言生成最终回答，支持MCP工具"""

    SYSTEM_PROMPT = """你是一个专业的写作Agent。你的职责是：
1. 综合各Agent的分析结果
2. 组织语言，生成清晰、有条理的回答
3. 确保回答准确、完整、易读
4. 必要时使用可用工具获取额外信息

可用工具：
- 以及其他可用的MCP工具

写作要求：
- 回答要结构清晰，逻辑连贯
- 使用适当的标题和分段
- 引用来源要准确标注
- 语言要专业但不晦涩
- 适当使用列表、表格等格式
- 如果需要额外信息，可以使用工具获取

输出格式：
直接输出最终回答，不需要额外的说明。"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        初始化写作Agent

        Args:
            model_name: 使用的模型名称
            temperature: 温度参数（写作可以稍高）
        """
        # 获取内置工具
        builtin_tools = get_all_tools()

        # 获取MCP工具
        mcp_tools = mcp_client.get_tools()

        # 合并所有工具
        all_tools: List[BaseTool] = builtin_tools + mcp_tools

        super().__init__(
            name="writing_agent",
            description="写作Agent，负责组织语言生成最终回答",
            agent_type=AgentType.WRITING,
            system_prompt=self.SYSTEM_PROMPT,
            tools=all_tools,
            model_name=model_name or settings.MODEL_NAME,
            temperature=temperature
        )

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> AgentResult:
        """执行写作任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 构建写作提示
            writing_prompt = self._build_writing_prompt(task, context)

            # 构建消息
            messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
            messages.append(HumanMessage(content=writing_prompt))

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

                        intermediate_steps.append({
                            "step": tool_name,
                            "args": tool_args,
                            "result": tool_result
                        })

                        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))
                else:
                    # 没有工具调用，生成最终输出
                    output = response.content

                    # 收集来源和搜索结果
                    sources = context.get("sources", [])
                    search_results = context.get("search_results", [])

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
            output = response.content if response.content else "写作完成"
            sources = context.get("sources", [])
            search_results = context.get("search_results", [])

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

    async def stream_execute(
        self, task: AgentTask, context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式执行写作任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 构建写作提示
            writing_prompt = self._build_writing_prompt(task, context)

            # 发送开始事件
            yield {
                "type": "thought",
                "content": "开始组织回答..."
            }

            # 构建消息
            messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
            messages.append(HumanMessage(content=writing_prompt))

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
                        "content": "正在分析并决定是否使用工具..."
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
                    output = response.content

                    # 收集来源和搜索结果
                    sources = context.get("sources", [])
                    search_results = context.get("search_results", [])

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

            # 达到最大迭代次数
            output = response.content if response.content else "写作完成"
            sources = context.get("sources", [])
            search_results = context.get("search_results", [])

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
                "content": f"写作出错: {str(e)}\n{traceback.format_exc()}"
            }

    def _build_writing_prompt(self, task: AgentTask, context: Dict[str, Any]) -> str:
        """构建写作提示"""
        prompt = f"用户问题: {task.description}\n\n"

        # 添加原始问题
        original_query = context.get("original_query", task.description)
        if original_query != task.description:
            prompt = f"原始问题: {original_query}\n当前任务: {task.description}\n\n"

        # 添加前置结果
        for key, value in context.items():
            if key.startswith("prev_result_"):
                prompt += f"前置分析结果:\n{value}\n\n"

        prompt += "请根据以上信息，生成一个完整、清晰、有条理的回答。"
        return prompt
