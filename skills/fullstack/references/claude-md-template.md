# CLAUDE.md Template

Generate this file at the project root when scaffolding a new project. Replace placeholders with actual values.

---

```markdown
# CLAUDE.md

## Project Overview

**{project-name}** is a full-stack web application with a FastAPI backend and React frontend.

**Tech Stack:**
- Backend: FastAPI, SQLAlchemy (async), aiosqlite, Pydantic Settings
- Frontend: Vite, React 19, TypeScript, TanStack Query v5, Tailwind CSS v4, ky
- Tooling: uv (Python), pnpm (Node.js)

## Repository Structure

```
{project-name}/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app (dual-app: api_app at /api, app serves SPA)
│   │   ├── config.py      # Pydantic Settings
│   │   ├── db.py          # Async SQLAlchemy engine + session
│   │   ├── models.py      # ORM models (DeclarativeBase + AsyncAttrs)
│   │   └── routers/       # API route modules
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── main.tsx        # Entry: QueryClient + BrowserRouter
│   │   ├── App.tsx         # Route definitions
│   │   ├── lib/
│   │   │   ├── api.ts      # ky HTTP client
│   │   │   └── query-keys.ts  # Query key factory
│   │   ├── hooks/
│   │   │   ├── api/        # Pure API functions (ky calls)
│   │   │   ├── queries/    # useQuery wrappers
│   │   │   └── mutations/  # useMutation wrappers
│   │   ├── pages/
│   │   ├── components/
│   │   └── types/
│   └── vite.config.ts
├── .vscode/                # Debug configs (Backend, Frontend, Full Stack)
├── Dockerfile              # Multi-stage: node + uv + python-alpine
├── compose.yaml
└── .github/workflows/      # Docker image CI
```

## Development Commands

```bash
# Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && pnpm dev

# Docker
docker compose up -d
```

## Architecture

- Backend serves API at `/api/*` and SPA frontend at all other routes
- Frontend proxies `/api` to backend in dev mode (vite.config.ts)
- Database: SQLite stored at `backend/data/db.sqlite3`
- Frontend data layer: API functions -> Query hooks -> Components (3-layer pattern)
- Query keys centralized in `lib/query-keys.ts`

## Keeping This File Current

This file must always reflect the current state of the codebase. When planning changes that modify the project structure, API surface, or architecture, include CLAUDE.md updates in the plan. Write the file as if from scratch for the current state — no changelogs or "updated X" notes.
```
