# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Backend (from backend/)
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# Frontend (from frontend/)
npm install
npm run dev
npm run build

# Database migration (from backend/)
python scripts/migrate_db.py
python scripts/migrate_chunks.py
```

## Architecture Overview

### Three-Level Knowledge Base Hierarchy

```
KnowledgeBase → Document → Chunk
```

- Each knowledge base maps to a ChromaDB collection named `kb_{id}`
- Chunk `enabled` status stored in ChromaDB metadata, filtered via `where={"enabled": True}` during retrieval
- SQLite stores structured data; ChromaDB stores vectors and metadata

### Three Chat Modes

1. **RAG Mode** (`/api/chat`) - Traditional retrieval-augmented generation
2. **Agent Mode** (`/api/chat/agent`) - Single agent with tool selection (knowledge base, web search)
3. **Multi-Agent Mode** (`/api/chat/multi-agent`) - Orchestrator coordinates: RetrievalAgent → AnalysisAgent → WritingAgent

### Backend Structure

```
backend/app/
├── config.py           # All configuration via pydantic-settings
├── models/
│   ├── models.py       # SQLAlchemy models (KnowledgeBase, Document, Chunk)
│   └── schemas.py      # Pydantic request/response schemas
├── api/                # FastAPI routers
└── services/
    ├── embedding.py    # OpenAI-compatible embeddings with HuggingFace fallback
    ├── rag.py          # Core RAG pipeline
    ├── agent.py        # Single agent implementation
    └── multi_agent/    # Multi-agent orchestration
```

### Frontend Structure

```
frontend/src/
├── views/              # Page components (ChatRAG, ChatAgentic, KnowledgeList, etc.)
├── components/         # Reusable components (AgentFlow, Pagination, etc.)
├── api/client.ts       # Axios API client
└── router/index.ts     # Vue Router configuration
```

## Key Configuration (backend/app/config.py)

| Setting | Default | Purpose |
|---------|---------|---------|
| `MODEL_NAME` | `deepseek-chat` | Chat model |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Embedding model |
| `RERANK_MODEL` | `BAAI/bge-reranker-v2-m3` | Rerank model |
| `CHUNK_SIZE` | `1000` | Default chunk size |
| `CHUNK_OVERLAP` | `200` | Default chunk overlap |

## Important Implementation Details

### Embedding Service (`embedding.py`)

- Uses OpenAI-compatible API for embeddings
- Falls back to `sentence-transformers/all-MiniLM-L6-v2` if API fails
- **Critical**: `set_chunks_enabled_by_doc_id()` must use `collection.update()` for metadata-only changes, not `upsert()` which triggers re-embedding

### Chunk Enable/Disable Flow

1. Frontend calls `/api/chunks/{id}/toggle`
2. Backend updates SQLite `Chunk.enabled`
3. Backend calls `embedding_service.set_chunks_enabled_by_doc_id()` to update ChromaDB metadata
4. Retrieval filters by `where={"enabled": True}`

### File Upload Processing

1. File saved to `backend/uploads/{kb_id}/`
2. Parsed by `file_parser.py` (supports PDF, TXT, MD, DOCX)
3. Split into chunks via `RecursiveCharacterTextSplitter`
4. Chunks embedded and stored in ChromaDB

## API Provider Compatibility

Works with any OpenAI-compatible API:

```env
# DeepSeek
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat

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
| Embedding model downloads unexpectedly | Check `set_chunks_enabled_by_doc_id` uses `update()` not `upsert()` |
| Disabled chunks still retrieved | Verify ChromaDB metadata has `enabled` field; check `enabled_only=True` in `search_similar()` |
| Database errors | Delete `backend/rag.db` and restart |
| ChromaDB errors | Delete `backend/chroma_db` and restart |
