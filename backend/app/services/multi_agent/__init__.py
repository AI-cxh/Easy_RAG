"""多Agent协同模块"""
from app.services.multi_agent.base_agent import BaseAgent, AgentResult, AgentTask, AgentType, TaskStatus
from app.services.multi_agent.agent_registry import AgentRegistry, agent_registry
from app.services.multi_agent.orchestrator import OrchestratorAgent
from app.services.multi_agent.retrieval_agent import RetrievalAgent
from app.services.multi_agent.analysis_agent import AnalysisAgent
from app.services.multi_agent.writing_agent import WritingAgent
from app.services.multi_agent.custom_agent import CustomAgent

__all__ = [
    "BaseAgent",
    "AgentResult",
    "AgentTask",
    "AgentType",
    "TaskStatus",
    "AgentRegistry",
    "agent_registry",
    "OrchestratorAgent",
    "RetrievalAgent",
    "AnalysisAgent",
    "WritingAgent",
    "CustomAgent",
]
