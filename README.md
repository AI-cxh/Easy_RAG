# Easy RAG

一个功能丰富的 RAG（检索增强生成）应用，支持三种对话模式：传统 RAG、智能 Agent 和多 Agent 协同。

## 功能特性

### 三种对话模式

- **RAG 模式** - 传统检索增强生成，选择知识库后进行问答
- **Agent 模式** - 单智能体自主决策，自动选择使用知识库检索或网络搜索
- **多 Agent 协同** - 多个专业 Agent 协作完成复杂任务，支持任务规划和可视化

### 核心功能

- **三层级知识库管理** - 知识库 → 文档 → 分块，精细化管控数据
- **分块管理** - 查看、编辑、启用/禁用单个分块，支持批量操作
- **文档状态管理** - 启用/禁用文档，控制是否参与检索
- **多知识库管理** - 创建、删除独立的知识库，支持多知识库同时检索
- **文件上传** - 支持 PDF、TXT、MD、DOCX 格式文档
- **网络搜索** - 集成 Tavily 搜索引擎，获取实时信息
- **重排序优化** - 可选的 Rerank 功能，提升检索精度
- **MCP 工具扩展** - 支持 Model Context Protocol，接入外部工具
- **自定义 Agent** - 创建和配置自定义智能体
- **流式响应** - 所有对话模式支持 SSE 流式输出
- **响应式设计** - 支持桌面和移动设备

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端框架 | Vue 3 + Vite + TypeScript |
| AI 模型 | 兼容 OpenAI API（DeepSeek、OpenAI、Ollama 等） |
| 向量数据库 | ChromaDB |
| 关系数据库 | SQLite（SQLAlchemy ORM） |
| RAG 框架 | LangChain |
| 网络搜索 | Tavily API |
| 工具协议 | MCP (Model Context Protocol) |

## 项目结构

```
agentic_RAG/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── models/
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── models.py        # SQLAlchemy 模型
│   │   │   └── schemas.py       # Pydantic 模型
│   │   ├── api/
│   │   │   ├── chat.py          # 聊天 API
│   │   │   ├── knowledge.py     # 知识库 API
│   │   │   ├── upload.py        # 文件上传 API
│   │   │   ├── chunks.py        # 分块管理 API
│   │   │   ├── agents.py        # Agent 管理 API
│   │   │   ├── mcp.py           # MCP 服务管理 API
│   │   │   └── app_settings.py  # 设置 API
│   │   ├── services/
│   │   │   ├── rag.py           # RAG 核心服务
│   │   │   ├── embedding.py     # 向量嵌入服务
│   │   │   ├── search.py        # 网络搜索服务
│   │   │   ├── rerank.py        # 重排序服务
│   │   │   ├── agent.py         # 单 Agent 服务
│   │   │   ├── tools.py         # 内置工具定义
│   │   │   ├── mcp_client.py    # MCP 客户端
│   │   │   └── multi_agent/     # 多 Agent 模块
│   │   │       ├── orchestrator.py    # 主控 Agent
│   │   │       ├── retrieval_agent.py # 检索 Agent
│   │   │       ├── analysis_agent.py  # 分析 Agent
│   │   │       ├── writing_agent.py   # 写作 Agent
│   │   │       └── custom_agent.py    # 自定义 Agent
│   │   └── utils/
│   │       └── file_parser.py   # 文件解析
│   ├── scripts/
│   │   ├── migrate_db.py        # 数据库迁移脚本
│   │   └── migrate_chunks.py    # 分块数据迁移脚本
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── ChatRAG.vue       # RAG 对话页面
│   │   │   ├── ChatAgentic.vue   # Agent 对话页面
│   │   │   ├── ChatMultiAgent.vue # 多 Agent 对话页面
│   │   │   ├── KnowledgeList.vue # 知识库列表页面
│   │   │   ├── DocumentList.vue  # 文档列表页面
│   │   │   ├── ChunkList.vue     # 分块列表页面
│   │   │   └── Settings.vue      # 设置页面
│   │   ├── components/
│   │   │   ├── AgentFlow.vue     # Agent 执行流程可视化
│   │   │   ├── AgentThinking.vue # Agent 思考过程展示
│   │   │   ├── Pagination.vue    # 分页组件
│   │   │   ├── Breadcrumb.vue    # 面包屑导航
│   │   │   ├── ToolsPanel.vue    # 工具面板
│   │   │   └── ...
│   │   ├── api/
│   │   │   └── client.ts         # API 客户端
│   │   └── router/
│   │       └── index.ts          # 路由配置
│   └── package.json
└── README.md
```

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=9000

# AI 模型配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# 嵌入模型配置
EMBEDDING_MODEL=text-embedding-3-small

# 网络搜索配置 (可选)
SEARCH_API_KEY=your_tavily_api_key

# 重排序配置 (可选，提升检索精度)
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_API_KEY=your_rerank_api_key
RERANK_API_BASE=https://api.siliconflow.cn/v1
```

### 3. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

后端将在 http://localhost:9000 启动，API 文档地址：http://localhost:9000/docs

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

### 知识库管理

Easy RAG 采用三层级管理架构：

```
知识库 (Knowledge Base)
  └── 文档 (Document)
        └── 分块 (Chunk)
```

#### 知识库层级

1. 访问"知识库管理"页面
2. 点击"新建知识库"，输入名称、描述、分块参数等
3. 点击知识库名称进入文档管理页面

#### 文档层级

1. 在文档管理页面上传文件（支持 PDF、TXT、MD、DOCX）
2. 查看文档处理状态（处理中/已完成/失败）
3. 可启用/禁用文档，禁用后该文档不参与检索
4. 点击文档名称进入分块管理页面

#### 分块层级

1. 查看文档的所有分块内容
2. 编辑分块内容，自动更新向量
3. 启用/禁用单个分块，精细控制检索范围
4. 批量操作：批量启用/禁用、全量启用/禁用
5. 重建向量：根据当前启用的分块重新生成向量

### RAG 模式

1. 访问"RAG 对话"页面
2. 在左侧选择要使用的知识库（可多选）
3. 可选：开启"网络搜索"
4. 输入问题，获取基于知识库的回答

### Agent 模式

1. 访问"Agent 对话"页面
2. Agent 会自主决定是否需要检索知识库或搜索网络
3. 可查看 Agent 的思考过程和工具调用记录
4. 支持多轮对话和上下文理解

### 多 Agent 协同

1. 访问"多 Agent"页面
2. 输入复杂问题，系统自动分解任务
3. 可视化展示执行计划：检索 Agent → 分析 Agent → 写作 Agent
4. 实时查看各 Agent 的执行状态和结果

### MCP 工具配置

在设置页面配置 MCP 服务器，或直接编辑 `mcp_servers.json`：

```json
{
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "command": "python",
      "args": ["/path/to/server.py"]
    },
    {
      "name": "database",
      "transport": "http",
      "url": "http://localhost:8001/mcp"
    }
  ]
}
```

## API 端点

### 聊天相关

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chat` | POST | RAG 模式聊天 |
| `/api/chat/agent` | POST | Agent 模式聊天 (SSE) |
| `/api/chat/multi-agent` | POST | 多 Agent 模式聊天 (SSE) |
| `/api/chat/sessions` | GET | 获取会话列表 |
| `/api/chat/sessions/{id}` | DELETE | 删除会话 |

### 知识库管理

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/knowledge` | GET | 获取知识库列表（分页） |
| `/api/knowledge` | POST | 创建知识库 |
| `/api/knowledge/stats` | GET | 获取统计数据 |
| `/api/knowledge/{id}` | GET/PUT/DELETE | 知识库详情/更新/删除 |
| `/api/knowledge/{id}/documents` | GET | 获取知识库的文档列表 |

### 文档管理

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/upload/{kb_id}` | POST | 上传文件到知识库 |
| `/api/upload/documents/{id}` | PUT | 更新文档信息 |
| `/api/upload/documents/{id}` | DELETE | 删除文档 |
| `/api/upload/documents/{id}/toggle` | PUT | 切换文档启用状态 |

### 分块管理

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chunks/{doc_id}` | GET | 获取分块列表（分页） |
| `/api/chunks/{doc_id}` | POST | 创建分块 |
| `/api/chunks/{chunk_id}` | PUT | 更新分块 |
| `/api/chunks/{chunk_id}` | DELETE | 删除分块 |
| `/api/chunks/{chunk_id}/toggle` | PUT | 切换分块启用状态 |
| `/api/chunks/batch-enable` | POST | 批量启用分块 |
| `/api/chunks/batch-disable` | POST | 批量禁用分块 |
| `/api/chunks/enable-all/{doc_id}` | POST | 全量启用 |
| `/api/chunks/disable-all/{doc_id}` | POST | 全量禁用 |
| `/api/chunks/rebuild-vectors/{doc_id}` | POST | 重建向量 |

### 其他

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/agents` | GET/POST | Agent 配置列表/创建 |
| `/api/mcp/servers` | GET | MCP 服务器列表 |
| `/api/settings` | GET/POST | 应用设置 |

## 数据迁移

如果您从旧版本升级，需要运行迁移脚本：

```bash
cd backend

# 迁移数据库结构（添加新字段）
python scripts/migrate_db.py

# 迁移分块数据（从 ChromaDB 同步到 SQLite）
python scripts/migrate_chunks.py
```

## 使用 DeepSeek

DeepSeek 是一个高性价比的 AI 服务提供商：

```env
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
```

注意：DeepSeek 目前不提供嵌入服务，建议嵌入模型使用 OpenAI 或其他服务。

## 使用 Ollama 本地模型

1. 安装 Ollama: https://ollama.com/

2. 下载模型：
```bash
ollama pull llama3
ollama pull nomic-embed-text  # 嵌入模型
```

3. 配置 `.env`：
```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
MODEL_NAME=llama3
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_API_BASE=http://localhost:11434/v1
```

## 多 Agent 架构

```
用户问题
    ↓
OrchestratorAgent (主控)
    ├── 分析问题，生成执行计划 (JSON)
    ├── 按依赖关系调度执行
    └── 综合结果，生成最终回答
        ↓
RetrievalAgent (检索)
    ├── 知识库搜索
    ├── 网络搜索
    └── MCP 工具调用
        ↓
AnalysisAgent (分析)
    └── 深度分析和推理
        ↓
WritingAgent (写作)
    └── 组织语言生成回答
```

## 问题排查

### 数据库错误
```bash
rm backend/rag.db
# 重启应用
```

### ChromaDB 错误
```bash
rm -rf backend/chroma_db
# 重启应用
```

### MCP 连接失败
- 检查 MCP 服务器是否正常运行
- 确认配置中的命令路径和参数正确
- 查看后端日志获取详细错误信息

### 禁用功能不生效
- 确保已运行数据库迁移脚本
- 检查 ChromaDB 中的 metadata 是否包含 `enabled` 字段
- 尝试重建向量

## 许可证

MIT License
