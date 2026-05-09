"""Mem0 跨会话用户长期记忆服务。"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class UserMemoryService:
    """封装 mem0 用户长期记忆，保持对主聊天流程的可选增强。"""

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self._init_error: Optional[str] = None

    @property
    def enabled(self) -> bool:
        return settings.MEM0_ENABLED

    async def build_user_memory_context(self, user_id: int, query: str) -> str:
        """检索跨会话用户记忆并格式化为 prompt 上下文。"""
        if not self.enabled or not query.strip():
            return ""

        client = self._get_client()
        if not client:
            return ""

        try:
            result = await self._search(client, user_id=user_id, query=query)
        except Exception as exc:
            logger.warning("Failed to search mem0 user memories: %s", exc)
            return ""

        memories = self._extract_memories(result)
        if not memories:
            return ""

        lines = ["用户长期记忆："]
        lines.extend([f"- {memory}" for memory in memories])
        return "\n".join(lines)

    async def list_user_memories(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """列出当前用户的 mem0 长期记忆。"""
        if not self.enabled:
            return []

        client = self._get_client()
        if not client:
            return []

        filters: Dict[str, Any] = {"user_id": str(user_id)}
        if settings.MEM0_AGENT_ID:
            filters["agent_id"] = settings.MEM0_AGENT_ID

        try:
            result = await client.get_all(filters=filters, top_k=limit)
        except TypeError:
            result = await client.get_all(user_id=str(user_id), top_k=limit)
        except Exception as exc:
            logger.warning("Failed to list mem0 user memories: %s", exc)
            raise

        return self._normalize_memory_items(result)

    async def delete_user_memory(self, user_id: int, memory_id: str) -> bool:
        """删除当前用户的一条 mem0 记忆。"""
        if not self.enabled:
            return False

        client = self._get_client()
        if not client:
            return False

        memories = await self.list_user_memories(user_id=user_id)
        if not any(str(memory.get("id")) == str(memory_id) for memory in memories):
            return False

        await client.delete(memory_id)
        return True

    async def add_turn(
        self,
        user_id: int,
        session_id: int,
        project_id: Optional[int],
        session_type: str,
        user_message: str,
        assistant_message: str
    ) -> None:
        """把一轮完整对话交给 mem0 自动抽取跨会话长期记忆。"""
        if not self.enabled or not user_message.strip() or not assistant_message.strip():
            return

        client = self._get_client()
        if not client:
            return

        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
        metadata = {
            "project_id": project_id,
            "session_id": session_id,
            "session_type": session_type
        }

        try:
            await self._add(client, user_id=user_id, messages=messages, metadata=metadata)
        except Exception as exc:
            logger.warning("Failed to add mem0 user memory: %s", exc)

    def schedule_add_turn(
        self,
        user_id: int,
        session_id: int,
        project_id: Optional[int],
        session_type: str,
        user_message: str,
        assistant_message: str
    ) -> None:
        """在当前事件循环中后台写入 mem0，避免阻塞 SSE 完成事件。"""
        if not self.enabled:
            return

        try:
            task = asyncio.create_task(self.add_turn(
                user_id=user_id,
                session_id=session_id,
                project_id=project_id,
                session_type=session_type,
                user_message=user_message,
                assistant_message=assistant_message
            ))
            task.add_done_callback(self._log_background_error)
        except RuntimeError as exc:
            logger.warning("Failed to schedule mem0 user memory write: %s", exc)

    def combine_contexts(self, *contexts: Optional[str]) -> str:
        """合并多个记忆上下文，自动跳过空字符串。"""
        return "\n\n".join(context.strip() for context in contexts if context and context.strip())

    def _get_client(self) -> Optional[Any]:
        if not self.enabled:
            return None
        if self._client:
            return self._client
        if self._init_error:
            return None

        try:
            from mem0 import AsyncMemory
        except Exception as exc:
            self._init_error = str(exc)
            logger.warning("mem0 is enabled but unavailable. Install mem0ai first: %s", exc)
            return None

        self._prepare_provider_env()
        config = self._build_mem0_config()

        try:
            if hasattr(AsyncMemory, "from_config"):
                self._client = AsyncMemory.from_config(config)
            else:
                try:
                    self._client = AsyncMemory(config=config)
                except TypeError:
                    logger.warning("AsyncMemory does not accept dict config, falling back to default mem0 config")
                    self._client = AsyncMemory()
            logger.info("mem0 user memory initialized")
        except Exception as exc:
            self._init_error = str(exc)
            logger.warning("Failed to initialize mem0 user memory: %s", exc)
            return None

        return self._client

    def _build_mem0_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "vector_store": {
                "provider": settings.MEM0_VECTOR_STORE_PROVIDER,
                "config": {
                    "collection_name": settings.MEM0_QDRANT_COLLECTION
                }
            }
        }

        if settings.MEM0_VECTOR_STORE_PROVIDER == "qdrant":
            config["vector_store"]["config"]["path"] = settings.MEM0_QDRANT_PATH

        if settings.MEM0_CUSTOM_INSTRUCTIONS:
            config["custom_instructions"] = settings.MEM0_CUSTOM_INSTRUCTIONS

        if settings.MEM0_LLM_PROVIDER:
            llm_config: Dict[str, Any] = {
                "temperature": settings.MEM0_LLM_TEMPERATURE
            }
            if settings.MEM0_LLM_MODEL:
                llm_config["model"] = settings.MEM0_LLM_MODEL
            llm_api_key = settings.MEM0_LLM_API_KEY or settings.OPENAI_API_KEY
            llm_base_url = settings.MEM0_LLM_BASE_URL or settings.OPENAI_API_BASE
            if llm_api_key:
                llm_config["api_key"] = llm_api_key
            if llm_base_url:
                if settings.MEM0_LLM_PROVIDER == "deepseek":
                    llm_config["deepseek_base_url"] = llm_base_url
                else:
                    llm_config["openai_base_url"] = llm_base_url
            config["llm"] = {
                "provider": settings.MEM0_LLM_PROVIDER,
                "config": llm_config
            }

        if settings.MEM0_EMBEDDER_PROVIDER:
            embedder_config: Dict[str, Any] = {}
            if settings.MEM0_EMBEDDER_MODEL:
                embedder_config["model"] = settings.MEM0_EMBEDDER_MODEL
            if settings.MEM0_EMBEDDER_DIMS:
                embedder_config["embedding_dims"] = settings.MEM0_EMBEDDER_DIMS
            embedder_api_key = settings.MEM0_EMBEDDER_API_KEY or settings.EMBEDDING_API_KEY or settings.OPENAI_API_KEY
            embedder_base_url = settings.MEM0_EMBEDDER_BASE_URL or settings.EMBEDDING_API_BASE or settings.OPENAI_API_BASE
            if embedder_api_key:
                embedder_config["api_key"] = embedder_api_key
            if embedder_base_url:
                embedder_config["openai_base_url"] = embedder_base_url
            config["embedder"] = {
                "provider": settings.MEM0_EMBEDDER_PROVIDER,
                "config": embedder_config
            }
            if settings.MEM0_EMBEDDER_DIMS and settings.MEM0_VECTOR_STORE_PROVIDER == "qdrant":
                config["vector_store"]["config"]["embedding_model_dims"] = settings.MEM0_EMBEDDER_DIMS

        return config

    def _prepare_provider_env(self) -> None:
        if settings.OPENAI_API_KEY and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        if settings.OPENAI_API_BASE and not os.environ.get("OPENAI_BASE_URL"):
            os.environ["OPENAI_BASE_URL"] = settings.OPENAI_API_BASE

        if (settings.MEM0_LLM_PROVIDER or "").lower() == "deepseek":
            if settings.OPENAI_API_KEY and not os.environ.get("DEEPSEEK_API_KEY"):
                os.environ["DEEPSEEK_API_KEY"] = settings.OPENAI_API_KEY
            if settings.OPENAI_API_BASE and not os.environ.get("DEEPSEEK_API_BASE"):
                os.environ["DEEPSEEK_API_BASE"] = settings.OPENAI_API_BASE

    async def _search(self, client: Any, user_id: int, query: str) -> Any:
        filters: Dict[str, Any] = {"user_id": str(user_id)}
        if settings.MEM0_AGENT_ID:
            filters["agent_id"] = settings.MEM0_AGENT_ID

        kwargs: Dict[str, Any] = {
            "query": query,
            "top_k": settings.MEM0_TOP_K,
            "filters": filters
        }

        try:
            return await client.search(**kwargs)
        except TypeError:
            return await client.search(query=query, top_k=settings.MEM0_TOP_K, user_id=str(user_id))

    async def _add(
        self,
        client: Any,
        user_id: int,
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any]
    ) -> Any:
        kwargs: Dict[str, Any] = {
            "messages": messages,
            "user_id": str(user_id),
            "metadata": metadata
        }
        if settings.MEM0_AGENT_ID:
            kwargs["agent_id"] = settings.MEM0_AGENT_ID

        try:
            return await client.add(**kwargs)
        except TypeError:
            kwargs.pop("agent_id", None)
            return await client.add(**kwargs)

    def _extract_memories(self, result: Any) -> List[str]:
        if isinstance(result, dict):
            items = result.get("results") or result.get("memories") or []
        elif isinstance(result, list):
            items = result
        else:
            return []

        memories: List[str] = []
        for item in items[:settings.MEM0_TOP_K]:
            if isinstance(item, str):
                text = item
            elif isinstance(item, dict):
                text = item.get("memory") or item.get("text") or item.get("content") or ""
            else:
                text = ""

            text = str(text).strip()
            if text:
                memories.append(text)

        return memories

    def _normalize_memory_items(self, result: Any) -> List[Dict[str, Any]]:
        if isinstance(result, dict):
            items = result.get("results") or result.get("memories") or []
        elif isinstance(result, list):
            items = result
        else:
            return []

        normalized: List[Dict[str, Any]] = []
        for item in items:
            if isinstance(item, str):
                normalized.append({
                    "id": item,
                    "memory": item,
                    "metadata": {},
                    "created_at": None,
                    "updated_at": None
                })
                continue

            if not isinstance(item, dict):
                continue

            memory_id = item.get("id") or item.get("memory_id") or item.get("uuid")
            memory_text = item.get("memory") or item.get("text") or item.get("content") or ""
            metadata = item.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}

            normalized.append({
                "id": str(memory_id) if memory_id is not None else "",
                "memory": str(memory_text).strip(),
                "metadata": metadata,
                "created_at": item.get("created_at") or item.get("createdAt"),
                "updated_at": item.get("updated_at") or item.get("updatedAt"),
                "score": item.get("score")
            })

        return [item for item in normalized if item["id"] and item["memory"]]

    def _log_background_error(self, task: asyncio.Task) -> None:
        try:
            task.result()
        except Exception as exc:
            logger.warning("Background mem0 user memory write failed: %s", exc)


user_memory_service = UserMemoryService()
