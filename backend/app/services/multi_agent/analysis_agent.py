"""分析Agent - 负责深度分析和推理"""
from typing import Dict, Optional, Any, AsyncGenerator
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType
)


class AnalysisAgent(BaseAgent):
    """分析Agent - 负责深度分析和推理"""

    SYSTEM_PROMPT = """你是一个专业的分析Agent。你的职责是：
1. 对检索到的信息进行深度分析
2. 识别关键信息和潜在关联
3. 进行逻辑推理和归纳
4. 得出分析结论

分析要求：
- 客观、全面地分析信息
- 识别信息之间的关联和矛盾
- 进行逻辑推理，得出合理结论
- 指出信息的可靠性和局限性

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
        super().__init__(
            name="analysis_agent",
            description="分析Agent，负责深度分析和推理",
            agent_type=AgentType.ANALYSIS,
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
        """执行分析任务"""
        start_time = time.time()
        intermediate_steps = []

        try:
            # 构建分析提示
            analysis_prompt = self._build_analysis_prompt(task, context)

            # 执行分析
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]

            response = await self.llm.ainvoke(messages)
            output = response.content

            intermediate_steps.append({
                "step": "analysis",
                "input": analysis_prompt[:500],
                "output": output
            })

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

    async def stream_execute(
        self, task: AgentTask, context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式执行分析任务"""
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

            # 执行分析
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]

            # 流式输出分析结果
            output = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    output += chunk.content
                    yield {
                        "type": "analysis",
                        "content": chunk.content
                    }

            intermediate_steps.append({
                "step": "analysis",
                "input": analysis_prompt[:500],
                "output": output
            })

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
