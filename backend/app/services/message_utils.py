"""消息序列化与历史回放工具。"""
from __future__ import annotations

from typing import Any, Dict, Optional
import json

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage


def _normalize_content(content: Any) -> str:
    """将消息内容规整为可持久化字符串。"""
    if isinstance(content, str):
        return content
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False)


def serialize_ai_message(message: AIMessage) -> Dict[str, Any]:
    """提取 AIMessage 中需要跨轮次保留的字段。"""
    payload: Dict[str, Any] = {
        "content": _normalize_content(message.content)
    }

    if getattr(message, "additional_kwargs", None):
        payload["additional_kwargs"] = message.additional_kwargs
    if getattr(message, "response_metadata", None):
        payload["response_metadata"] = message.response_metadata
    if getattr(message, "tool_calls", None):
        payload["tool_calls"] = message.tool_calls
    if getattr(message, "invalid_tool_calls", None):
        payload["invalid_tool_calls"] = message.invalid_tool_calls
    if getattr(message, "name", None):
        payload["name"] = message.name
    if getattr(message, "id", None):
        payload["id"] = message.id

    usage_metadata = getattr(message, "usage_metadata", None)
    if usage_metadata:
        try:
            payload["usage_metadata"] = dict(usage_metadata)
        except Exception:
            payload["usage_metadata"] = usage_metadata

    return payload


def build_history_message(msg: Dict[str, Any]) -> BaseMessage:
    """把持久化的历史消息恢复为 LangChain Message。"""
    role = msg.get("role")
    content = msg.get("content", "")

    if role == "user":
        return HumanMessage(content=content)

    assistant_payload = msg.get("assistant_message") or {}
    if role == "assistant":
        return AIMessage(
            content=assistant_payload.get("content", content),
            additional_kwargs=assistant_payload.get("additional_kwargs", {}),
            response_metadata=assistant_payload.get("response_metadata", {}),
            tool_calls=assistant_payload.get("tool_calls", []),
            invalid_tool_calls=assistant_payload.get("invalid_tool_calls", []),
            name=assistant_payload.get("name"),
            id=assistant_payload.get("id"),
            usage_metadata=assistant_payload.get("usage_metadata")
        )

    return HumanMessage(content=content)
