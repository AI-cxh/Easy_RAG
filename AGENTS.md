# Repository Guidelines

## Project Structure & Module Organization
`backend/` contains the FastAPI API and data layer. Core code lives under `backend/app/`: `api/` for route handlers, `services/` for RAG, agent, search, and MCP logic, `models/` for SQLAlchemy and Pydantic models, and `utils/` for file parsing. Migration and one-off maintenance scripts live in `backend/scripts/`.

`frontend/` is a Vue 3 + Vite + TypeScript app. Use `src/views/` for page-level screens, `src/components/` for reusable UI, `src/composables/` for shared stateful logic, `src/api/` for HTTP clients, and `src/styles/` plus `src/assets/` for styling assets.

## Build, Test, and Development Commands
Backend setup and run:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

Frontend setup and run:

```bash
cd frontend
npm install
npm run dev
npm run build
```

Use `npm run build` to verify the frontend production bundle before opening a PR. For backend data changes, run the relevant script in `backend/scripts/`, for example `python scripts/migrate_db.py`.

## Coding Style & Naming Conventions
Follow the existing style in each area: Python uses 4-space indentation, type hints, and `snake_case`; keep FastAPI routes thin and move business logic into `services/`. Vue and TypeScript files use 2-space indentation, `PascalCase` for component files like `SourceDrawer.vue`, and `camelCase` for composables and helpers such as `useAuth.ts`.

No formatter or linter config is committed yet, so keep imports tidy, favor small modules, and match nearby files instead of introducing a new style.

## Testing Guidelines
There is no dedicated `tests/` directory yet. Until one is added, validate changes with targeted manual checks: start both apps, exercise the affected flow, and confirm the backend health endpoint at `/health` plus the relevant UI screen. If you add automated coverage, place backend tests under `backend/tests/` and frontend tests beside the feature or under `frontend/src/__tests__/`.

## Commit & Pull Request Guidelines
Recent history mixes short Chinese summaries with Conventional Commit style such as `fix: improve embedding error handling with retry and fallback`. Prefer concise, imperative subjects and use prefixes like `fix:`, `feat:`, or `docs:` when practical.

PRs should explain scope, list touched areas (`backend/app/services/rag.py`, `frontend/src/views/ChatAgentic.vue`), describe manual verification, and include screenshots for UI changes.

## Security & Configuration Tips
Do not commit real API keys, JWT secrets, or `.env` files. Keep local credentials in environment variables, rotate any exposed secrets, and treat `backend/settings.json` and `backend/mcp_servers.json` as configuration files that may contain environment-specific values.
