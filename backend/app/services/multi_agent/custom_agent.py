"""自定义Agent - 用户可配置的通用Agent"""
from typing import List, Dict, Optional, Any, AsyncGenerator
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType
)


class CustomAgent(BaseAgent):
    """自定义Agent - 用户可配置的通用Agent"""

    DEFAULT_SYSTEM_PROMPT = """你是一个专业的助手。请根据用户的问题和提供的上下文，给出准确、有帮助的回答。

回答要求：
- 准确理解用户的问题
- 充分利用提供的上下文信息
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
            tools: 可用工具列表
            model_name: 使用的模型名称
            temperature: 温度参数
        """
        super().__init__(
            name=name,
            description=description,
            agent_type=AgentType.CUSTOM,
            system_prompt=system_prompt or self.DEFAULT_SYSTEM_PROMPT,
            tools=tools or [],
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
        """执行任务"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 构建执行提示
            prompt = self._build_prompt(task, context)

            # 执行
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]

            response = await self.llm.ainvoke(messages)
            output = response.content

            intermediate_steps.append({
                "step": "execute",
                "input": prompt[:500],
                "output": output
            })

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
        """流式执行任务"""
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

            # 执行
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]

            # 流式输出
            output = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    output += chunk.content
                    yield {
                        "type": "answer",
                        "content": chunk.content
                    }

            intermediate_steps.append({
                "step": "execute",
                "input": prompt[:500],
                "output": output
            })

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
