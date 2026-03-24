"""Agent管理API"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import json

from app.models.database import SessionLocal
from app.models.models import AgentConfig, AgentExecution
from app.models.schemas import (
    AgentConfigCreate,
    AgentConfigUpdate,
    AgentConfigResponse,
    AgentExecutionResponse,
    MultiAgentChatRequest,
    AgentTaskEvent
)
from app.services.multi_agent import (
    OrchestratorAgent,
    RetrievalAgent,
    AnalysisAgent,
    WritingAgent,
    CustomAgent,
    agent_registry,
    AgentType
)

router = APIRouter()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Agent配置管理 ====================

@router.get("/agents", response_model=List[AgentConfigResponse])
async def list_agents(db: Session = Depends(get_db)):
    """获取所有Agent配置"""
    agents = db.query(AgentConfig).all()
    result = []
    for agent in agents:
        tools = json.loads(agent.tools) if agent.tools else []
        result.append(AgentConfigResponse(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            description=agent.description,
            system_prompt=agent.system_prompt,
            tools=tools,
            model_name=agent.model_name,
            temperature=agent.temperature / 100.0 if agent.temperature else 0.7,
            is_active=agent.is_active,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        ))
    return result


@router.post("/agents", response_model=AgentConfigResponse)
async def create_agent(config: AgentConfigCreate, db: Session = Depends(get_db)):
    """创建自定义Agent"""
    # 检查名称是否已存在
    existing = db.query(AgentConfig).filter(AgentConfig.name == config.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent名称已存在")

    # 创建配置
    agent_config = AgentConfig(
        name=config.name,
        type=config.type,
        description=config.description,
        system_prompt=config.system_prompt,
        tools=json.dumps(config.tools),
        model_name=config.model_name,
        temperature=int(config.temperature * 100),
        is_active=True
    )

    db.add(agent_config)
    db.commit()
    db.refresh(agent_config)

    return AgentConfigResponse(
        id=agent_config.id,
        name=agent_config.name,
        type=agent_config.type,
        description=agent_config.description,
        system_prompt=agent_config.system_prompt,
        tools=config.tools,
        model_name=agent_config.model_name,
        temperature=config.temperature,
        is_active=agent_config.is_active,
        created_at=agent_config.created_at,
        updated_at=agent_config.updated_at
    )


@router.get("/agents/{agent_id}", response_model=AgentConfigResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """获取单个Agent配置"""
    agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")

    tools = json.loads(agent.tools) if agent.tools else []
    return AgentConfigResponse(
        id=agent.id,
        name=agent.name,
        type=agent.type,
        description=agent.description,
        system_prompt=agent.system_prompt,
        tools=tools,
        model_name=agent.model_name,
        temperature=agent.temperature / 100.0 if agent.temperature else 0.7,
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )


@router.put("/agents/{agent_id}", response_model=AgentConfigResponse)
async def update_agent(
    agent_id: int,
    config: AgentConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新Agent配置"""
    agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")

    # 更新字段
    if config.name is not None:
        # 检查名称是否已被其他Agent使用
        existing = db.query(AgentConfig).filter(
            AgentConfig.name == config.name,
            AgentConfig.id != agent_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Agent名称已存在")
        agent.name = config.name

    if config.description is not None:
        agent.description = config.description
    if config.system_prompt is not None:
        agent.system_prompt = config.system_prompt
    if config.tools is not None:
        agent.tools = json.dumps(config.tools)
    if config.model_name is not None:
        agent.model_name = config.model_name
    if config.temperature is not None:
        agent.temperature = int(config.temperature * 100)
    if config.is_active is not None:
        agent.is_active = config.is_active

    db.commit()
    db.refresh(agent)

    tools = json.loads(agent.tools) if agent.tools else []
    return AgentConfigResponse(
        id=agent.id,
        name=agent.name,
        type=agent.type,
        description=agent.description,
        system_prompt=agent.system_prompt,
        tools=tools,
        model_name=agent.model_name,
        temperature=agent.temperature / 100.0 if agent.temperature else 0.7,
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """删除Agent"""
    agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")

    db.delete(agent)
    db.commit()
    return {"message": "Agent已删除"}


# ==================== Agent执行记录 ====================

@router.get("/agents/executions/{session_id}", response_model=List[AgentExecutionResponse])
async def get_session_executions(session_id: int, db: Session = Depends(get_db)):
    """获取会话的Agent执行记录"""
    executions = db.query(AgentExecution).filter(
        AgentExecution.session_id == session_id
    ).order_by(AgentExecution.started_at).all()

    return [
        AgentExecutionResponse(
            id=e.id,
            session_id=e.session_id,
            agent_name=e.agent_name,
            agent_type=e.agent_type,
            task=e.task,
            input_context=e.input_context,
            output=e.output,
            status=e.status,
            error=e.error,
            started_at=e.started_at,
            completed_at=e.completed_at
        )
        for e in executions
    ]


# ==================== 多Agent聊天 ====================

@router.post("/chat/multi-agent")
async def multi_agent_chat(
    request: MultiAgentChatRequest,
    db: Session = Depends(get_db)
):
    """
    多Agent协同聊天（流式响应）

    返回SSE流，事件类型包括：
    - planning: 正在规划
    - plan: 执行计划
    - task_start: 任务开始
    - task_complete: 任务完成
    - thought: 思考过程
    - tool_call: 工具调用
    - tool_result: 工具结果
    - analysis: 分析内容
    - answer: 最终回答
    - error: 错误
    - done: 完成
    """
    from fastapi.responses import StreamingResponse
    from app.models.models import ChatSession, ChatMessage
    from datetime import datetime
    import json

    async def generate():
        # 获取或创建会话
        session = None
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()

        if not session:
            session = ChatSession(
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                session_type="multi_agent"
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # 保存用户消息
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()

        # 获取聊天历史
        history_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()

        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages[-6:]  # 最近3轮对话
        ]

        # 注册专业Agent - 先清空再注册
        agent_registry.clear()
        agent_registry.register(RetrievalAgent(kb_ids=request.kb_ids, use_web_search=request.use_web_search))
        agent_registry.register(AnalysisAgent())
        agent_registry.register(WritingAgent())

        # 加载自定义Agent
        custom_agents = db.query(AgentConfig).filter(
            AgentConfig.is_active == True,
            AgentConfig.type == "custom"
        ).all()

        for config in custom_agents:
            custom_agent = CustomAgent(
                name=config.name,
                description=config.description or "",
                system_prompt=config.system_prompt,
                model_name=config.model_name,
                temperature=config.temperature / 100.0 if config.temperature else 0.7
            )
            agent_registry.register(custom_agent)

        # 初始化Agent - 在注册完成后创建
        orchestrator = OrchestratorAgent(agent_registry=agent_registry)

        # 构建上下文
        context = {
            "kb_ids": request.kb_ids or [],
            "use_web_search": request.use_web_search,
            "original_query": request.message,
            "sources": [],
            "search_results": []
        }

        # 创建任务
        from app.services.multi_agent.base_agent import AgentTask
        task = AgentTask(
            id="main_task",
            description=request.message,
            agent_type=AgentType.ORCHESTRATOR
        )

        # 执行并流式返回
        full_response = ""
        all_sources = []
        all_search_results = []
        # 收集多Agent执行流程数据
        agent_plan = []
        agent_logs = []
        completed_tasks = []
        current_task_id = None

        try:
            async for event in orchestrator.stream_execute(task, context):
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"data: {event_data}\n\n"

                # 收集结果
                if event.get("type") == "answer":
                    full_response += event.get("content", "")
                if event.get("type") == "result":
                    result = event.get("result")
                    if result:
                        # result 现在是字典
                        if result.get("sources"):
                            all_sources.extend(result["sources"])
                        if result.get("search_results"):
                            all_search_results.extend(result["search_results"])

                # 收集多Agent执行流程数据
                if event.get("type") == "plan":
                    agent_plan = event.get("tasks", [])
                elif event.get("type") == "planning":
                    agent_logs.append({
                        "type": "thought",
                        "content": event.get("content", "")
                    })
                elif event.get("type") == "task_start":
                    current_task_id = event.get("task_id")
                    agent_logs.append({
                        "type": "thought",
                        "content": f"开始执行: {event.get('description', '')}"
                    })
                elif event.get("type") == "task_complete":
                    if event.get("task_id"):
                        completed_tasks.append(event.get("task_id"))
                    current_task_id = None
                elif event.get("type") == "thought":
                    agent_logs.append({
                        "type": "thought",
                        "content": event.get("content", "")
                    })
                elif event.get("type") == "tool_call":
                    agent_logs.append({
                        "type": "tool_call",
                        "content": event.get("content", ""),
                        "tool_name": event.get("tool_name")
                    })
                elif event.get("type") == "tool_result":
                    agent_logs.append({
                        "type": "tool_result",
                        "content": event.get("content", ""),
                        "tool_name": event.get("tool_name")
                    })

        except Exception as e:
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            error_event = json.dumps({"type": "error", "content": error_detail}, ensure_ascii=False)
            yield f"data: {error_event}\n\n"

        # 保存助手消息
        extra_data = {}
        if all_sources:
            extra_data["sources"] = list(set(all_sources))
        if all_search_results:
            extra_data["search_results"] = all_search_results
        # 保存多Agent执行流程数据
        if agent_plan:
            extra_data["agent_plan"] = agent_plan
        if agent_logs:
            extra_data["agent_logs"] = agent_logs
        if completed_tasks:
            extra_data["completed_tasks"] = completed_tasks

        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=full_response,
            extra_data=json.dumps(extra_data) if extra_data else None
        )
        db.add(assistant_message)
        db.commit()

        # 发送完成事件
        done_event = json.dumps({
            "type": "done",
            "session_id": session.id,
            "sources": list(set(all_sources)) if all_sources else None,
            "search_results": all_search_results if all_search_results else None
        }, ensure_ascii=False)
        yield f"data: {done_event}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ==================== Agent类型列表 ====================

@router.get("/agents/types/list")
async def get_agent_types():
    """获取可用的Agent类型"""
    return [
        {"value": "retrieval", "label": "检索Agent", "description": "负责从知识库和网络搜索相关信息"},
        {"value": "analysis", "label": "分析Agent", "description": "负责深度分析和推理"},
        {"value": "writing", "label": "写作Agent", "description": "负责组织语言生成最终回答"},
        {"value": "custom", "label": "自定义Agent", "description": "用户自定义的通用Agent"}
    ]
