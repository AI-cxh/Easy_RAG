from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    from app.models.models import KnowledgeBase, Document, ChatSession, ChatMessage
    Base.metadata.create_all(bind=engine)

    # 迁移：为 chat_messages 表添加 extra_data 列（如果不存在）
    if "sqlite" in settings.DATABASE_URL:
        with engine.connect() as conn:
            # 检查列是否存在
            result = conn.execute(text("PRAGMA table_info(chat_messages)"))
            columns = [row[1] for row in result.fetchall()]
            if 'extra_data' not in columns:
                conn.execute(text("ALTER TABLE chat_messages ADD COLUMN extra_data TEXT"))
                conn.commit()

            # 为 knowledge_bases 表添加分块设置列
            result = conn.execute(text("PRAGMA table_info(knowledge_bases)"))
            kb_columns = [row[1] for row in result.fetchall()]
            if 'chunk_size' not in kb_columns:
                conn.execute(text("ALTER TABLE knowledge_bases ADD COLUMN chunk_size INTEGER DEFAULT 1000"))
                conn.commit()
            if 'chunk_overlap' not in kb_columns:
                conn.execute(text("ALTER TABLE knowledge_bases ADD COLUMN chunk_overlap INTEGER DEFAULT 200"))
                conn.commit()

            # 为 chat_sessions 表添加 session_type 列
            result = conn.execute(text("PRAGMA table_info(chat_sessions)"))
            session_columns = [row[1] for row in result.fetchall()]
            if 'session_type' not in session_columns:
                conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN session_type VARCHAR(20) DEFAULT 'rag'"))
                conn.commit()
