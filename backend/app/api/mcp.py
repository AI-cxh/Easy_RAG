"""MCP配置管理API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.mcp_client import mcp_client
from app.config import settings

router = APIRouter()


class MCPServerConfig(BaseModel):
    """MCP服务器配置"""
    name: str = Field(..., min_length=1, max_length=100, description="服务器名称")
    transport: str = Field(default="stdio", description="传输类型: stdio | http | streamable-http")
    command: Optional[str] = Field(None, description="stdio模式的命令")
    args: Optional[List[str]] = Field(default=None, description="stdio模式的参数列表")
    url: Optional[str] = Field(None, description="http模式的URL")


class MCPServerResponse(BaseModel):
    """MCP服务器响应"""
    name: str
    transport: str
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    status: str = "configured"  # configured | connected | error


class MCPToolResponse(BaseModel):
    """MCP工具响应"""
    name: str
    description: Optional[str] = None


class MCPStatusResponse(BaseModel):
    """MCP状态响应"""
    initialized: bool
    servers: List[MCPServerResponse]
    tools: List[MCPToolResponse]


@router.get("/mcp/status", response_model=MCPStatusResponse)
async def get_mcp_status():
    """获取MCP客户端状态"""
    server_configs = mcp_client.get_server_configs()

    servers = []
    for config in server_configs:
        servers.append(MCPServerResponse(
            name=config.get("name", ""),
            transport=config.get("transport", "stdio"),
            command=config.get("command"),
            args=config.get("args"),
            url=config.get("url"),
            status="connected" if mcp_client.is_initialized() else "configured"
        ))

    tools = []
    for tool in mcp_client.get_tools():
        tools.append(MCPToolResponse(
            name=tool.name,
            description=tool.description if hasattr(tool, 'description') else None
        ))

    return MCPStatusResponse(
        initialized=mcp_client.is_initialized(),
        servers=servers,
        tools=tools
    )


@router.get("/mcp/servers", response_model=List[MCPServerResponse])
async def list_mcp_servers():
    """列出已配置的MCP服务器"""
    server_configs = mcp_client.get_server_configs()

    servers = []
    for config in server_configs:
        servers.append(MCPServerResponse(
            name=config.get("name", ""),
            transport=config.get("transport", "stdio"),
            command=config.get("command"),
            args=config.get("args"),
            url=config.get("url"),
            status="connected" if mcp_client.is_initialized() else "configured"
        ))

    return servers


@router.post("/mcp/servers", response_model=MCPServerResponse)
async def add_mcp_server(config: MCPServerConfig):
    """添加MCP服务器配置"""
    # 验证配置
    if config.transport == "stdio" and not config.command:
        raise HTTPException(status_code=400, detail="stdio transport requires 'command' field")

    if config.transport in ["http", "streamable-http"] and not config.url:
        raise HTTPException(status_code=400, detail=f"{config.transport} transport requires 'url' field")

    # 转换为字典
    config_dict = config.model_dump(exclude_none=True)

    # 添加服务器
    success = await mcp_client.add_server(config_dict)

    if not success:
        raise HTTPException(status_code=400, detail="Server with this name already exists")

    return MCPServerResponse(
        name=config.name,
        transport=config.transport,
        command=config.command,
        args=config.args,
        url=config.url,
        status="connected"
    )


@router.delete("/mcp/servers/{name}")
async def remove_mcp_server(name: str):
    """移除MCP服务器"""
    success = await mcp_client.remove_server(name)

    if not success:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")

    return {"message": f"Server '{name}' removed successfully"}


@router.get("/mcp/tools", response_model=List[MCPToolResponse])
async def list_mcp_tools():
    """列出所有MCP工具"""
    tools = []
    for tool in mcp_client.get_tools():
        tools.append(MCPToolResponse(
            name=tool.name,
            description=tool.description if hasattr(tool, 'description') else None
        ))

    return tools


@router.post("/mcp/reload")
async def reload_mcp_servers():
    """重新加载MCP服务器配置"""
    await mcp_client.close()
    await mcp_client.initialize(settings.MCP_SERVERS)

    return {
        "message": "MCP servers reloaded",
        "initialized": mcp_client.is_initialized(),
        "tools_count": len(mcp_client.get_tools())
    }
