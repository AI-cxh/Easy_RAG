"""Agent注册中心"""
from typing import Dict, List, Optional, Type
from app.services.multi_agent.base_agent import BaseAgent, AgentType


class AgentRegistry:
    """Agent注册中心 - 管理所有可用的Agent"""

    def __init__(self):
        """初始化注册中心"""
        self._agents: Dict[str, BaseAgent] = {}
        self._type_agents: Dict[AgentType, List[str]] = {
            agent_type: [] for agent_type in AgentType
        }

    def register(self, agent: BaseAgent) -> None:
        """
        注册Agent

        Args:
            agent: 要注册的Agent实例
        """
        self._agents[agent.name] = agent
        if agent.name not in self._type_agents[agent.agent_type]:
            self._type_agents[agent.agent_type].append(agent.name)

    def unregister(self, name: str) -> Optional[BaseAgent]:
        """
        注销Agent

        Args:
            name: Agent名称

        Returns:
            被注销的Agent实例，如果不存在则返回None
        """
        agent = self._agents.pop(name, None)
        if agent:
            self._type_agents[agent.agent_type].remove(name)
        return agent

    def get(self, name: str) -> Optional[BaseAgent]:
        """
        获取Agent

        Args:
            name: Agent名称

        Returns:
            Agent实例，如果不存在则返回None
        """
        return self._agents.get(name)

    def get_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """
        获取指定类型的所有Agent

        Args:
            agent_type: Agent类型

        Returns:
            该类型的所有Agent实例列表
        """
        return [self._agents[name] for name in self._type_agents[agent_type]]

    def get_all(self) -> List[BaseAgent]:
        """
        获取所有注册的Agent

        Returns:
            所有Agent实例列表
        """
        return list(self._agents.values())

    def list_names(self) -> List[str]:
        """
        获取所有Agent名称

        Returns:
            所有Agent名称列表
        """
        return list(self._agents.keys())

    def exists(self, name: str) -> bool:
        """
        检查Agent是否存在

        Args:
            name: Agent名称

        Returns:
            是否存在
        """
        return name in self._agents

    def clear(self) -> None:
        """清空所有注册的Agent"""
        self._agents.clear()
        for agent_type in self._type_agents:
            self._type_agents[agent_type] = []

    def to_dict_list(self) -> List[Dict]:
        """
        将所有Agent转换为字典列表

        Returns:
            Agent字典列表
        """
        return [agent.to_dict() for agent in self._agents.values()]


# 全局Agent注册中心实例
agent_registry = AgentRegistry()
