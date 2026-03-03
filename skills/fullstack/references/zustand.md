# Zustand State Management

Optional feature for the fullstack scaffold. Read this file when the user requests Zustand.

## Installation

```bash
cd frontend
pnpm add zustand
```

## Token Store (Auth Use Case)

The primary use case is storing authentication tokens with localStorage persistence:

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
    {
      name: "auth-storage",
    },
  ),
);
```

## Integration with ky

Read the token from Zustand inside ky hooks:

```typescript
// src/lib/api.ts
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

Key: use `useAuthStore.getState()` outside React components — this is Zustand's API for non-reactive access.

## General Store Pattern

For non-auth global state:

```typescript
// src/stores/appStore.ts
import { create } from "zustand";

interface AppState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()((set) => ({
  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
}));
```

## Usage in Components

```tsx
import { useAuthStore } from "@/stores/authStore";

function UserMenu() {
  const token = useAuthStore((s) => s.token);
  const clearToken = useAuthStore((s) => s.clearToken);

  if (!token) return null;

  return <button onClick={clearToken}>Logout</button>;
}
```

Key rules:
- Always use selector functions `(s) => s.field` to avoid unnecessary re-renders
- Use `persist` middleware only for state that must survive page reloads
- Keep stores small and focused — one store per domain, not one giant store
