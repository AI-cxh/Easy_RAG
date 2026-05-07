"""设置API路由"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os

from app.config import settings

router = APIRouter()

SETTINGS_FILE = "./settings.json"


MASKED_PREFIX = "***"


def mask_api_key(key: str) -> str:
    """脱敏 API Key，只显示末尾 4 位"""
    if not key:
        return ""
    if len(key) <= 4:
        return MASKED_PREFIX
    return MASKED_PREFIX + key[-4:]


class ModelSettings(BaseModel):
    model: str = ""
    apiKey: str = ""
    apiUrl: str = ""


class MCPServerConfig(BaseModel):
    """MCP服务器配置"""
    name: str = ""
    transport: str = "stdio"  # stdio | http | streamable-http
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None


class SettingsData(BaseModel):
    llm: ModelSettings = ModelSettings()
    embedding: ModelSettings = ModelSettings()
    rerank: ModelSettings = ModelSettings()
    mcpServers: List[MCPServerConfig] = []


def load_settings_from_file() -> SettingsData:
    """从文件加载设置"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return SettingsData(**data)
        except:
            pass

    # 返回当前环境变量中的设置
    return SettingsData(
        llm=ModelSettings(
            model=settings.MODEL_NAME,
            apiKey=settings.OPENAI_API_KEY,
            apiUrl=settings.OPENAI_API_BASE or ""
        ),
        embedding=ModelSettings(
            model=settings.EMBEDDING_MODEL,
            apiKey=settings.EMBEDDING_API_KEY or settings.OPENAI_API_KEY,
            apiUrl=settings.EMBEDDING_API_BASE or settings.OPENAI_API_BASE or ""
        ),
        rerank=ModelSettings(
            model=settings.RERANK_MODEL,
            apiKey=settings.RERANK_API_KEY or "",
            apiUrl=settings.RERANK_API_BASE or ""
        ),
        mcpServers=[]
    )


def save_settings_to_file(data: SettingsData):
    """保存设置到文件（API Key 为脱敏值时保留已有值）"""
    existing = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            pass

    payload = data.model_dump()

    for section in ("llm", "embedding", "rerank"):
        if payload[section]["apiKey"].startswith(MASKED_PREFIX):
            payload[section]["apiKey"] = existing.get(section, {}).get("apiKey", "")

    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


@router.get("/settings")
async def get_settings():
    """获取当前设置（API Key 脱敏返回）"""
    data = load_settings_from_file()
    result = data.model_dump()
    result["llm"]["apiKey"] = mask_api_key(data.llm.apiKey)
    result["embedding"]["apiKey"] = mask_api_key(data.embedding.apiKey)
    result["rerank"]["apiKey"] = mask_api_key(data.rerank.apiKey)
    return result


@router.post("/settings")
async def save_settings(data: SettingsData):
    """保存设置"""
    save_settings_to_file(data)

    # 更新运行时设置
    if data.llm.model:
        settings.MODEL_NAME = data.llm.model
    if data.llm.apiKey and not data.llm.apiKey.startswith(MASKED_PREFIX):
        settings.OPENAI_API_KEY = data.llm.apiKey
    if data.llm.apiUrl:
        settings.OPENAI_API_BASE = data.llm.apiUrl

    if data.embedding.model:
        settings.EMBEDDING_MODEL = data.embedding.model
    if data.embedding.apiKey and not data.embedding.apiKey.startswith(MASKED_PREFIX):
        settings.EMBEDDING_API_KEY = data.embedding.apiKey
    if data.embedding.apiUrl:
        settings.EMBEDDING_API_BASE = data.embedding.apiUrl

    if data.rerank.model:
        settings.RERANK_MODEL = data.rerank.model
    if data.rerank.apiKey and not data.rerank.apiKey.startswith(MASKED_PREFIX):
        settings.RERANK_API_KEY = data.rerank.apiKey
    if data.rerank.apiUrl:
        settings.RERANK_API_BASE = data.rerank.apiUrl

    return {"success": True, "message": "设置已保存"}
