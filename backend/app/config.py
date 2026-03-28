from pydantic_settings import BaseSettings
from typing import Optional, List, Dict


class Settings(BaseSettings):
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # AI模型配置
    OPENAI_API_KEY: str = "sk-3e63a0bd10724616af4b6cc7711283c2"
    OPENAI_API_BASE: Optional[str] = "https://api.deepseek.com"
    # 支持 OPENAI_BASE_URL 作为 OPENAI_API_BASE 的别名
    OPENAI_BASE_URL: Optional[str] = None
    MODEL_NAME: str = "deepseek-chat"

    # 嵌入模型配置
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_API_BASE: Optional[str] = None

    # 重排序模型配置
    RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANK_API_KEY: Optional[str] = None
    RERANK_API_BASE: Optional[str] = None

    # 网络搜索配置
    SEARCH_API_KEY: Optional[str] = "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"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./rag.db"

    # ChromaDB配置
    CHROMA_DB_PATH: str = "./chroma_db"

    # 文本分块配置
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Agent配置
    AGENT_MAX_ITERATIONS: int = 10  # Agent最大迭代次数
    AGENT_VERBOSE: bool = False     # 是否输出详细日志

    # JWT认证配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MCP服务器配置
    # 示例配置格式:
    # MCP_SERVERS = [
    #     {
    #         "name": "filesystem",
    #         "transport": "stdio",
    #         "command": "python",
    #         "args": ["/path/to/filesystem_server.py"]
    #     },
    #     {
    #         "name": "database",
    #         "transport": "http",
    #         "url": "http://localhost:8001/mcp"
    #     }
    # ]
    MCP_SERVERS: List[Dict] = []  # MCP服务器配置列表

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果设置了 OPENAI_BASE_URL，使用它作为 OPENAI_API_BASE
        if self.OPENAI_BASE_URL and not self.OPENAI_API_BASE:
            self.OPENAI_API_BASE = self.OPENAI_BASE_URL

    class Config:
        env_file = ".env"
        extra = "ignore"  # 允许额外的环境变量


settings = Settings()
