"""
数据库迁移脚本：添加新字段到现有表

使用方法：
    cd backend
    python scripts/migrate_db.py
"""
import sqlite3
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


def get_db_path():
    """获取数据库文件路径"""
    return settings.DATABASE_URL.replace('sqlite:///', '')


def migrate_database():
    """执行数据库迁移"""
    db_path = get_db_path()
    print(f"数据库路径: {db_path}")

    if not os.path.exists(db_path):
        print("数据库文件不存在，将在启动时自动创建")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 获取现有表结构
        def get_columns(table_name):
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [row[1] for row in cursor.fetchall()]

        # 添加 knowledge_bases 表的新列
        kb_columns = get_columns('knowledge_bases')
        print(f"knowledge_bases 现有列: {kb_columns}")

        if 'embedding_model' not in kb_columns:
            print("添加 embedding_model 列...")
            cursor.execute("ALTER TABLE knowledge_bases ADD COLUMN embedding_model VARCHAR(255) DEFAULT 'text-embedding-ada-002'")

        if 'owner' not in kb_columns:
            print("添加 owner 列...")
            cursor.execute("ALTER TABLE knowledge_bases ADD COLUMN owner VARCHAR(100) DEFAULT ''")

        if 'updated_at' not in kb_columns:
            print("添加 updated_at 列...")
            cursor.execute("ALTER TABLE knowledge_bases ADD COLUMN updated_at DATETIME")

        # 添加 documents 表的新列
        doc_columns = get_columns('documents')
        print(f"documents 现有列: {doc_columns}")

        if 'file_type' not in doc_columns:
            print("添加 file_type 列...")
            cursor.execute("ALTER TABLE documents ADD COLUMN file_type VARCHAR(20) DEFAULT ''")

        if 'source' not in doc_columns:
            print("添加 source 列...")
            cursor.execute("ALTER TABLE documents ADD COLUMN source VARCHAR(100) DEFAULT 'upload'")

        if 'processing_mode' not in doc_columns:
            print("添加 processing_mode 列...")
            cursor.execute("ALTER TABLE documents ADD COLUMN processing_mode VARCHAR(50) DEFAULT 'auto'")

        if 'status' not in doc_columns:
            print("添加 status 列...")
            cursor.execute("ALTER TABLE documents ADD COLUMN status VARCHAR(20) DEFAULT 'completed'")

        if 'enabled' not in doc_columns:
            print("添加 enabled 列...")
            cursor.execute("ALTER TABLE documents ADD COLUMN enabled BOOLEAN DEFAULT 1")

        if 'updated_at' not in doc_columns:
            print("添加 updated_at 列...")
            cursor.execute("ALTER TABLE documents ADD COLUMN updated_at DATETIME")

        # 创建 chunks 表（如果不存在）
        print("检查 chunks 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                char_count INTEGER DEFAULT 0,
                token_count INTEGER DEFAULT 0,
                enabled BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_chunks_doc_id ON chunks(doc_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_chunks_id ON chunks(id)")

        conn.commit()
        print("数据库迁移完成!")

    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("数据库迁移脚本")
    print("=" * 50)
    migrate_database()
