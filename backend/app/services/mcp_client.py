"""MCP客户端服务：连接外部MCP服务器并加载工具"""
from typing import List, Dict, Optional, Any
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)


class MCPClientService:
    """MCP客户端服务 - 管理与外部MCP服务器的连接"""

    def __init__(self):
        self.client: Optional[Any] = None
        self.tools: List[BaseTool] = []
        self._initialized = False
        self._server_configs: List[Dict] = []

    async def initialize(self, server_configs: List[Dict]) -> None:
        """
        初始化MCP客户端并连接服务器

        Args:
            server_configs: MCP服务器配置列表
                每个配置包含:
                - name: 服务器名称
                - transport: 传输类型 ("stdio" | "http" | "streamable-http")
                - command: stdio模式的命令 (可选)
                - args: stdio模式的参数列表 (可选)
                - url: http模式的URL (可选)
        """
        if not server_configs:
            logger.info("No MCP servers configured, skipping initialization")
            return

        self._server_configs = server_configs

        try:
            # 动态导入MCP适配器
            from langchain_mcp_adapters.client import MultiServerMCPClient

            # 构建服务器配置
            servers = {}
            for config in server_configs:
                name = config.get("name")
                transport = config.get("transport", "stdio")

                if not name:
                    logger.warning("MCP server config missing 'name', skipping")
                    continue

                if transport == "stdio":
                    command = config.get("command")
                    if not command:
                        logger.warning(f"MCP server '{name}' missing 'command' for stdio transport")
                        continue
                    servers[name] = {
                        "command": command,
                        "args": config.get("args", []),
                        "transport": "stdio"
                    }
                    logger.info(f"Configured MCP server '{name}' with stdio transport")

                elif transport in ["http", "streamable-http"]:
                    url = config.get("url")
                    if not url:
                        logger.warning(f"MCP server '{name}' missing 'url' for {transport} transport")
                        continue
                    servers[name] = {
                        "url": url,
                        "transport": transport
                    }
                    logger.info(f"Configured MCP server '{name}' with {transport} transport")

                else:
                    logger.warning(f"Unknown transport type '{transport}' for MCP server '{name}'")

            if not servers:
                logger.warning("No valid MCP server configurations found")
                return

            # 创建MCP客户端
            self.client = MultiServerMCPClient(servers)

            # 获取所有工具
            self.tools = await self.client.get_tools()
            self._initialized = True

            logger.info(f"MCP client initialized with {len(self.tools)} tools from {len(servers)} servers")
            for tool in self.tools:
                logger.info(f"  - Loaded MCP tool: {tool.name}")

        except ImportError as e:
            logger.warning(f"MCP adapters not installed, skipping MCP initialization: {e}")
            logger.info("Install with: pip install langchain-mcp-adapters")
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            import traceback
            traceback.print_exc()

    def get_tools(self) -> List[BaseTool]:
        """获取所有MCP工具"""
        return self.tools

    def get_server_configs(self) -> List[Dict]:
        """获取当前配置的服务器列表"""
        return self._server_configs.copy()

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized

    async def add_server(self, config: Dict) -> bool:
        """
        添加新的MCP服务器

        注意：添加新服务器需要重新初始化所有连接

        Args:
            config: 服务器配置

        Returns:
            是否添加成功
        """
        name = config.get("name")
        if not name:
            return False

        # 检查是否已存在
        for existing in self._server_configs:
            if existing.get("name") == name:
                logger.warning(f"MCP server '{name}' already exists")
                return False

        # 添加配置
        self._server_configs.append(config)

        # 重新初始化
        self._initialized = False
        self.tools = []
        await self.initialize(self._server_configs)

        return True

    async def remove_server(self, name: str) -> bool:
        """
        移除MCP服务器

        Args:
            name: 服务器名称

        Returns:
            是否移除成功
        """
        # 查找并移除
        for i, config in enumerate(self._server_configs):
            if config.get("name") == name:
                self._server_configs.pop(i)

                # 重新初始化
                self._initialized = False
                self.tools = []
                await self.initialize(self._server_configs)

                return True

        return False

    async def close(self) -> None:
        """关闭MCP连接并清理资源"""
        if self.client:
            try:
                # MCP客户端的清理逻辑
                # MultiServerMCPClient 可能有自己的清理方法
                if hasattr(self.client, 'close'):
                    await self.client.close()
                elif hasattr(self.client, 'cleanup'):
                    await self.client.cleanup()
            except Exception as e:
                logger.error(f"Error closing MCP client: {e}")
            finally:
                self.client = None
                self.tools = []
                self._initialized = False
                logger.info("MCP client closed")


# 全局MCP客户端实例
mcp_client = MCPClientService()
