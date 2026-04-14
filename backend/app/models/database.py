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
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

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
    from app.models.models import KnowledgeBase, Document, ChatSession, ChatMessage, User
    Base.metadata.create_all(bind=engine)

    if "sqlite" in settings.DATABASE_URL:
        with engine.connect() as conn:
            # 迁移：让 chat_sessions 使用 AUTOINCREMENT，避免删除尾部会话后复用主键
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='chat_sessions'"))
            chat_sessions_sql = result.scalar()
            if chat_sessions_sql and "AUTOINCREMENT" not in chat_sessions_sql.upper():
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                conn.execute(text("""
                    CREATE TABLE chat_sessions_new (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(255) NOT NULL,
                        session_type VARCHAR(20) DEFAULT 'rag',
                        user_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users (id)
                    )
                """))
                conn.execute(text("""
                    INSERT INTO chat_sessions_new (id, title, session_type, user_id, created_at)
                    SELECT id, title, session_type, user_id, created_at
                    FROM chat_sessions
                    ORDER BY id
                """))
                conn.execute(text("DROP TABLE chat_sessions"))
                conn.execute(text("ALTER TABLE chat_sessions_new RENAME TO chat_sessions"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chat_sessions_id ON chat_sessions (id)"))
                conn.execute(text("PRAGMA foreign_keys=ON"))
                conn.commit()

            # 迁移：让 chat_messages 使用 AUTOINCREMENT，避免删除尾部消息后复用主键
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='chat_messages'"))
            chat_messages_sql = result.scalar()
            if chat_messages_sql and "AUTOINCREMENT" not in chat_messages_sql.upper():
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                conn.execute(text("""
                    CREATE TABLE chat_messages_new (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        extra_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
                    )
                """))
                conn.execute(text("""
                    INSERT INTO chat_messages_new (id, session_id, role, content, extra_data, created_at)
                    SELECT id, session_id, role, content, extra_data, created_at
                    FROM chat_messages
                    ORDER BY id
                """))
                conn.execute(text("DROP TABLE chat_messages"))
                conn.execute(text("ALTER TABLE chat_messages_new RENAME TO chat_messages"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chat_messages_id ON chat_messages (id)"))
                conn.execute(text("PRAGMA foreign_keys=ON"))
                conn.commit()

            # 迁移：让 agent_executions 使用 AUTOINCREMENT，避免删除记录后复用主键
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='agent_executions'"))
            agent_executions_sql = result.scalar()
            if agent_executions_sql and "AUTOINCREMENT" not in agent_executions_sql.upper():
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                conn.execute(text("""
                    CREATE TABLE agent_executions_new (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        agent_name VARCHAR(255) NOT NULL,
                        agent_type VARCHAR(50) NOT NULL,
                        task TEXT NOT NULL,
                        input_context TEXT,
                        output TEXT,
                        status VARCHAR(50) DEFAULT 'pending',
                        error TEXT,
                        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        completed_at DATETIME,
                        FOREIGN KEY(session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
                    )
                """))
                conn.execute(text("""
                    INSERT INTO agent_executions_new (
                        id, session_id, agent_name, agent_type, task, input_context,
                        output, status, error, started_at, completed_at
                    )
                    SELECT
                        id, session_id, agent_name, agent_type, task, input_context,
                        output, status, error, started_at, completed_at
                    FROM agent_executions
                    ORDER BY id
                """))
                conn.execute(text("DROP TABLE agent_executions"))
                conn.execute(text("ALTER TABLE agent_executions_new RENAME TO agent_executions"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_agent_executions_id ON agent_executions (id)"))
                conn.execute(text("PRAGMA foreign_keys=ON"))
                conn.commit()

            # 迁移：为 chat_messages 表添加 extra_data 列（如果不存在）
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

            # 为 chat_sessions 表添加 user_id 列
            if 'user_id' not in session_columns:
                conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER"))
                conn.commit()

            # 为 knowledge_bases 表添加 user_id 列
            result = conn.execute(text("PRAGMA table_info(knowledge_bases)"))
            kb_columns = [row[1] for row in result.fetchall()]
            if 'user_id' not in kb_columns:
                conn.execute(text("ALTER TABLE knowledge_bases ADD COLUMN user_id INTEGER"))
                conn.commit()
