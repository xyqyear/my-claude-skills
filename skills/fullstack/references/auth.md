# JWT Authentication

Optional feature for the fullstack scaffold. Read this file when the user requests login/auth.

This adds JWT-based authentication using `pwdlib` (Argon2 password hashing) and `joserfc` (JWT tokens).

## Backend Setup

### Install Dependencies

```bash
cd backend
uv add 'pwdlib[argon2]' joserfc
```

### Update config.py

Add JWT settings to `app/config.py`:

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseModel):
    secret_key: str = "change-me-to-a-random-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "My App"
    api_prefix: str = "/api"
    database_url: str = "sqlite+aiosqlite:///./data/db.sqlite3"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    debug: bool = False

    jwt: JWTSettings = JWTSettings()


settings = Settings()
```

Note `env_nested_delimiter="__"` — this allows setting `JWT__SECRET_KEY=xxx` as an environment variable.

### User Model

Add to `app/models.py`:

```python
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
```

### Auth Utilities

Create `app/auth.py`:

```python
from datetime import datetime, timedelta, timezone

from joserfc import jwt
from joserfc.jwk import OctKey
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.config import settings

password_hash = PasswordHash((Argon2Hasher(),))
key = OctKey.import_key(settings.jwt.secret_key)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + (expires_delta or timedelta(minutes=settings.jwt.access_token_expire_minutes))
    claims = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode({"alg": settings.jwt.algorithm}, claims, key)


def decode_access_token(token: str) -> dict:
    token_obj = jwt.decode(token, key)
    claims = token_obj.claims

    now = datetime.now(timezone.utc).timestamp()
    if claims.get("exp", 0) < now:
        raise ValueError("Token expired")

    return claims
```

### Auth Dependencies

Create `app/deps.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_access_token
from app.db import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        claims = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.username == claims["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
```

### Auth Router

Create `app/routers/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(user.username))


@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

Register the router in `app/main.py`:

```python
from app.routers import auth
api_app.include_router(auth.router)
```

### Protecting Routes

Use `Depends(get_current_user)` on protected endpoints:

```python
from app.deps import get_current_user
from app.models import User

@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user
```

Or apply to an entire router:

```python
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)],
)
```

## Frontend Setup

### Token Storage

Use Zustand for token persistence (see [zustand.md](zustand.md)):

```typescript
// src/stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  setToken: (token: string) => void;
  clearToken: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token) => set({ token }),
      clearToken: () => set({ token: null }),
    }),
    { name: "auth-storage" },
  ),
);
```

### API Client with Auth

Update `src/lib/api.ts` to include auth hooks:

```typescript
import ky from "ky";
import { useAuthStore } from "@/stores/authStore";

export const api = ky.create({
  prefixUrl: "/api",
  timeout: 15_000,
  hooks: {
    beforeRequest: [
      ({ request }) => {
        const token = useAuthStore.getState().token;
        if (token) {
          request.headers.set("Authorization", `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async ({ response }) => {
        if (response.status === 401) {
          useAuthStore.getState().clearToken();
          window.location.href = "/login";
        }
      },
    ],
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

### Login Page

```tsx
// src/pages/Login.tsx
import { useState } from "react";
import { useNavigate } from "react-router";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/authStore";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const setToken = useAuthStore((s) => s.setToken);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const form = new URLSearchParams();
      form.set("username", username);
      form.set("password", password);

      const data = await api
        .post("auth/login", { body: form })
        .json<{ access_token: string }>();

      setToken(data.access_token);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleSubmit} className="w-80 space-y-4">
        <h1 className="text-2xl font-bold text-center">Login</h1>
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full rounded border px-3 py-2"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded border px-3 py-2"
        />
        <button
          type="submit"
          className="w-full rounded bg-primary px-3 py-2 text-white hover:bg-primary-dark"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
```

Note: `OAuth2PasswordRequestForm` expects `application/x-www-form-urlencoded`, not JSON. Use `URLSearchParams` as the body.

### Protected Routes

```tsx
// src/App.tsx
import { Navigate, Outlet, Route, Routes } from "react-router";
import { useAuthStore } from "@/stores/authStore";
import Login from "@/pages/Login";
import Home from "@/pages/Home";

function ProtectedRoute() {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
}

function AuthRoute() {
  const token = useAuthStore((s) => s.token);
  if (token) return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<AuthRoute />}>
        <Route path="/login" element={<Login />} />
      </Route>
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
      </Route>
    </Routes>
  );
}
```

### .env.example Additions

```bash
# JWT
JWT__SECRET_KEY=change-me-to-a-random-secret
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=30
```
