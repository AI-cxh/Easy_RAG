"""自定义Agent - 用户可配置的通用Agent"""
from typing import List, Dict, Optional, Any, AsyncGenerator
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


class CustomAgent(BaseAgent):
    """自定义Agent - 用户可配置的通用Agent，支持MCP工具"""

    DEFAULT_SYSTEM_PROMPT = """你是一个专业的助手。请根据用户的问题和提供的上下文，给出准确、有帮助的回答。
你可以使用可用的工具来获取更多信息或执行特定任务。

回答要求：
- 准确理解用户的问题
- 充分利用提供的上下文信息
- 必要时使用工具获取额外信息
- 给出清晰、有条理的回答
- 如有不确定的地方，请明确说明"""

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        初始化自定义Agent

        Args:
            name: Agent名称
            description: Agent描述
            system_prompt: 系统提示词
            tools: 可用工具列表（如果为None，则加载所有可用工具）
            model_name: 使用的模型名称
            temperature: 温度参数
        """
        # 如果没有指定工具，加载所有可用工具
        if tools is None:
            builtin_tools = get_all_tools()
            mcp_tools = mcp_client.get_tools()
            tools = builtin_tools + mcp_tools

        super().__init__(
            name=name,
            description=description,
            agent_type=AgentType.CUSTOM,
            system_prompt=system_prompt or self.DEFAULT_SYSTEM_PROMPT,
            tools=tools,
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
        """执行任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 构建执行提示
            prompt = self._build_prompt(task, context)

            # 构建消息
            messages = [SystemMessage(content=self.system_prompt)]
            messages.append(HumanMessage(content=prompt))

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
            output = response.content if response.content else "执行完成"
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
        """流式执行任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 构建执行提示
            prompt = self._build_prompt(task, context)

            # 发送开始事件
            yield {
                "type": "thought",
                "content": f"开始执行任务: {task.description}"
            }

            # 构建消息
            messages = [SystemMessage(content=self.system_prompt)]
            messages.append(HumanMessage(content=prompt))

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
            output = response.content if response.content else "执行完成"
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
                "content": f"执行出错: {str(e)}\n{traceback.format_exc()}"
            }

    def _build_prompt(self, task: AgentTask, context: Dict[str, Any]) -> str:
        """构建执行提示"""
        prompt = f"任务: {task.description}\n\n"

        # 添加上下文
        if context:
            context_parts = []
            for key, value in context.items():
                if key.startswith("prev_result_"):
                    context_parts.append(f"前置结果:\n{value}")

            if context_parts:
                prompt += "\n\n".join(context_parts) + "\n\n"

        prompt += "请完成任务。"
        return prompt

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "CustomAgent":
        """
        从配置字典创建Agent

        Args:
            config: 配置字典

        Returns:
            CustomAgent实例
        """
        return cls(
            name=config.get("name", "custom_agent"),
            description=config.get("description", "自定义Agent"),
            system_prompt=config.get("system_prompt"),
            model_name=config.get("model_name"),
            temperature=config.get("temperature", 0.7)
        )
