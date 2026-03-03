---
name: fullstack
description: Scaffold a full-stack web application with FastAPI backend and React frontend. Use when the user wants to create a new project, initialize a web app, or set up a FastAPI + React monorepo. Triggers on requests like "create a new app", "scaffold a project", "init fullstack", "new FastAPI React project".
user-invokable: true
argument-hint: project-name
---

# Full-Stack Project Scaffold: FastAPI + React

Create a production-ready monorepo with a FastAPI backend (SQLAlchemy + aiosqlite) and a React frontend (Vite + TypeScript + TanStack Query + Tailwind CSS v4).

## Input

Parse the project name from `$ARGUMENTS` or ask the user. Use kebab-case for the directory name and derive display names from it.

Ask the user which optional features to include:
- **Ant Design** — UI component library. See [antdesign.md](references/antdesign.md)
- **Zustand** — State management. See [zustand.md](references/zustand.md)
- **JWT Auth** — Login system with pwdlib + joserfc. See [auth.md](references/auth.md)
- **Alembic** — Database migrations. See [alembic.md](references/alembic.md)

Read the corresponding reference file before implementing each optional feature.

## Project Structure

```
<project-name>/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI dual-app with SPA serving
│   │   ├── config.py         # Pydantic Settings
│   │   ├── db.py             # Async SQLAlchemy engine + session
│   │   ├── models.py         # SQLAlchemy ORM models (DeclarativeBase)
│   │   ├── repositories/     # Data access layer (pure DB operations)
│   │   │   └── __init__.py
│   │   ├── services/         # Business logic layer
│   │   │   └── __init__.py
│   │   └── routers/          # API route modules (HTTP concerns only)
│   │       └── __init__.py
│   ├── pyproject.toml
│   └── .python-version
├── frontend/
│   ├── src/
│   │   ├── main.tsx           # React entry with QueryClient + Router
│   │   ├── App.tsx            # Route definitions
│   │   ├── index.css          # Tailwind v4 entry
│   │   ├── lib/
│   │   │   ├── api.ts         # ky HTTP client instance
│   │   │   └── query-keys.ts  # Centralized query key factory
│   │   ├── hooks/
│   │   │   ├── api/           # Layer 1: pure API functions
│   │   │   ├── queries/       # Layer 2: useQuery wrappers
│   │   │   └── mutations/     # Layer 3: useMutation wrappers
│   │   ├── pages/             # Route page components
│   │   ├── components/        # Shared components
│   │   └── types/             # TypeScript type definitions
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   └── package.json
├── .vscode/
│   ├── launch.json
│   ├── tasks.json
│   └── <project-name>.code-workspace
├── .github/
│   └── workflows/
│       └── docker-image.yml
├── Dockerfile
├── compose.yaml
├── .env.example
├── .gitignore
└── CLAUDE.md
```

## Step 1: Initialize Project Root

Create the project directory and `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
.ruff_cache/
data/

# Node
node_modules/
dist/

# IDE
.idea/
*.swp
*.swo

# Environment
.env
!.env.example

# OS
.DS_Store
Thumbs.db
```

Initialize git: `git init`

## Step 2: Backend Setup

### 2.1 Initialize with uv

```bash
cd backend
uv init .
uv add fastapi 'uvicorn[standard]' 'sqlalchemy[asyncio]' aiosqlite pydantic-settings jinja2
uv add --dev pytest pytest-asyncio httpx ruff
```

Add to `pyproject.toml`:

```toml
[tool.uv]
package = false
```

### 2.2 app/config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "My App"
    api_prefix: str = "/api"
    database_url: str = "sqlite+aiosqlite:///./data/db.sqlite3"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    debug: bool = False


settings = Settings()
```

### 2.3 app/models.py

Use SQLAlchemy 2.x modern declarative style with `AsyncAttrs` + `DeclarativeBase`:

```python
from sqlalchemy import MetaData, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)


# Example model — replace with actual domain models
class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
```

Key rules:
- Always use `Mapped[type]` with `mapped_column()` — never legacy `Column()`
- Always include `AsyncAttrs` mixin on `Base` for async relationship access
- Always define `naming_convention` on `MetaData` — required for SQLite batch migrations
- Use `str | None` union syntax (Python 3.10+), not `Optional[str]`

### 2.4 app/db.py

```python
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Base

engine = create_async_engine(settings.database_url, echo=settings.debug)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    db_path = settings.database_url.split("///")[-1]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

Key rules:
- Always set `expire_on_commit=False` on async sessions
- Always enable `PRAGMA foreign_keys=ON` for SQLite via event listener
- Create the data directory before first DB access
- If Alembic is enabled, replace `create_all` with Alembic upgrade — see [alembic.md](references/alembic.md)

### 2.5 app/main.py

Dual-app architecture: a separate `api_app` mounted at `/api` on the main `app`. The main app serves the SPA frontend for all non-API routes.

```python
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routers import items

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    logger.info("Database initialized")
    yield


api_app = FastAPI(title=f"{settings.app_name} API")
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_app.include_router(items.router)


@api_app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {exc}"},
    )


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount(settings.api_prefix, api_app)

if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


def _resolve_frontend_file(path: str) -> Path | None:
    candidate = (FRONTEND_DIST / path).resolve()
    try:
        candidate.relative_to(FRONTEND_DIST.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _frontend_index() -> Path:
    index = FRONTEND_DIST / "index.html"
    if not index.is_file():
        raise HTTPException(
            status_code=404,
            detail="Frontend not built. Run `pnpm build` in frontend/.",
        )
    return index


@app.get("/", include_in_schema=False)
async def serve_spa_root():
    return FileResponse(_frontend_index())


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    prefix = settings.api_prefix.strip("/")
    if full_path == prefix or full_path.startswith(f"{prefix}/"):
        raise HTTPException(status_code=404, detail="Not found")

    if full_path:
        file = _resolve_frontend_file(full_path)
        if file is not None:
            return FileResponse(file)

    return FileResponse(_frontend_index())
```

Key rules:
- Always use `lifespan` context manager — never `@app.on_event()` (deprecated)
- CORS goes on `api_app`, not `app`
- SPA fallback must include path traversal protection via `relative_to()`
- Use `FileResponse` for static files, not Jinja2 templates

### 2.6 app/repositories/ — Data Access Layer

Repositories contain pure database operations — no business logic, no HTTP concerns. Async functions that accept `AsyncSession` as the first parameter.

Create `app/repositories/__init__.py` (empty) and `app/repositories/items.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item


async def get_by_id(db: AsyncSession, item_id: int) -> Item | None:
    return await db.get(Item, item_id)


async def list_all(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item).order_by(Item.id))
    return list(result.scalars().all())


async def save(db: AsyncSession, item: Item) -> Item:
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete(db: AsyncSession, item: Item) -> None:
    await db.delete(item)
    await db.commit()
```

Pattern rules:
- Pure data access — no validation, no HTTP exceptions, no business logic
- Accept `AsyncSession` as first parameter
- Consistent naming: `get_by_id`, `list_all`, `save`, `delete`
- Repositories handle `commit` and `refresh` for mutation operations
- Return ORM models or `None`, never raise HTTP exceptions

### 2.7 app/services/ — Business Logic Layer

Services orchestrate repositories and contain validation/business logic. They raise domain-specific errors that routers translate to HTTP responses.

Create `app/services/__init__.py` (empty) and `app/services/items.py`:

```python
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item
from app.repositories import items as item_repo


async def list_items(db: AsyncSession) -> list[Item]:
    return await item_repo.list_all(db)


async def get_item(db: AsyncSession, item_id: int) -> Item:
    item = await item_repo.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


async def create_item(db: AsyncSession, title: str, description: str | None) -> Item:
    item = Item(title=title, description=description)
    return await item_repo.save(db, item)


async def delete_item(db: AsyncSession, item_id: int) -> None:
    item = await get_item(db, item_id)
    await item_repo.delete(db, item)
```

Pattern rules:
- Import repositories as modules: `from app.repositories import items as item_repo`
- Contain validation and business rules (e.g., checking existence before delete)
- For simple CRUD, services may look thin — they become valuable as business logic grows

### 2.8 app/routers/ — API Route Modules

Routers handle HTTP concerns only: request parsing, response serialization, dependency injection. They delegate all logic to services.

Create `app/routers/__init__.py` (empty) and `app/routers/items.py`:

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services import items as item_service

router = APIRouter(prefix="/items", tags=["items"])


class ItemCreate(BaseModel):
    title: str
    description: str | None = None


class ItemRead(BaseModel):
    id: int
    title: str
    description: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ItemRead])
async def list_items(db: AsyncSession = Depends(get_db)):
    return await item_service.list_items(db)


@router.post("", response_model=ItemRead, status_code=201)
async def create_item(payload: ItemCreate, db: AsyncSession = Depends(get_db)):
    return await item_service.create_item(db, payload.title, payload.description)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    return await item_service.get_item(db, item_id)


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    await item_service.delete_item(db, item_id)
```

Pattern rules:
- Routers import services as modules: `from app.services import items as item_service`
- Pydantic schemas go in the same router file if small, or in `app/schemas/` if large
- Use `from_attributes = True` (was `orm_mode`) for ORM model serialization
- Use `model_dump()` (was `dict()`) for Pydantic v2
- Routers never import repositories directly — always go through services

**Data flow**: Router (HTTP) → Service (business logic) → Repository (DB operations)

## Step 3: Frontend Setup

### 3.1 Initialize with Vite

```bash
cd frontend
pnpm create vite . --template react-ts
pnpm add react-router @tanstack/react-query ky
pnpm add -D @tailwindcss/vite tailwindcss vite-tsconfig-paths @tanstack/react-query-devtools
```

Remove any auto-generated CSS files except `src/index.css`. Remove `src/App.css` if created.

### 3.2 vite.config.ts

```typescript
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tailwindcss(), tsconfigPaths()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

### 3.3 tsconfig.json and tsconfig.app.json

`tsconfig.json`:

```json
{
  "files": [],
  "references": [{ "path": "./tsconfig.app.json" }]
}
```

`tsconfig.app.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
```

### 3.4 src/index.css — Tailwind v4

```css
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
}
```

No `tailwind.config.js` needed. No `postcss.config.js` needed. The `@tailwindcss/vite` plugin handles everything.

### 3.5 src/main.tsx

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import App from "@/App";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
      retry: (failureCount, error) => {
        if ("response" in error && (error as any).response?.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
);
```

Key rules:
- Import `BrowserRouter` from `react-router` (not `react-router-dom`) — React Router v7 unified the packages
- `gcTime` replaces `cacheTime` from TanStack Query v4
- Do not retry on 4xx errors

### 3.6 src/App.tsx

```tsx
import { Route, Routes } from "react-router";
import Home from "@/pages/Home";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  );
}
```

Create `src/pages/Home.tsx` as a simple starter page.

### 3.7 src/lib/api.ts — ky Client

```typescript
import ky from "ky";

export const api = ky.create({
  prefixUrl: "/api",
  timeout: 15_000,
  hooks: {
    beforeError: [
      async ({ error }) => {
        if ("response" in error) {
          const body = (error as any).data as { detail?: string } | undefined;
          if (body?.detail) {
            error.message = body.detail;
          }
        }
        return error;
      },
    ],
  },
});
```

Key ky rules:
- `prefixUrl` not `baseURL` — and request paths must NOT start with `/`
- Use `json:` not `data:` for request body
- Use `searchParams:` not `params:` for query parameters
- Must call `.json<T>()` explicitly — ky does not auto-parse responses
- Hooks use `{ request, response, ... }` object — not positional args like axios interceptors

When auth is enabled, add `beforeRequest` and `afterResponse` hooks — see [auth.md](references/auth.md).

### 3.8 src/lib/query-keys.ts — Query Key Factory

```typescript
export const queryKeys = {
  items: {
    all: ["items"] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.items.all, "list", filters] as const,
    detail: (id: number) =>
      [...queryKeys.items.all, "detail", id] as const,
  },
  // Add more domains here as the app grows:
  // users: { ... },
  // settings: { ... },
};
```

Key rules:
- Always use `as const` for type safety
- Always use factory functions for parameterized keys
- Hierarchical structure: `domain.all` as base, `domain.list(filters)`, `domain.detail(id)`
- Never use string literals directly in useQuery/useMutation — always reference this factory

### 3.9 src/hooks/api/ — Layer 1: API Functions

Pure async functions that call ky. No React hooks. Example `src/hooks/api/itemApi.ts`:

```typescript
import { api } from "@/lib/api";
import type { Item, ItemCreate } from "@/types/item";

export const itemApi = {
  list: () => api.get("items").json<Item[]>(),
  get: (id: number) => api.get(`items/${id}`).json<Item>(),
  create: (data: ItemCreate) => api.post("items", { json: data }).json<Item>(),
  delete: (id: number) => api.delete(`items/${id}`),
};
```

### 3.10 src/hooks/queries/ — Layer 2: Query Hooks

Wrap API functions with `useQuery`. Example `src/hooks/queries/useItemQueries.ts`:

```typescript
import { useQuery } from "@tanstack/react-query";
import { itemApi } from "@/hooks/api/itemApi";
import { queryKeys } from "@/lib/query-keys";

export function useItems() {
  return useQuery({
    queryKey: queryKeys.items.list(),
    queryFn: itemApi.list,
  });
}

export function useItem(id: number) {
  return useQuery({
    queryKey: queryKeys.items.detail(id),
    queryFn: () => itemApi.get(id),
    enabled: !!id,
  });
}
```

Key rules:
- Always use single-object signature — overloads were removed in TanStack Query v5
- Use `isPending` for loading state, not `isLoading` (v5 change)
- Set `enabled: false` to disable query until a condition is met

### 3.11 src/hooks/mutations/ — Layer 3: Mutation Hooks

Wrap API functions with `useMutation`. Example `src/hooks/mutations/useItemMutations.ts`:

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { itemApi } from "@/hooks/api/itemApi";
import { queryKeys } from "@/lib/query-keys";

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: itemApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
  });
}

export function useDeleteItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: itemApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
  });
}
```

Key rules:
- Invalidate using the `all` key to refresh all queries in that domain
- `onSuccess`/`onError`/`onSettled` callbacks are available on mutations (removed from queries in v5)

### 3.12 src/types/ — Type Definitions

Create `src/types/item.ts`:

```typescript
export interface Item {
  id: number;
  title: string;
  description: string | null;
}

export interface ItemCreate {
  title: string;
  description?: string;
}
```

## Step 4: VSCode Configuration

### .vscode/launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend: Uvicorn",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "cwd": "${workspaceFolder}/backend",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "debug"
      ],
      "justMyCode": true
    },
    {
      "name": "Frontend: Chrome (Vite)",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend",
      "preLaunchTask": "Frontend: Dev Server",
      "postDebugTask": "Frontend: Stop Dev Server"
    }
  ],
  "compounds": [
    {
      "name": "Full Stack Debug",
      "configurations": [
        "Backend: Uvicorn",
        "Frontend: Chrome (Vite)"
      ]
    }
  ]
}
```

### .vscode/tasks.json

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Frontend: Dev Server",
      "type": "shell",
      "command": "pnpm dev",
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "isBackground": true,
      "problemMatcher": {
        "owner": "custom",
        "pattern": { "regexp": "." },
        "background": {
          "activeOnStart": true,
          "beginsPattern": ".",
          "endsPattern": ".*Local:.*http://localhost.*"
        }
      },
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      }
    },
    {
      "label": "Frontend: Stop Dev Server",
      "type": "shell",
      "command": "pkill -f \"${workspaceFolder}/frontend.*vite\" || true",
      "problemMatcher": []
    }
  ]
}
```

### .vscode/\<project-name\>.code-workspace

```json
{
  "folders": [
    { "path": "frontend", "name": "Frontend" },
    { "path": "backend", "name": "Backend" },
    { "path": ".", "name": "Root" }
  ]
}
```

## Step 5: Dockerfile

Multi-stage build with pnpm + uv:

```dockerfile
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM ghcr.io/astral-sh/uv:python3.13-alpine AS backend-venv
WORKDIR /app/backend
ENV UV_LINK_MODE=copy
RUN apk add --no-cache gcc musl-dev libffi-dev
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv venv /app/backend/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM python:3.13-alpine AS runtime
WORKDIR /app
ENV VIRTUAL_ENV=/app/backend/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache libffi libgcc libstdc++
COPY --from=backend-venv /app/backend/.venv /app/backend/.venv
COPY backend/ /app/backend/
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist
EXPOSE 8000
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips=*"]
```

## Step 6: compose.yaml

```yaml
services:
  app:
    image: ghcr.io/<owner>/<project-name>
    container_name: <project-name>
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/backend/data
    environment:
      - APP_NAME=My App
    restart: unless-stopped
```

Replace `<owner>` and `<project-name>` with actual values.

## Step 7: GitHub Actions

`.github/workflows/docker-image.yml`:

```yaml
name: Docker Image CI

on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
  workflow_dispatch:

permissions:
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=sha
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## Step 8: .env.example

```bash
# Application
APP_NAME=My App
DEBUG=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/db.sqlite3

# CORS (comma-separated origins are not supported — use JSON array in code)
# Defaults: http://localhost:5173, http://localhost:3000
```

## Step 9: CLAUDE.md

Generate a project `CLAUDE.md` using the template in [claude-md-template.md](references/claude-md-template.md). Fill in the project name, tech stack, and initial structure.

## Step 10: Final Checks

1. Verify backend starts: `cd backend && uv run uvicorn app.main:app --reload --port 8000`
2. Verify frontend starts: `cd frontend && pnpm dev`
3. Verify API proxy works: open `http://localhost:5173/api/items` in browser
4. Create initial git commit: `git add . && git commit -m "feat: scaffold project"`
