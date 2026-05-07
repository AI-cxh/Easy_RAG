# Easy RAG

A full-featured RAG (Retrieval-Augmented Generation) application with three chat modes, multi-project collaboration, and cross-session memory.

## Features

### Chat Modes

- **RAG Mode** — Traditional retrieval-augmented generation with multi-KB selection
- **Agent Mode** — Single agent with autonomous tool selection (knowledge base search, web search)
- **Multi-Agent Mode** — Orchestrator delegates to specialized agents: Retrieval → Analysis → Writing, with visual execution flow

### Knowledge Management

- **Three-tier hierarchy**: Knowledge Base → Document → Chunk
- **Chunk-level control**: View, edit, enable/disable individual chunks, batch operations, vector rebuild
- **Multi-format upload**: PDF, TXT, MD, DOCX
- **Reranking**: Optional BGE reranker for improved retrieval precision
- **Web search**: Tavily integration for real-time information

### User & Collaboration

- **JWT authentication** with user registration, login, admin approval workflow
- **Project-based collaboration** with role-based access (owner / editor / viewer)
- **Admin panel**: User management, system settings

### Memory System

- **Session memory**: Automatic multi-turn conversation summarization
- **Project memory**: Pinned project-level context and preferences
- **Cross-session memory**: Mem0-powered long-term user memory across sessions

### Extensibility

- **MCP protocol**: Model Context Protocol support for external tools
- **Custom agents**: Create and configure custom agents per project
- **OpenAI-compatible**: Works with DeepSeek, OpenAI, Ollama, and any compatible API

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + TypeScript |
| Backend | FastAPI (Python) |
| LLM | OpenAI-compatible API (DeepSeek, OpenAI, Ollama, etc.) |
| Vector DB | ChromaDB |
| Relational DB | SQLite (SQLAlchemy ORM) |
| RAG Framework | LangChain |
| Search | Tavily API |
| Long-term Memory | Mem0 + Qdrant |

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+

### 1. Install Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# AI Model
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# Embedding (optional — falls back to local model)
EMBEDDING_MODEL=BAAI/bge-m3

# Web Search (optional)
SEARCH_API_KEY=your_tavily_api_key

# Rerank (optional)
RERANK_API_BASE=https://api.siliconflow.cn/v1
RERANK_API_KEY=your_key

# Auth (set a strong secret in production)
JWT_SECRET_KEY=your_secret_key
```

### 3. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

Backend runs at `http://localhost:9000`, API docs at `http://localhost:9000/docs`.

### 4. Install & Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 5. First Launch

On first visit, you'll be redirected to the admin initialization page. Create an admin account, then log in to start using the app.

## Usage

### Three Chat Modes

| Mode | Route | Best For |
|------|-------|----------|
| RAG | `/rag` | Factual Q&A over your documents |
| Agent | `/agentic` | Flexible tasks with automatic tool selection |
| Multi-Agent | `/multi-agent` | Complex research requiring planning and synthesis |

All modes support SSE streaming, source citation with relevance scores, and memory integration.

### Knowledge Base Management

```
Knowledge Base → Document → Chunk
```

1. Create a knowledge base with custom chunk size/overlap
2. Upload documents (PDF, TXT, MD, DOCX)
3. Manage chunks: view, edit content, enable/disable, batch operations
4. Rebuild vectors when chunk configuration changes

Disabled documents or chunks are excluded from retrieval via ChromaDB metadata filtering.

### Project Collaboration

- Create projects to organize knowledge bases and conversations
- Invite members with **owner**, **editor**, or **viewer** roles
- Set project-level memories (context, preferences, instructions)

### Memory System

The app maintains three layers of memory:

1. **Session memory** — automatically summarizes conversations when they grow long, preserving goals, constraints, and key facts
2. **Project memory** — pinned context snippets shared across sessions within a project
3. **User memory** (Mem0) — cross-session long-term memory, enabled via `MEM0_ENABLED=true`

## API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get access + refresh tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/password` | Change password |
| POST | `/api/auth/init-admin` | Initialize first admin |
| GET | `/api/auth/check-init` | Check if admin exists |
| GET | `/api/auth/users` | List users (admin) |
| PUT | `/api/auth/users/{id}/status` | Approve/reject user (admin) |
| POST | `/api/auth/users/{id}/reset-password` | Reset user password (admin) |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/projects` | List / create projects |
| GET/PUT/DELETE | `/api/projects/{id}` | Get / update / delete project |
| GET/POST | `/api/projects/{id}/members` | List / add members |
| DELETE | `/api/projects/{id}/members/{user_id}` | Remove member |
| GET/POST | `/api/projects/{id}/memories` | List / create project memories |
| DELETE | `/api/projects/{id}/memories/{mem_id}` | Delete project memory |

### Knowledge Bases

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/knowledge` | List / create knowledge bases |
| GET | `/api/knowledge/stats` | Get statistics |
| GET/PUT/DELETE | `/api/knowledge/{id}` | Get / update / delete KB |
| GET | `/api/knowledge/{id}/documents` | List documents in KB |

### Documents & Chunks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/{kb_id}` | Upload file to KB |
| PUT | `/api/upload/documents/{id}/toggle` | Toggle document enabled |
| DELETE | `/api/upload/documents/{id}` | Delete document |
| GET | `/api/chunks/{doc_id}` | List chunks |
| PUT | `/api/chunks/{id}` | Update chunk content |
| DELETE | `/api/chunks/{id}` | Delete chunk |
| PUT | `/api/chunks/{id}/toggle` | Toggle chunk enabled |
| POST | `/api/chunks/batch-enable` | Batch enable chunks |
| POST | `/api/chunks/batch-disable` | Batch disable chunks |
| POST | `/api/chunks/rebuild-vectors/{doc_id}` | Rebuild vectors |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | RAG chat (SSE) |
| POST | `/api/chat/agent` | Agent chat (SSE) |
| POST | `/api/chat/multi-agent` | Multi-agent chat (SSE) |
| GET | `/api/chat/sessions` | List sessions |
| DELETE | `/api/chat/sessions/{id}` | Delete session |

### Settings & Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/settings` | Get / update app settings |
| GET/POST | `/api/agents` | List / create agent configs |
| PUT/DELETE | `/api/agents/{id}` | Update / delete agent config |
| GET | `/api/mcp/servers` | List MCP servers |

## Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `MODEL_NAME` | `deepseek-chat` | Chat model |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Embedding model |
| `RERANK_MODEL` | `BAAI/bge-reranker-v2-m3` | Rerank model |
| `CHUNK_SIZE` | `1000` | Default chunk size |
| `CHUNK_OVERLAP` | `200` | Default chunk overlap |
| `AGENT_MAX_ITERATIONS` | `10` | Max agent reasoning steps |
| `MEM0_ENABLED` | `false` | Enable cross-session user memory |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token TTL (24h) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |

## Architecture

```
User Question
    │
    ▼
┌─────────────────────────────────────┐
│  Chat API (RAG / Agent / Multi-Agent) │
├─────────────────────────────────────┤
│  Memory Layer                        │
│  ├── Session Summary                 │
│  ├── Project Memory                  │
│  └── User Memory (Mem0)              │
├─────────────────────────────────────┤
│  Retrieval                           │
│  ├── ChromaDB Vector Search          │
│  ├── Rerank (BGE)                    │
│  └── Web Search (Tavily)             │
├─────────────────────────────────────┤
│  Generation (OpenAI-compatible LLM)  │
└─────────────────────────────────────┘
```

## Using Different LLM Providers

```env
# DeepSeek
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# OpenAI
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# Ollama (local)
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
MODEL_NAME=llama3
EMBEDDING_API_BASE=http://localhost:11434/v1
EMBEDDING_MODEL=nomic-embed-text
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database errors | `rm backend/rag.db` and restart |
| ChromaDB errors | `rm -rf backend/chroma_db` and restart |
| Embedding model downloads unexpectedly | Ensure `set_chunks_enabled_by_doc_id` uses `collection.update()` not `upsert()` |
| Disabled chunks still retrieved | Check ChromaDB metadata has `enabled` field |
| Login issues | Verify user status is "approved", clear browser cache |
| MCP connection failed | Check MCP server is running and paths are correct |

## License

MIT License
