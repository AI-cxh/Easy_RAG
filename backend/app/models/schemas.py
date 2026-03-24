from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# KnowledgeBase Schemas
class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="知识库名称")
    description: Optional[str] = None
    chunk_size: Optional[int] = Field(default=1000, ge=100, le=10000, description="分块大小")
    chunk_overlap: Optional[int] = Field(default=200, ge=0, le=2000, description="分块重叠")


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    chunk_size: int = 1000
    chunk_overlap: int = 200
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBaseWithDocuments(KnowledgeBaseResponse):
    documents: List["DocumentResponse"] = []

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    kb_id: int
    filename: str
    file_path: str
    file_size: Optional[int]
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


# Chat Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: Optional[int] = None
    kb_ids: List[int] = Field(default_factory=list, description="选择的KnowledgeBase ID列表")
    use_web_search: bool = False
    session_type: str = Field(default="rag", description="会话类型: rag, agentic, multi_agent")


class ChatResponse(BaseModel):
    response: str
    session_id: int
    sources: Optional[List[str]] = None
    search_results: Optional[List[dict]] = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime
    # 可选的metadata字段
    sources: Optional[List[str]] = None
    search_results: Optional[List[dict]] = None
    thinking_steps: Optional[List[dict]] = None
    # 多Agent执行流程数据
    agent_plan: Optional[List[dict]] = None
    agent_logs: Optional[List[dict]] = None
    completed_tasks: Optional[List[str]] = None
    current_task_id: Optional[str] = None

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    session_type: str = "rag"  # rag, agentic, multi_agent
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]


class SessionRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="会话标题")


class KnowledgeBaseRenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="知识库名称")
    description: Optional[str] = None
    chunk_size: Optional[int] = Field(default=None, ge=100, le=10000, description="分块大小")
    chunk_overlap: Optional[int] = Field(default=None, ge=0, le=2000, description="分块重叠")


# Agent Chat Schemas
class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: Optional[int] = None
    kb_ids: Optional[List[int]] = Field(default=None, description="可选的知识库ID列表，Agent可自主选择")
    use_web_search: bool = True
    show_thinking: bool = True  # 是否展示思考过程


class AgentStepResponse(BaseModel):
    type: str  # "thought" | "tool_call" | "tool_result" | "answer" | "error"
    content: str
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None


# Update forward references
KnowledgeBaseWithDocuments.model_rebuild()


# Agent Schemas
class AgentConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Agent名称")
    type: str = Field(..., description="Agent类型: retrieval/analysis/writing/custom")
    description: Optional[str] = Field(None, description="Agent描述")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    tools: Optional[List[str]] = Field(default_factory=list, description="工具列表")
    model_name: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2, description="温度参数")


class AgentConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Agent名称")
    description: Optional[str] = Field(None, description="Agent描述")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    tools: Optional[List[str]] = Field(None, description="工具列表")
    model_name: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="温度参数")
    is_active: Optional[bool] = Field(None, description="是否启用")


class AgentConfigResponse(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str]
    system_prompt: Optional[str]
    tools: List[str] = []
    model_name: Optional[str]
    temperature: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AgentExecutionResponse(BaseModel):
    id: int
    session_id: int
    agent_name: str
    agent_type: str
    task: str
    input_context: Optional[str]
    output: Optional[str]
    status: str
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Multi-Agent Chat Schemas
class MultiAgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: Optional[int] = None
    kb_ids: Optional[List[int]] = Field(default=None, description="可选的知识库ID列表")
    use_web_search: bool = True
    show_process: bool = True  # 是否展示执行过程


class AgentTaskEvent(BaseModel):
    type: str  # planning/plan/task_start/task_complete/analysis/answer/error/result
    task_id: Optional[str] = None
    agent_type: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    tasks: Optional[List[dict]] = None
