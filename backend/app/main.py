"""FastAPI应用主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.models.database import init_db
from app.api import chat, knowledge, upload

# 创建FastAPI应用
app = FastAPI(
    title="Easy RAG API",
    description="简单的RAG（检索增强生成）应用API",
    version="1.0.0"
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

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()

    # 确保必要的目录存在
    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)


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
