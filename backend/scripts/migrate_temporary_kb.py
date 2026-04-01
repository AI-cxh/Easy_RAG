"""添加临时知识库字段的数据库迁移"""
import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'rag.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查字段是否已存在
    cursor.execute("PRAGMA table_info(knowledge_bases)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'is_temporary' not in columns:
        cursor.execute("ALTER TABLE knowledge_bases ADD COLUMN is_temporary BOOLEAN DEFAULT 0")
        print("Added is_temporary column")

    if 'session_id' not in columns:
        cursor.execute("ALTER TABLE knowledge_bases ADD COLUMN session_id INTEGER REFERENCES chat_sessions(id)")
        print("Added session_id column")

    conn.commit()
    conn.close()
    print("Migration completed successfully")

if __name__ == "__main__":
    migrate()
