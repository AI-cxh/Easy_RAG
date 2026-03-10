from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # AI模型配置
    OPENAI_API_KEY: str = "your_api_key"
    OPENAI_API_BASE: Optional[str] = "http://localhost:11434/v1"
    # 支持 OPENAI_BASE_URL 作为 OPENAI_API_BASE 的别名
    OPENAI_BASE_URL: Optional[str] = None
    MODEL_NAME: str = "gpt-4o-mini"

    # 嵌入模型配置
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 网络搜索配置
    SEARCH_API_KEY: Optional[str] = None

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./rag.db"

    # ChromaDB配置
    CHROMA_DB_PATH: str = "./chroma_db"

    # 文本分块配置
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果设置了 OPENAI_BASE_URL，使用它作为 OPENAI_API_BASE
        if self.OPENAI_BASE_URL and not self.OPENAI_API_BASE:
            self.OPENAI_API_BASE = self.OPENAI_BASE_URL

    class Config:
        env_file = ".env"
        extra = "ignore"  # 允许额外的环境变量


settings = Settings()
