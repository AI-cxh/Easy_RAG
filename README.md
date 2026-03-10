# Easy RAG

一个简单易用的 RAG（检索增强生成）应用，支持多知识库管理和网络搜索功能。

## 功能特性

- 聊天对话功能 - 基于 AI 模型的智能对话
- 多知识库管理 - 创建、删除独立的知识库
- 文件上传 - 支持 PDF、TXT、MD、DOCX 格式
- 知识库选择 - 聊天时可选择一个或多个知识库
- 网络搜索 - 集成在线搜索功能，可与知识库同时使用
- 响应式设计 - 支持桌面和移动设备

## 技术栈

- **后端**: FastAPI
- **前端**: Vue 3 + Vite
- **AI 模型**: 兼容 OpenAI API（支持 Ollama、VLLM 等本地模型）
- **向量数据库**: ChromaDB
- **数据库**: SQLite（使用 SQLAlchemy ORM）
- **RAG 框架**: LangChain

## 项目结构

```
Easy_RAG/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 应用入口
│   │   ├── config.py         # 配置管理
│   │   ├── models/           # 数据库模型
│   │   │   ├── database.py   # 数据库连接
│   │   │   ├── schemas.py    # Pydantic 模型
│   │   │   └── models.py     # SQL 模型
│   │   ├── api/              # API 路由
│   │   │   ├── chat.py       # 聊天 API
│   │   │   ├── knowledge.py  # 知识库 API
│   │   │   └── upload.py     # 文件上传 API
│   │   ├── services/         # 业务逻辑
│   │   │   ├── rag.py        # RAG 核心服务
│   │   │   ├── embedding.py  # 向量嵌入服务
│   │   │   └── search.py     # 网络搜索服务
│   │   └── utils/            # 工具函数
│   │       └── file_parser.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── components/
│   │   │   ├── ChatBoard.vue
│   │   │   ├── MessageList.vue
│   │   │   ├── KnowledgeSelector.vue
│   │   │   └── FileUpload.vue
│   │   ├── views/
│   │   │   ├── Chat.vue
│   │   │   └── KnowledgeBase.vue
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── router/
│   │   │   └── index.ts
│   │   └── styles/
│   │       └── main.css
│   ├── package.json
│   ├── vite.config.ts
│   └── .env
└── README.md
```

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+
- (可选) Ollama 或其他兼容 OpenAI API 的模型服务

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例配置文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据你的需求配置：

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# AI 模型配置
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=http://localhost:11434/v1  # Ollama
MODEL_NAME=gpt-4o-mini

# 嵌入模型配置
EMBEDDING_MODEL=text-embedding-3-small

# 数据库配置
DATABASE_URL=sqlite:///./rag.db

# ChromaDB 配置
CHROMA_DB_PATH=./chroma_db
```

### 3. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload
```

后端将在 http://localhost:8000 启动

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动前端服务

```bash
npm run dev
```

前端将在 http://localhost:5173 启动

## 使用说明

### 创建知识库

1. 访问"知识库管理"页面
2. 点击"创建知识库"按钮
3. 输入知识库名称和描述
4. 点击"创建"

### 上传文件

1. 选择一个知识库
2. 拖拽文件到上传区域，或点击选择文件
3. 支持的格式：PDF、TXT、MD、DOCX

### 开始聊天

1. 访问"聊天"页面
2. 选择要使用的知识库（可多选）
3. 勾选"网络搜索"启用在线搜索
4. 输入消息并发送

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看自动生成的 API 文档。

### 主要 API 端点

- `POST /api/chat` - 发送聊天消息
- `GET /api/chat/sessions` - 获取所有聊天会话
- `GET /api/knowledge` - 获取所有知识库
- `POST /api/knowledge` - 创建知识库
- `DELETE /api/knowledge/{kb_id}` - 删除知识库
- `POST /api/upload/{kb_id}` - 上传文件到知识库

## 使用 Ollama（可选）

如果你想使用本地模型而不是 OpenAI API：

1. 安装 Ollama: https://ollama.com/

2. 下载模型（例如 Llama3）:
```bash
ollama pull llama3
```

3. 配置 `.env` 文件:
```env
OPENAI_API_KEY=dummy_key
OPENAI_API_BASE=http://localhost:11434/v1
MODEL_NAME=llama3
EMBEDDING_MODEL=dummy_model  # Ollama 不需要单独的嵌入模型
```

注意：由于 Ollama 原生不支持嵌入 API，你可能需要使用其他嵌入服务或修改代码使用 Ollama 的 `/api/embeddings` 端点。

## 开发

### 后端开发

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm run dev
```

### 构建生产版本

```bash
cd frontend
npm run build
```

## 问题排查

### 数据库错误

如果遇到数据库错误，删除 `rag.db` 文件并重启应用，会自动创建新数据库。

### ChromaDB 错误

删除 `chroma_db` 目录并重启应用。

### 上传失败

确保上传的文件格式正确，文件大小合理（建议小于 50MB）。

## 许可证

MIT License
