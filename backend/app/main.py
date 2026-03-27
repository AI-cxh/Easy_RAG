"""FastAPI应用主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.config import settings
from app.models.database import init_db
from app.api import chat, knowledge, upload, app_settings as settings_api, mcp, agents, chunks
from app.services.mcp_client import mcp_client
from app.services.agent import agent_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("Initializing application...")

    # 初始化数据库
    init_db()

    # 确保必要的目录存在
    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)

    # 初始化MCP客户端（从配置文件加载）
    logger.info("Initializing MCP client...")
    await mcp_client.initialize()

    # 初始化Agent服务（加载MCP工具）
    logger.info("Initializing Agent service...")
    await agent_service.initialize()

    logger.info("Application started successfully")

    yield

    # 关闭时清理
    logger.info("Shutting down application...")
    await mcp_client.close()
    logger.info("Application shutdown complete")


# 创建FastAPI应用
app = FastAPI(
    title="Easy RAG API",
    description="简单的RAG（检索增强生成）应用API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api", tags=["聊天"])
app.include_router(knowledge.router, prefix="/api", tags=["知识库"])
app.include_router(upload.router, prefix="/api", tags=["文件上传"])
app.include_router(chunks.router, prefix="/api", tags=["分块管理"])
app.include_router(settings_api.router, prefix="/api", tags=["设置"])
app.include_router(mcp.router, prefix="/api", tags=["MCP"])
app.include_router(agents.router, prefix="/api", tags=["Agent"])


# 健康检查
@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {
        "message": "Easy RAG API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
