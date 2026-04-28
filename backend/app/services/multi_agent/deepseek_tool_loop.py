"""DeepSeek thinking/tool-call 兼容辅助函数。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from langchain_core.tools import BaseTool

from app.config import settings


def should_use_native_deepseek(model_name: Optional[str]) -> bool:
    """判断当前模型是否应走 DeepSeek 原生工具循环。"""
    candidate = f"{model_name or ''} {settings.OPENAI_API_BASE or ''}".lower()
    return "deepseek" in candidate


def build_native_client() -> AsyncOpenAI:
    """构建 DeepSeek/OpenAI 兼容异步客户端。"""
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE
    )


def tool_to_openai_schema(tool: BaseTool) -> Dict[str, Any]:
    """将 LangChain Tool 转换为 OpenAI function schema。"""
    parameters: Dict[str, Any] = {"type": "object", "properties": {}}
    args_schema = getattr(tool, "args_schema", None)

    if isinstance(args_schema, dict):
        if args_schema.get("type") == "object":
            parameters = args_schema
    elif args_schema is not None:
        try:
            parameters = args_schema.model_json_schema()
        except Exception:
            parameters = {"type": "object", "properties": {}}

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": getattr(tool, "description", "") or f"Tool: {tool.name}",
            "parameters": parameters
        }
    }


def build_native_messages(system_prompt: str, prompt: str) -> List[Dict[str, Any]]:
    """构建原生 SDK 请求消息。"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
