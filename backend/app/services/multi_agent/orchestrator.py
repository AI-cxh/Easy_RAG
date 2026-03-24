"""主控Agent - 负责任务分解和协调"""
from typing import List, Dict, Optional, Any, AsyncGenerator
import json
import uuid
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.services.multi_agent.base_agent import (
    BaseAgent, AgentResult, AgentTask, AgentType, TaskStatus
)
from app.services.multi_agent.agent_registry import AgentRegistry


class OrchestratorAgent(BaseAgent):
    """主控Agent - 负责任务分解和协调"""

    SYSTEM_PROMPT = """你是一个多Agent系统的主控协调器。你的职责是：
1. 分析用户问题，理解问题的核心需求
2. 制定执行计划，决定需要调用哪些专业Agent
3. 协调各Agent的执行顺序
4. 综合各Agent的结果，生成最终回答

可用的专业Agent：
- 检索Agent (retrieval): 负责从知识库和网络搜索相关信息
- 分析Agent (analysis): 负责深度分析和推理
- 写作Agent (writing): 负责组织语言生成最终回答

你需要以JSON格式输出执行计划：
{
    "analysis": "问题分析...",
    "plan": [
        {
            "agent": "retrieval",
            "task": "检索相关文档和信息",
            "priority": 1
        },
        {
            "agent": "analysis",
            "task": "分析检索结果并得出结论",
            "priority": 2,
            "depends_on": ["retrieval"]
        }
    ]
}

注意：
- 简单问题可能只需要一个Agent
- 复杂问题需要多个Agent协作
- 考虑Agent之间的依赖关系
- 优先级数字越小越先执行"""

    def __init__(
        self,
        agent_registry: Optional[AgentRegistry] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        初始化主控Agent

        Args:
            agent_registry: Agent注册中心
            model_name: 使用的模型名称
            temperature: 温度参数
        """
        super().__init__(
            name="orchestrator",
            description="主控协调Agent，负责任务分解和协调",
            agent_type=AgentType.ORCHESTRATOR,
            system_prompt=self.SYSTEM_PROMPT,
            model_name=model_name or settings.MODEL_NAME,
            temperature=temperature
        )
        self.agent_registry = agent_registry or AgentRegistry()
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

    async def plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[AgentTask]:
        """
        分析用户问题，制定执行计划

        Args:
            query: 用户问题
            context: 额外上下文（如可用的知识库ID等）

        Returns:
            任务列表
        """
        # 构建规划提示
        plan_prompt = self._build_plan_prompt(query, context)

        # 调用LLM生成计划
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=plan_prompt)
        ]

        response = await self.llm.ainvoke(messages)

        # 解析计划
        tasks = self._parse_plan(response.content)

        return tasks

    def _build_plan_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建规划提示"""
        prompt = f"请分析以下用户问题，并制定执行计划：\n\n用户问题：{query}\n"

        if context:
            if context.get("kb_ids"):
                prompt += f"\n可用知识库ID: {context['kb_ids']}"
            if context.get("use_web_search"):
                prompt += "\n网络搜索: 可用"

        prompt += "\n\n请输出执行计划（JSON格式）："
        return prompt

    def _parse_plan(self, plan_str: str) -> List[AgentTask]:
        """解析执行计划"""
        tasks = []
        # 用于记录 agent_type 到 task_id 的映射
        type_to_task_id: Dict[str, str] = {}

        try:
            # 尝试提取JSON
            json_start = plan_str.find("{")
            json_end = plan_str.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = plan_str[json_start:json_end]
                plan_data = json.loads(json_str)

                for idx, item in enumerate(plan_data.get("plan", [])):
                    agent_type_str = item.get("agent", "retrieval")
                    try:
                        agent_type = AgentType(agent_type_str)
                    except ValueError:
                        agent_type = AgentType.CUSTOM

                    task_id = f"task_{uuid.uuid4().hex[:8]}"
                    # 解析依赖，将 agent_type 转换为对应的 task_id
                    depends_on_types = item.get("depends_on", [])
                    depends_on_ids = []
                    for dep_type in depends_on_types:
                        if dep_type in type_to_task_id:
                            depends_on_ids.append(type_to_task_id[dep_type])

                    task = AgentTask(
                        id=task_id,
                        description=item.get("task", ""),
                        agent_type=agent_type,
                        priority=item.get("priority", idx),
                        dependencies=depends_on_ids
                    )
                    tasks.append(task)
                    # 记录映射
                    type_to_task_id[agent_type_str] = task_id

        except json.JSONDecodeError:
            # 如果解析失败，创建默认任务
            task_id_1 = f"task_{uuid.uuid4().hex[:8]}"
            task_id_2 = f"task_{uuid.uuid4().hex[:8]}"
            tasks = [
                AgentTask(
                    id=task_id_1,
                    description="检索相关信息",
                    agent_type=AgentType.RETRIEVAL,
                    priority=1
                ),
                AgentTask(
                    id=task_id_2,
                    description="生成回答",
                    agent_type=AgentType.WRITING,
                    priority=2,
                    dependencies=[task_id_1]
                )
            ]

        # 按优先级排序
        tasks.sort(key=lambda t: t.priority)
        return tasks

    async def execute_plan(
        self,
        tasks: List[AgentTask],
        context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        按计划调度各Agent执行

        Args:
            tasks: 任务列表
            context: 执行上下文

        Yields:
            执行过程中的事件
        """
        results: Dict[str, AgentResult] = {}
        completed_tasks: set = set()

        while len(completed_tasks) < len(tasks):
            # 找到可以执行的任务（依赖已满足）
            ready_tasks = [
                task for task in tasks
                if task.id not in completed_tasks
                and all(dep in completed_tasks for dep in task.dependencies)
            ]

            if not ready_tasks:
                # 没有可执行的任务，可能存在循环依赖
                yield {
                    "type": "error",
                    "content": "任务依赖关系存在问题，无法继续执行"
                }
                break

            # 执行就绪的任务
            for task in ready_tasks:
                # 更新任务状态
                task.status = TaskStatus.RUNNING

                # 发送任务开始事件
                yield {
                    "type": "task_start",
                    "task_id": task.id,
                    "agent_type": task.agent_type.value,
                    "description": task.description
                }

                # 获取对应的Agent
                agent = self._get_agent_for_task(task)
                if not agent:
                    yield {
                        "type": "error",
                        "task_id": task.id,
                        "content": f"未找到类型为 {task.agent_type.value} 的Agent"
                    }
                    task.status = TaskStatus.FAILED
                    completed_tasks.add(task.id)
                    continue

                # 构建任务上下文
                task_context = self._build_task_context(task, results, context)

                try:
                    # 流式执行Agent
                    async for event in agent.stream_execute(task, task_context):
                        event["task_id"] = task.id
                        yield event

                        # 收集结果
                        if event.get("type") == "result":
                            results[task.id] = event.get("result")

                    task.status = TaskStatus.COMPLETED

                except Exception as e:
                    import traceback
                    task.status = TaskStatus.FAILED
                    yield {
                        "type": "error",
                        "task_id": task.id,
                        "content": f"Agent执行出错: {str(e)}\n{traceback.format_exc()}"
                    }

                completed_tasks.add(task.id)

                # 发送任务完成事件
                yield {
                    "type": "task_complete",
                    "task_id": task.id,
                    "status": task.status.value
                }

    def _get_agent_for_task(self, task: AgentTask) -> Optional[BaseAgent]:
        """获取执行任务的Agent"""
        agents = self.agent_registry.get_by_type(task.agent_type)
        if agents:
            return agents[0]
        return None

    def _build_task_context(
        self,
        task: AgentTask,
        results: Dict[str, Any],
        global_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建任务执行上下文"""
        import copy
        context = copy.deepcopy(global_context)

        # 确保必要的字段存在
        if "sources" not in context:
            context["sources"] = []
        if "search_results" not in context:
            context["search_results"] = []

        # 添加依赖任务的结果
        for dep_id in task.dependencies:
            if dep_id in results:
                dep_result = results[dep_id]
                # dep_result 现在是字典
                context[f"prev_result_{dep_id}"] = dep_result.get("output", "")
                if dep_result.get("sources"):
                    context["sources"].extend(dep_result["sources"])
                if dep_result.get("search_results"):
                    context["search_results"].extend(dep_result["search_results"])

        return context

    async def synthesize(
        self,
        query: str,
        results: Dict[str, AgentResult]
    ) -> AsyncGenerator[str, None]:
        """
        综合各Agent结果，生成最终回答

        Args:
            query: 原始用户问题
            results: 各Agent的执行结果

        Yields:
            最终回答的文本块
        """
        # 构建综合提示
        synthesis_prompt = self._build_synthesis_prompt(query, results)

        messages = [
            SystemMessage(content="你是一个专业的回答生成器。请根据各Agent的分析结果，生成一个完整、准确、有条理的回答。"),
            HumanMessage(content=synthesis_prompt)
        ]

        # 流式生成最终回答
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

    def _build_synthesis_prompt(
        self,
        query: str,
        results: Dict[str, Any]
    ) -> str:
        """构建综合提示"""
        prompt = f"用户问题：{query}\n\n"

        if results:
            prompt += "以下是各专业Agent的分析结果：\n\n"
            for task_id, result in results.items():
                # result 现在是字典
                agent_name = result.get("agent_name", "unknown")
                agent_type = result.get("agent_type", "unknown")
                output = result.get("output", "")
                prompt += f"### {agent_name} ({agent_type})\n"
                prompt += f"任务：{output}\n\n"
            prompt += "请综合以上分析结果，生成一个完整、准确、有条理的回答。"
        else:
            prompt += "请直接回答用户的问题。"

        return prompt

    async def execute(
        self,
        task: AgentTask,
        context: Dict[str, Any]
    ) -> AgentResult:
        """执行任务（主控Agent通常不直接执行任务）"""
        start_time = time.time()

        try:
            # 制定计划
            tasks = await self.plan(task.description, context)

            # 执行计划
            results = {}
            async for event in self.execute_plan(tasks, context):
                if event.get("type") == "result":
                    results[event["task_id"]] = event["result"]

            # 综合结果
            final_output = ""
            async for chunk in self.synthesize(task.description, results):
                final_output += chunk

            return AgentResult(
                task_id=task.id,
                agent_name=self.name,
                agent_type=self.agent_type,
                success=True,
                output=final_output,
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
        self,
        task: AgentTask,
        context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式执行任务"""
        start_time = time.time()

        try:
            # 发送规划开始事件
            yield {
                "type": "planning",
                "content": "正在分析问题并制定执行计划..."
            }

            # 制定计划
            tasks = await self.plan(task.description, context)

            # 如果没有生成任务，创建默认任务
            if not tasks:
                tasks = [
                    AgentTask(
                        id=f"task_{uuid.uuid4().hex[:8]}",
                        description="检索相关信息",
                        agent_type=AgentType.RETRIEVAL,
                        priority=1
                    ),
                    AgentTask(
                        id=f"task_{uuid.uuid4().hex[:8]}",
                        description="生成回答",
                        agent_type=AgentType.WRITING,
                        priority=2
                    )
                ]

            # 发送计划事件
            yield {
                "type": "plan",
                "tasks": [
                    {
                        "id": t.id,
                        "agent_type": t.agent_type.value,
                        "description": t.description,
                        "priority": t.priority
                    }
                    for t in tasks
                ]
            }

            # 执行计划
            results = {}
            async for event in self.execute_plan(tasks, context):
                yield event

                # 收集结果
                if event.get("type") == "result":
                    results[event["task_id"]] = event["result"]

            # 发送综合开始事件
            yield {
                "type": "synthesizing",
                "content": "正在综合各Agent的结果..."
            }

            # 综合结果并流式输出
            final_output = ""
            async for chunk in self.synthesize(task.description, results):
                final_output += chunk
                yield {
                    "type": "answer",
                    "content": chunk
                }

            # 发送最终结果
            all_sources = []
            all_search_results = []
            for result in results.values():
                # result 现在是字典
                if result.get("sources"):
                    all_sources.extend(result["sources"])
                if result.get("search_results"):
                    all_search_results.extend(result["search_results"])

            yield {
                "type": "result",
                "result": {
                    "task_id": task.id,
                    "agent_name": self.name,
                    "agent_type": self.agent_type.value,
                    "success": True,
                    "output": final_output,
                    "sources": list(set(all_sources)),
                    "search_results": all_search_results,
                    "execution_time": time.time() - start_time
                }
            }

        except Exception as e:
            import traceback
            error_detail = f"执行出错: {str(e)}\n{traceback.format_exc()}"
            yield {
                "type": "error",
                "content": error_detail
            }
