# Easy RAG

一个功能完整的 RAG（检索增强生成）应用，支持三种对话模式、多项目协作和跨会话记忆。

## 功能特性

### 对话模式

- **RAG 模式** — 传统检索增强生成，支持多知识库联合检索
- **Agent 模式** — 单智能体自主决策，自动选择知识库检索或网络搜索
- **Multi-Agent 模式** — 多智能体协同：Retrieval → Analysis → Writing，可视化展示执行流程

### 知识库管理

- **三层级架构**：知识库 → 文档 → 分块
- **分块级管控**：查看、编辑、启用/禁用单个分块，支持批量操作和向量重建
- **多格式上传**：支持 PDF、TXT、MD、DOCX
- **重排序优化**：可选 BGE reranker，提升检索精度
- **网络搜索**：集成 Tavily，获取实时信息

### 用户与协作

- **JWT 认证**：注册、登录、管理员审核流程
- **项目协作**：基于角色的权限控制（owner / editor / viewer）
- **管理面板**：用户管理、系统设置

### 记忆系统

- **会话记忆**：自动对多轮对话进行摘要压缩
- **项目记忆**：项目级别的固定上下文和偏好设置
- **跨会话记忆**：基于 Mem0 的用户长期记忆，跨会话保留

### 扩展能力

- **MCP 协议**：支持 Model Context Protocol，接入外部工具
- **自定义 Agent**：按项目创建和配置自定义智能体
- **兼容多厂商**：兼容 OpenAI API，支持 DeepSeek、OpenAI、Ollama 等

## 技术栈

| 层级 | 技术 |
|-------|------------|
| 前端 | Vue 3 + Vite + TypeScript |
| 后端 | FastAPI |
| 大模型 | OpenAI 兼容 API（DeepSeek、OpenAI、Ollama 等） |
| 向量库 | ChromaDB |
| 关系库 | SQLite（SQLAlchemy ORM） |
| RAG 框架 | LangChain |
| 搜索引擎 | Tavily |
| 长期记忆 | Mem0 + Qdrant |

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+

### 1. 安装后端

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 填入配置：

```env
# 大模型
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# 嵌入模型（可选，失败时自动回退到本地模型）
EMBEDDING_MODEL=BAAI/bge-m3

# 网络搜索（可选）
SEARCH_API_KEY=your_tavily_api_key

# 重排序（可选）
RERANK_API_BASE=https://api.siliconflow.cn/v1
RERANK_API_KEY=your_key

# 认证（生产环境务必设置强密钥）
JWT_SECRET_KEY=your_secret_key
```

### 3. 启动后端

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

后端运行在 `http://localhost:9000`，API 文档在 `http://localhost:9000/docs`。

### 4. 安装并启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`。

### 5. 首次使用

首次访问会自动跳转到管理员初始化页面，创建管理员账号后即可登录使用。

## 使用指南

### 三种对话模式

| 模式 | 路由 | 适用场景 |
|------|-------|----------|
| RAG | `/rag` | 基于文档的事实性问答 |
| Agent | `/agentic` | 灵活任务，自动选择检索或搜索 |
| Multi-Agent | `/multi-agent` | 复杂研究，需要规划和综合 |

三种模式均支持 SSE 流式输出、参考来源展示（含相关度评分）和记忆系统集成。

### 知识库管理

```
知识库 → 文档 → 分块
```

1. 创建知识库，可自定义分块大小和重叠量
2. 上传文档（PDF、TXT、MD、DOCX）
3. 管理分块：查看内容、编辑文本、启用/禁用、批量操作
4. 分块配置变更后重建向量

禁用的文档或分块通过 ChromaDB metadata 过滤，不参与检索。

### 项目协作

- 创建项目来组织知识库和对话
- 按 **owner**（所有者）、**editor**（编辑者）、**viewer**（查看者）角色邀请成员
- 设置项目记忆（背景、偏好、指令）

### 记忆系统

应用维护三层记忆：

1. **会话记忆** — 对话过长时自动摘要压缩，保留目标、约束和关键信息
2. **项目记忆** — 项目内跨会话共享的固定上下文
3. **用户记忆**（Mem0） — 设置 `MEM0_ENABLED=true` 后启用跨会话长期记忆

## API 端点

### 认证

| 方法 | 端点 | 说明 |
|--------|----------|-------------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 登录，返回 access + refresh token |
| POST | `/api/auth/refresh` | 刷新 access token |
| GET | `/api/auth/me` | 获取当前用户信息 |
| PUT | `/api/auth/password` | 修改密码 |
| POST | `/api/auth/init-admin` | 初始化首个管理员 |
| GET | `/api/auth/check-init` | 检查是否已有管理员 |
| GET | `/api/auth/users` | 用户列表（管理员） |
| PUT | `/api/auth/users/{id}/status` | 审核用户（管理员） |
| POST | `/api/auth/users/{id}/reset-password` | 重置密码（管理员） |

### 项目

| 方法 | 端点 | 说明 |
|--------|----------|-------------|
| GET / POST | `/api/projects` | 项目列表 / 创建项目 |
| GET / PUT / DELETE | `/api/projects/{id}` | 项目详情 / 更新 / 删除 |
| GET / POST | `/api/projects/{id}/members` | 成员列表 / 添加成员 |
| DELETE | `/api/projects/{id}/members/{user_id}` | 移除成员 |
| GET / POST | `/api/projects/{id}/memories` | 项目记忆列表 / 创建 |
| DELETE | `/api/projects/{id}/memories/{mem_id}` | 删除项目记忆 |

### 知识库

| 方法 | 端点 | 说明 |
|--------|----------|-------------|
| GET / POST | `/api/knowledge` | 知识库列表 / 创建 |
| GET | `/api/knowledge/stats` | 统计数据 |
| GET / PUT / DELETE | `/api/knowledge/{id}` | 详情 / 更新 / 删除 |
| GET | `/api/knowledge/{id}/documents` | 文档列表 |

### 文档与分块

| 方法 | 端点 | 说明 |
|--------|----------|-------------|
| POST | `/api/upload/{kb_id}` | 上传文件 |
| PUT | `/api/upload/documents/{id}/toggle` | 切换文档启用状态 |
| DELETE | `/api/upload/documents/{id}` | 删除文档 |
| GET | `/api/chunks/{doc_id}` | 分块列表 |
| PUT | `/api/chunks/{id}` | 编辑分块内容 |
| DELETE | `/api/chunks/{id}` | 删除分块 |
| PUT | `/api/chunks/{id}/toggle` | 切换分块启用状态 |
| POST | `/api/chunks/batch-enable` | 批量启用 |
| POST | `/api/chunks/batch-disable` | 批量禁用 |
| POST | `/api/chunks/rebuild-vectors/{doc_id}` | 重建向量 |

### 对话

| 方法 | 端点 | 说明 |
|--------|----------|-------------|
| POST | `/api/chat` | RAG 对话（SSE） |
| POST | `/api/chat/agent` | Agent 对话（SSE） |
| POST | `/api/chat/multi-agent` | Multi-Agent 对话（SSE） |
| GET | `/api/chat/sessions` | 会话列表 |
| DELETE | `/api/chat/sessions/{id}` | 删除会话 |

### 设置与 Agent

| 方法 | 端点 | 说明 |
|--------|----------|-------------|
| GET / POST | `/api/settings` | 获取 / 更新应用设置 |
| GET / POST | `/api/agents` | Agent 配置列表 / 创建 |
| PUT / DELETE | `/api/agents/{id}` | 更新 / 删除 Agent 配置 |
| GET | `/api/mcp/servers` | MCP 服务器列表 |

## 配置参考

| 配置项 | 默认值 | 说明 |
|---------|---------|-------------|
| `MODEL_NAME` | `deepseek-chat` | 对话模型 |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | 嵌入模型 |
| `RERANK_MODEL` | `BAAI/bge-reranker-v2-m3` | 重排序模型 |
| `CHUNK_SIZE` | `1000` | 默认分块大小 |
| `CHUNK_OVERLAP` | `200` | 默认分块重叠量 |
| `AGENT_MAX_ITERATIONS` | `10` | Agent 最大推理步数 |
| `MEM0_ENABLED` | `false` | 是否启用跨会话用户记忆 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | access token 有效期（24h） |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | refresh token 有效期 |

## 架构

```
用户问题
    │
    ▼
┌─────────────────────────────────────┐
│  对话 API（RAG / Agent / Multi-Agent）│
├─────────────────────────────────────┤
│  记忆层                              │
│  ├── 会话摘要                        │
│  ├── 项目记忆                        │
│  └── 用户记忆（Mem0）                 │
├─────────────────────────────────────┤
│  检索                                │
│  ├── ChromaDB 向量检索               │
│  ├── 重排序（BGE）                   │
│  └── 网络搜索（Tavily）               │
├─────────────────────────────────────┤
│  生成（OpenAI 兼容 LLM）              │
└─────────────────────────────────────┘
```

## 不同 LLM 提供者配置

```env
# DeepSeek
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# OpenAI
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# Ollama（本地）
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
MODEL_NAME=llama3
EMBEDDING_API_BASE=http://localhost:11434/v1
EMBEDDING_MODEL=nomic-embed-text
```

## 常见问题

| 问题 | 解决方法 |
|-------|----------|
| 数据库错误 | `rm backend/rag.db` 后重启 |
| ChromaDB 错误 | `rm -rf backend/chroma_db` 后重启 |
| 嵌入模型意外下载 | 检查 `set_chunks_enabled_by_doc_id` 是否使用 `collection.update()` 而非 `upsert()` |
| 禁用的分块仍被检索 | 检查 ChromaDB metadata 中 `enabled` 字段 |
| 登录异常 | 确认用户状态为"approved"，清除浏览器缓存 |
| MCP 连接失败 | 检查 MCP 服务器是否运行，配置路径是否正确 |

## 许可证

MIT License
