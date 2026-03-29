from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class AdminInit(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


# Admin User Management Schemas
class AdminUserCreate(BaseModel):
    """管理员创建用户"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: str = Field(default="user", description="角色: admin/user")
    status: str = Field(default="approved", description="状态: pending/approved/rejected")


class AdminUserUpdate(BaseModel):
    """管理员更新用户信息"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    role: Optional[str] = Field(None, description="角色: admin/user")
    status: Optional[str] = Field(None, description="状态: pending/approved/rejected")


class AdminPasswordReset(BaseModel):
    """管理员重置用户密码"""
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UserStatsResponse(BaseModel):
    """用户统计信息"""
    kb_count: int = 0
    doc_count: int = 0
    chunk_count: int = 0


class UserDetailResponse(UserResponse):
    """用户详情，包含统计信息"""
    stats: UserStatsResponse = UserStatsResponse()


# KnowledgeBase Schemas
class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="知识库名称")
    description: Optional[str] = None
    chunk_size: Optional[int] = Field(default=1000, ge=100, le=10000, description="分块大小")
    chunk_overlap: Optional[int] = Field(default=200, ge=0, le=2000, description="分块重叠")
    embedding_model: Optional[str] = Field(default="text-embedding-ada-002", description="Embedding模型")
    owner: Optional[str] = Field(default="", max_length=100, description="负责人")


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "text-embedding-ada-002"
    owner: str = ""
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeBaseListItem(BaseModel):
    """知识库列表项，包含文档数量"""
    id: int
    name: str
    description: Optional[str]
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "text-embedding-ada-002"
    owner: str = ""
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    doc_count: int = 0

    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(BaseModel):
    items: List[KnowledgeBaseListItem]
    total: int
    page: int
    page_size: int


class KnowledgeBaseStatsResponse(BaseModel):
    total_kbs: int
    total_docs: int
    kbs_with_docs: int


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
    file_type: str = ""
    chunk_count: int
    source: str = "upload"
    processing_mode: str = "auto"
    status: str = "completed"
    enabled: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentUpdateRequest(BaseModel):
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    source: Optional[str] = Field(None, max_length=100)
    enabled: Optional[bool] = None


# Chunk Schemas
class ChunkResponse(BaseModel):
    id: int
    doc_id: int
    content: str
    char_count: int
    token_count: int
    enabled: bool
    sort_order: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChunkListResponse(BaseModel):
    items: List[ChunkResponse]
    total: int
    page: int
    page_size: int


class ChunkCreate(BaseModel):
    content: str = Field(..., min_length=1, description="分块内容")


class ChunkUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    enabled: Optional[bool] = None


class ChunkBatchRequest(BaseModel):
    chunk_ids: List[int] = Field(..., min_items=1, description="分块ID列表")


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
    user_id: Optional[int] = None
    username: Optional[str] = None  # 用户名，用于管理员区分
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
    embedding_model: Optional[str] = Field(default=None, max_length=255, description="Embedding模型")
    owner: Optional[str] = Field(default=None, max_length=100, description="负责人")


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
