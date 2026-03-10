# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 开发命令

### 后端 (FastAPI)
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器（端口 9000）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# 访问 API 文档：http://localhost:9000/docs
```

### 前端 (Vue 3 + Vite)
```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器（端口 5173，代理到后端端口 9000）
npm run dev

# 生产构建
npm run build
```

### 环境配置
复制 `backend/.env.example` 到 `backend/.env` 并配置：
- `OPENAI_API_KEY` 和 `OPENAI_BASE_URL` 用于 LLM 端点（如 DeepSeek、OpenAI）
- `SEARCH_API_KEY` 用于 Tavily 搜索服务
- `API_PORT` 必须与后端端口匹配（默认 9000）

## 架构概览

Easy RAG 是一个前后端分离的 RAG（检索增强生成）应用，具有以下关键特性：

### 后端架构
- **FastAPI** 配合 SQLAlchemy ORM（默认 SQLite）
- **ChromaDB** 用于向量存储 - 每个知识库映射到独立的集合：`kb_{kb_id}`
- **LangChain** 构建 RAG 流程：文本分块 → 嵌入 → 检索 → 生成
- **Tavily** 集成网络搜索功能

### 数据流程
1. **文件上传**：解析器 → 文本分块 → 嵌入（通过 OpenAI 兼容 API）→ ChromaDB 存储
2. **聊天请求**：查询嵌入 → 相似度搜索（跨选中的知识库）→ 网络搜索（可选）→ 带上下文的 LLM 生成
3. **会话管理**：聊天会话和消息持久化到 SQLite

### 核心服务
| 模块 | 用途 |
|------|------|
| `services/embedding.py` | 文本分块、向量嵌入、按知识库操作 ChromaDB |
| `services/rag.py` | 从检索文档构建上下文、使用 LLM 生成响应 |
| `services/search.py` | Tavily 网络搜索集成 |
| `utils/file_parser.py` | 支持：TXT、MD、PDF、DOCX |

### 数据库模型 (SQLAlchemy)
- `KnowledgeBase` → `Document`（级联删除）
- `ChatSession` → `ChatMessage`（级联删除）
- 删除知识库会同时移除 SQLite 记录和 ChromaDB 集合

### API 路由结构
所有路由使用前缀 `/api`。路由路径是相对的：
- `/api/chat` → POST（聊天），GET/DELETE `/chat/sessions`
- `/api/knowledge` → CRUD 操作，GET `/knowledge/{id}/documents`
- `/api/upload` → POST `/upload/{kb_id}`，DELETE `/upload/documents/{id}`

**重要**：修改路由时，确保路径不重复（例如，不要同时使用 `/api/chat` 作为前缀和路径，否则会得到 `/api/chat/chat`）。

### 重要配置说明
- `Settings` 类同时支持 `OPENAI_API_BASE` 和 `OPENAI_BASE_URL`（作为别名）
- 设置 `extra = "ignore"` 允许额外的环境变量而不报验证错误
- 文本分块：`CHUNK_SIZE=1000`、`CHUNK_OVERLAP=200`（可配置）
- ChromaDB 路径、上传目录在启动时自动创建

### LangChain 版本要求
- 使用 `langchain>=1.2.10`、`langchain-core>=1.2.18`、`langchain-openai>=1.1.11`
- 与旧版本相比的导入变化：
  - `from langchain_core.messages import SystemMessage, HumanMessage`（而非 `langchain.schema`）
  - `from langchain_text_splitters import RecursiveCharacterTextSplitter`（而非 `langchain.text_splitter`）

### 前后端通信
- Vite 开发服务器将 `/api/*` 代理到 `http://localhost:9000`
- API 客户端：`frontend/src/api/client.ts`，带 axios 拦截器
- 组件：`ChatBoard.vue`、`MessageList.vue`（使用 marked + highlight.js）、`KnowledgeSelector.vue`、`FileUpload.vue`
