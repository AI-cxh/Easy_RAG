# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (port 9000)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# API docs: http://localhost:9000/docs
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend

# Install dependencies
npm install

# Run development server (port 5173, proxies to backend port 9000)
npm run dev

# Production build
npm run build
```

### Environment Configuration
Copy `backend/.env.example` to `backend/.env` and configure:
- `OPENAI_API_KEY` and `OPENAI_API_BASE` for LLM endpoints (e.g., DeepSeek, OpenAI)
- `SEARCH_API_KEY` for Tavily search service
- `API_PORT` must match backend port (default 9000)

## Architecture Overview

Easy RAG is a RAG application with three chat modes: basic RAG, Agent, and Multi-Agent collaboration.

### Backend Architecture
- **FastAPI** with SQLAlchemy ORM (SQLite by default)
- **ChromaDB** for vector storage - each knowledge base maps to a separate collection: `kb_{kb_id}`
- **LangChain** for RAG pipeline: text chunking → embedding → retrieval → generation
- **Tavily** for web search integration
- **MCP** (Model Context Protocol) for external tool integration via `langchain-mcp-adapters`

### Chat Modes
1. **RAG Mode** (`ChatRAG.vue`): Traditional RAG with knowledge base selection and optional web search
2. **Agent Mode** (`ChatAgentic.vue`): Single agent with tool calling, autonomous decision-making
3. **Multi-Agent Mode** (`ChatMultiAgent.vue`): OrchestratorAgent coordinates RetrievalAgent, AnalysisAgent, WritingAgent

### Data Flow
1. **File Upload**: Parser → Text chunking → Embedding (via OpenAI-compatible API) → ChromaDB storage
2. **Chat Request**: Query embedding → Similarity search (across selected knowledge bases) → Web search (optional) → LLM generation with context
3. **Session Management**: Chat sessions and messages persisted to SQLite

### Core Services
| Module | Purpose |
|--------|---------|
| `services/embedding.py` | Text chunking, vector embedding, ChromaDB operations per knowledge base |
| `services/rag.py` | Build context from retrieved docs, generate responses using LLM |
| `services/rerank.py` | Re-rank retrieved documents using external rerank API (optional) |
| `services/search.py` | Tavily web search integration |
| `services/agent.py` | Single agent service with tool calling loop |
| `services/tools.py` | Built-in tools: `knowledge_search`, `web_search`, `list_knowledge_bases`, `get_current_time`, `get_document_details` |
| `services/mcp_client.py` | MCP client for loading external tools from MCP servers |
| `utils/file_parser.py` | Supports: TXT, MD, PDF, DOCX |

### Multi-Agent Architecture
Located in `services/multi_agent/`:
- `base_agent.py`: BaseAgent abstract class, AgentTask, AgentResult, AgentType enum
- `orchestrator.py`: OrchestratorAgent - analyzes queries, generates execution plans, coordinates agents, synthesizes final answers
- `retrieval_agent.py`: RetrievalAgent - knowledge base search, web search, MCP tool execution
- `analysis_agent.py`: AnalysisAgent - deep analysis and reasoning
- `writing_agent.py`: WritingAgent - organizes language for final response
- `agent_registry.py`: AgentRegistry - manages registered agents by type

**Multi-Agent Flow**: User query → OrchestratorAgent.plan() → JSON execution plan → execute_plan() with dependency resolution → synthesize() final answer

### Database Models (SQLAlchemy)
- `KnowledgeBase` → `Document` (cascade delete)
- `ChatSession` → `ChatMessage` (cascade delete)
- `AgentConfig` - custom agent configurations
- Deleting a knowledge base removes both SQLite records and ChromaDB collection

### API Route Structure
All routes use `/api` prefix. Route paths are relative:
- `/api/chat` → POST (chat), GET/DELETE `/chat/sessions`
- `/api/chat/agent` → POST (agent mode chat, streaming SSE)
- `/api/chat/multi-agent` → POST (multi-agent mode chat, streaming SSE)
- `/api/knowledge` → CRUD operations, GET `/knowledge/{id}/documents`
- `/api/upload` → POST `/upload/{kb_id}`, DELETE `/upload/documents/{id}`
- `/api/settings` → GET/POST settings (persisted to `settings.json`)
- `/api/agents` → CRUD for custom agent configs
- `/api/mcp` → MCP server management

**Important**: When modifying routes, ensure paths don't duplicate (e.g., don't use `/api/chat` as both prefix and path, or you'll get `/api/chat/chat`).

### Configuration Notes
- `Settings` class supports both `OPENAI_API_BASE` and `OPENAI_BASE_URL` (as alias)
- Setting `extra = "ignore"` allows additional environment variables without validation errors
- Text chunking: `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=200` (configurable)
- Agent: `AGENT_MAX_ITERATIONS=10` (max tool calling iterations)
- ChromaDB path and upload directories are created on startup
- Settings API persists model configurations to `./settings.json` at runtime
- MCP servers configured in `./mcp_servers.json` with format: `{"servers": [{"name": "...", "transport": "stdio|http", ...}]}`

### LangChain Version Requirements
- Uses `langchain>=1.2.10`, `langchain-core>=1.2.18`, `langchain-openai>=1.1.11`
- Import changes from older versions:
  - `from langchain_core.messages import SystemMessage, HumanMessage` (not `langchain.schema`)
  - `from langchain_text_splitters import RecursiveCharacterTextSplitter` (not `langchain.text_splitter`)

### Frontend-Backend Communication
- Vite dev server proxies `/api/*` to `http://localhost:9000`
- API client: `frontend/src/api/client.ts` using native fetch with SSE streaming support
- Views: `ChatRAG.vue`, `ChatAgentic.vue`, `ChatMultiAgent.vue`, `KnowledgeBase.vue`, `Settings.vue`
- Components: `ChatBoard.vue`, `MessageList.vue`, `AgentFlow.vue`, `AgentThinking.vue`, `KnowledgeSelector.vue`, `FileUpload.vue`, `ToolsPanel.vue`

### Module Naming Convention
- API route modules are in `app/api/` - avoid naming conflicts with `config.py`'s `settings` instance
- Settings API module is named `app_settings.py` (not `settings.py`) to prevent shadowing the config settings
