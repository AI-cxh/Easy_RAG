"""Agent基类定义"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from langchain_core.tools import BaseTool


class AgentType(str, Enum):
    """Agent类型枚举"""
    ORCHESTRATOR = "orchestrator"
    RETRIEVAL = "retrieval"
    ANALYSIS = "analysis"
    WRITING = "writing"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """Agent任务"""
    id: str
    description: str
    agent_type: AgentType
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class AgentResult:
    """Agent执行结果"""
    task_id: str
    agent_name: str
    agent_type: AgentType
    success: bool
    output: str
    intermediate_steps: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    search_results: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(
        self,
        name: str,
        description: str,
        agent_type: AgentType,
        system_prompt: str = "",
        tools: Optional[List[BaseTool]] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        初始化Agent

        Args:
            name: Agent名称
            description: Agent描述
            agent_type: Agent类型
            system_prompt: 系统提示词
            tools: 可用工具列表
            model_name: 使用的模型名称
            temperature: 温度参数
        """
        self.name = name
        self.description = description
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model_name = model_name
        self.temperature = temperature

    @abstractmethod
    async def execute(self, task: AgentTask, context: Dict[str, Any]) -> AgentResult:
        """
        执行任务

        Args:
            task: 要执行的任务
            context: 执行上下文

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    async def stream_execute(
        self, task: AgentTask, context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式执行任务

        Args:
            task: 要执行的任务
            context: 执行上下文

        Yields:
            执行过程中的事件
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type.value,
            "system_prompt": self.system_prompt,
            "tools": [tool.name for tool in self.tools],
            "model_name": self.model_name,
            "temperature": self.temperature
        }
