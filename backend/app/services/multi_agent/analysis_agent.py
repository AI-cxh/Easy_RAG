"""分析Agent - 负责深度分析和推理"""
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


class AnalysisAgent(BaseAgent):
    """分析Agent - 负责深度分析和推理，支持MCP工具"""

    SYSTEM_PROMPT = """你是一个专业的分析Agent。你的职责是：
1. 对检索到的信息进行深度分析
2. 识别关键信息和潜在关联
3. 进行逻辑推理和归纳
4. 使用可用的工具进行额外查询或计算
5. 得出分析结论

可用工具：
- 以及其他可用的MCP工具

分析要求：
- 客观、全面地分析信息
- 识别信息之间的关联和矛盾
- 进行逻辑推理，得出合理结论
- 指出信息的可靠性和局限性
- 必要时使用工具获取更多信息

输出格式：
1. 信息分析：对输入信息的分析
2. 关键发现：识别的关键点
3. 推理过程：逻辑推理步骤
4. 分析结论：最终结论"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        初始化分析Agent

        Args:
            model_name: 使用的模型名称
            temperature: 温度参数
        """
        # 获取内置工具
        builtin_tools = get_all_tools()

        # 获取MCP工具
        mcp_tools = mcp_client.get_tools()

        # 合并所有工具
        all_tools: List[BaseTool] = builtin_tools + mcp_tools

        super().__init__(
            name="analysis_agent",
            description="分析Agent，负责深度分析和推理",
            agent_type=AgentType.ANALYSIS,
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
        """执行分析任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []

        try:
            # 构建分析提示
            analysis_prompt = self._build_analysis_prompt(task, context)

            # 构建消息
            messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
            messages.append(HumanMessage(content=analysis_prompt))

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

                    return AgentResult(
                        task_id=task.id,
                        agent_name=self.name,
                        agent_type=self.agent_type,
                        success=True,
                        output=output,
                        intermediate_steps=intermediate_steps,
                        execution_time=time.time() - start_time
                    )

            # 达到最大迭代次数
            output = response.content if response.content else "分析完成"
            return AgentResult(
                task_id=task.id,
                agent_name=self.name,
                agent_type=self.agent_type,
                success=True,
                output=output,
                intermediate_steps=intermediate_steps,
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
        """流式执行分析任务 - 使用LLM动态工具调用"""
        start_time = time.time()
        intermediate_steps = []

        try:
            # 构建分析提示
            analysis_prompt = self._build_analysis_prompt(task, context)

            # 发送开始事件
            yield {
                "type": "thought",
                "content": "开始分析检索到的信息..."
            }

            # 构建消息
            messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
            messages.append(HumanMessage(content=analysis_prompt))

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
                            "execution_time": time.time() - start_time
                        }
                    }
                    return

            # 达到最大迭代次数
            output = response.content if response.content else "分析完成"
            yield {
                "type": "result",
                "result": {
                    "task_id": task.id,
                    "agent_name": self.name,
                    "agent_type": self.agent_type.value,
                    "success": True,
                    "output": output,
                    "intermediate_steps": intermediate_steps,
                    "execution_time": time.time() - start_time
                }
            }

        except Exception as e:
            import traceback
            yield {
                "type": "error",
                "content": f"分析出错: {str(e)}\n{traceback.format_exc()}"
            }

    def _build_analysis_prompt(self, task: AgentTask, context: Dict[str, Any]) -> str:
        """构建分析提示"""
        prompt = f"分析任务: {task.description}\n\n"

        # 添加检索结果
        for key, value in context.items():
            if key.startswith("prev_result_"):
                prompt += f"检索结果:\n{value}\n\n"

        prompt += "请对以上信息进行深度分析，得出结论。"
        return prompt
