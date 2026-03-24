from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


class KnowledgeBase(Base):
    """知识库模型"""
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    # 分块设置
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")


class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="新对话")
    session_type = Column(String(20), default="rag")  # rag, agentic, multi_agent
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    # 存储额外数据：thinking_steps, sources, search_results
    extra_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    session = relationship("ChatSession", back_populates="messages")


class AgentConfig(Base):
    """Agent配置模型"""
    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # retrieval/analysis/writing/custom
    description = Column(Text)
    system_prompt = Column(Text)
    tools = Column(Text)  # JSON格式的工具配置
    model_name = Column(String(255))
    temperature = Column(Integer, default=70)  # 存储为整数(0-100)，使用时除以100
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AgentExecution(Base):
    """Agent执行记录模型"""
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False)
    task = Column(Text, nullable=False)
    input_context = Column(Text)  # JSON格式的输入上下文
    output = Column(Text)
    status = Column(String(50), default="pending")  # pending/running/completed/failed
    error = Column(Text)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # 关系
    session = relationship("ChatSession")
