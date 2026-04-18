"""记忆服务：管理项目记忆和会话摘要记忆。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import logging
import re

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import ChatMessage, ProjectMemory, SessionMemory
from app.models.schemas import SessionMemoryResponse

logger = logging.getLogger(__name__)


class MemoryService:
    """统一处理项目记忆与会话摘要。"""

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

    def build_project_memory_context(self, db: Session, project_id: Optional[int]) -> str:
        """构建项目级记忆上下文。"""
        if not project_id:
            return ""

        memories = db.query(ProjectMemory).filter(
            ProjectMemory.project_id == project_id,
            ProjectMemory.enabled == True
        ).order_by(ProjectMemory.pinned.desc(), ProjectMemory.created_at.asc()).all()

        if not memories:
            return ""

        lines = ["当前项目背景："]
        for memory in memories:
            lines.append(f"- [{memory.memory_type}] {memory.content}")
        return "\n".join(lines)

    def get_session_memory(self, db: Session, session_id: int) -> Optional[SessionMemory]:
        """获取会话摘要记忆。"""
        return db.query(SessionMemory).filter(SessionMemory.session_id == session_id).first()

    def build_session_memory_context(self, session_memory: Optional[SessionMemory]) -> str:
        """把会话摘要记忆格式化为 prompt 上下文。"""
        if not session_memory or not session_memory.summary.strip():
            return ""

        lines = ["当前会话摘要：", session_memory.summary.strip()]

        if session_memory.user_goal:
            lines.append(f"用户当前目标：{session_memory.user_goal.strip()}")

        constraints = self._parse_json_list(session_memory.constraints)
        if constraints:
            lines.append("当前约束：")
            lines.extend([f"- {item}" for item in constraints])

        open_tasks = self._parse_json_list(session_memory.open_tasks)
        if open_tasks:
            lines.append("待完成事项：")
            lines.extend([f"- {item}" for item in open_tasks])

        key_facts = self._parse_json_list(session_memory.key_facts)
        if key_facts:
            lines.append("关键事实：")
            lines.extend([f"- {item}" for item in key_facts])

        return "\n".join(lines)

    def trim_chat_history(self, history: List[Dict[str, str]], keep_last: int = 6) -> List[Dict[str, str]]:
        """仅保留最近几条原始消息，其余交给会话摘要。"""
        if keep_last <= 0:
            return []
        return history[-keep_last:]

    def should_refresh_session_memory(
        self,
        session_memory: Optional[SessionMemory],
        messages: List[ChatMessage],
        keep_recent: int = 6
    ) -> bool:
        """判断是否需要刷新会话摘要。"""
        summarizable_count = max(len(messages) - keep_recent, 0)
        if summarizable_count <= 0:
            return False
        if not session_memory:
            return len(messages) >= keep_recent + 2
        return summarizable_count >= session_memory.source_message_count + 4

    def refresh_session_memory(
        self,
        db: Session,
        session_id: int,
        messages: List[ChatMessage],
        force: bool = False,
        keep_recent: int = 6
    ) -> Optional[SessionMemory]:
        """刷新会话摘要记忆。"""
        if not messages:
            return self.get_session_memory(db, session_id)

        summarizable_messages = self._select_messages_for_summary(messages, force=force, keep_recent=keep_recent)
        if not summarizable_messages:
            return self.get_session_memory(db, session_id)

        payload = self._summarize_messages(summarizable_messages)
        session_memory = self.get_session_memory(db, session_id)

        if session_memory is None:
            session_memory = SessionMemory(
                session_id=session_id,
                summary=payload["summary"],
                user_goal=payload.get("user_goal"),
                constraints=self._dump_json_list(payload.get("constraints")),
                open_tasks=self._dump_json_list(payload.get("open_tasks")),
                key_facts=self._dump_json_list(payload.get("key_facts")),
                source_message_count=len(summarizable_messages),
                version=1
            )
            db.add(session_memory)
        else:
            session_memory.summary = payload["summary"]
            session_memory.user_goal = payload.get("user_goal")
            session_memory.constraints = self._dump_json_list(payload.get("constraints"))
            session_memory.open_tasks = self._dump_json_list(payload.get("open_tasks"))
            session_memory.key_facts = self._dump_json_list(payload.get("key_facts"))
            session_memory.source_message_count = len(summarizable_messages)
            session_memory.version += 1

        db.commit()
        db.refresh(session_memory)
        return session_memory

    def to_response(self, session_memory: SessionMemory) -> SessionMemoryResponse:
        """将 ORM 模型转换为 API 响应。"""
        return SessionMemoryResponse(
            id=session_memory.id,
            session_id=session_memory.session_id,
            summary=session_memory.summary,
            user_goal=session_memory.user_goal,
            constraints=self._parse_json_list(session_memory.constraints),
            open_tasks=self._parse_json_list(session_memory.open_tasks),
            key_facts=self._parse_json_list(session_memory.key_facts),
            source_message_count=session_memory.source_message_count,
            version=session_memory.version,
            created_at=session_memory.created_at,
            updated_at=session_memory.updated_at
        )

    def _select_messages_for_summary(
        self,
        messages: List[ChatMessage],
        force: bool,
        keep_recent: int
    ) -> List[ChatMessage]:
        if force:
            if len(messages) <= keep_recent:
                return messages
            return messages[:-max(keep_recent // 2, 1)]

        if len(messages) <= keep_recent:
            return []
        return messages[:-keep_recent]

    def _summarize_messages(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        transcript = self._build_transcript(messages)
        system_prompt = (
            "你负责把多轮对话压缩成稳定的会话记忆。"
            "只保留后续回答仍然需要的信息，不要编造。"
            "输出必须是 JSON 对象，包含字段："
            "summary(string), user_goal(string|null), constraints(string[]), "
            "open_tasks(string[]), key_facts(string[])。"
        )
        human_prompt = (
            "请总结下面的对话，压缩成供后续模型使用的会话记忆。\n"
            "要求：summary 不超过 220 个中文字符；列表项每项一句话。\n\n"
            f"{transcript}"
        )

        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            parsed = self._parse_summary_response(response.content if hasattr(response, "content") else "")
            if parsed["summary"]:
                return parsed
        except Exception as exc:
            logger.warning("Failed to summarize session memory: %s", exc)

        return self._build_fallback_summary(messages)

    def _parse_summary_response(self, content: str) -> Dict[str, Any]:
        if not content:
            return self._empty_summary_payload()

        content = content.strip()
        fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.S)
        if fenced_match:
            content = fenced_match.group(1)

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return self._empty_summary_payload()

        return {
            "summary": str(data.get("summary") or "").strip(),
            "user_goal": self._normalize_optional_text(data.get("user_goal")),
            "constraints": self._normalize_list(data.get("constraints")),
            "open_tasks": self._normalize_list(data.get("open_tasks")),
            "key_facts": self._normalize_list(data.get("key_facts"))
        }

    def _build_fallback_summary(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        user_messages = [msg.content.strip() for msg in messages if msg.role == "user" and msg.content.strip()]
        assistant_messages = [msg.content.strip() for msg in messages if msg.role == "assistant" and msg.content.strip()]

        summary_parts: List[str] = []
        if user_messages:
            summary_parts.append(f"用户最近主要在讨论：{user_messages[-1][:120]}")
        if len(user_messages) >= 2:
            summary_parts.append(f"此前还提到：{user_messages[-2][:80]}")
        if assistant_messages:
            summary_parts.append(f"系统已给出过阶段性回答：{assistant_messages[-1][:120]}")

        return {
            "summary": "；".join(summary_parts)[:220] or "会话已有多轮上下文，请结合最近消息继续回答。",
            "user_goal": user_messages[-1][:120] if user_messages else None,
            "constraints": [],
            "open_tasks": [],
            "key_facts": []
        }

    def _build_transcript(self, messages: List[ChatMessage]) -> str:
        lines = []
        for msg in messages:
            role = "用户" if msg.role == "user" else "助手"
            lines.append(f"{role}: {msg.content.strip()}")
        return "\n".join(lines)

    def _empty_summary_payload(self) -> Dict[str, Any]:
        return {
            "summary": "",
            "user_goal": None,
            "constraints": [],
            "open_tasks": [],
            "key_facts": []
        }

    def _normalize_optional_text(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _normalize_list(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        items = []
        for item in value:
            text = str(item).strip()
            if text:
                items.append(text)
        return items[:8]

    def _parse_json_list(self, raw_value: Optional[str]) -> List[str]:
        if not raw_value:
            return []
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            return []
        return self._normalize_list(value)

    def _dump_json_list(self, items: Optional[List[str]]) -> str:
        return json.dumps(self._normalize_list(items), ensure_ascii=False)


memory_service = MemoryService()
