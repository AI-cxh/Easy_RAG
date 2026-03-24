"""写作Agent - 负责组织语言生成最终回答"""
from typing import Dict, Optional, Any, AsyncGenerator
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType
)


class WritingAgent(BaseAgent):
    """写作Agent - 负责组织语言生成最终回答"""

    SYSTEM_PROMPT = """你是一个专业的写作Agent。你的职责是：
1. 综合各Agent的分析结果
2. 组织语言，生成清晰、有条理的回答
3. 确保回答准确、完整、易读

写作要求：
- 回答要结构清晰，逻辑连贯
- 使用适当的标题和分段
- 引用来源要准确标注
- 语言要专业但不晦涩
- 适当使用列表、表格等格式

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
        super().__init__(
            name="writing_agent",
            description="写作Agent，负责组织语言生成最终回答",
            agent_type=AgentType.WRITING,
            system_prompt=self.SYSTEM_PROMPT,
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
        """执行写作任务"""
        start_time = time.time()
        intermediate_steps = []
        sources = []
        search_results = []

        try:
            # 构建写作提示
            writing_prompt = self._build_writing_prompt(task, context)

            # 执行写作
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=writing_prompt)
            ]

            response = await self.llm.ainvoke(messages)
            output = response.content

            intermediate_steps.append({
                "step": "writing",
                "input": writing_prompt[:500],
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
        """流式执行写作任务"""
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

            # 执行写作
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=writing_prompt)
            ]

            # 流式输出回答
            output = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    output += chunk.content
                    yield {
                        "type": "answer",
                        "content": chunk.content
                    }

            intermediate_steps.append({
                "step": "writing",
                "input": writing_prompt[:500],
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
