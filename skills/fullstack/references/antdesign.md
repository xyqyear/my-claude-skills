# Ant Design Integration

Optional feature for the fullstack scaffold. Read this file when the user requests Ant Design.

## Installation

```bash
cd frontend
pnpm add antd @ant-design/icons
```

## Tailwind CSS v4 Compatibility

Ant Design has its own CSS reset which conflicts with Tailwind's preflight. In Tailwind v4, disable preflight using a CSS layer:

```css
/* src/index.css */
@import "tailwindcss";

@layer base {
  /* Disable Tailwind preflight to avoid conflicts with Ant Design */
  *, ::before, ::after {
    border-style: none;
  }
}

@theme {
  --color-primary: #1677ff;
}
```

Alternatively, if the conflict is minimal, you may keep both and override specific styles as needed.

## ConfigProvider Setup

Wrap the app in `ConfigProvider` in `src/main.tsx`:

```tsx
import { App as AntdApp, ConfigProvider } from "antd";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import App from "@/App";
import "./index.css";

const theme = {
  token: {
    colorPrimary: "#1677ff",
    borderRadius: 6,
  },
  components: {
    Layout: {
      headerBg: "#001529",
      bodyBg: "#f5f7fb",
    },
  },
};

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
    <ConfigProvider theme={theme}>
      <AntdApp>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <App />
          </BrowserRouter>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </AntdApp>
    </ConfigProvider>
  </StrictMode>,
);
```

Key points:
- `AntdApp` wraps everything to enable `App.useApp()` hooks for `message`, `notification`, `modal`
- `ConfigProvider` accepts a `theme` prop for design token customization
- For Chinese locale: `import zhCN from "antd/locale/zh_CN"` and add `locale={zhCN}` to ConfigProvider

## Layout Pattern

Standard admin layout with sidebar navigation synced to React Router:

```tsx
import { Layout, Menu } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router";
import {
  DashboardOutlined,
  SettingOutlined,
  UnorderedListOutlined,
} from "@ant-design/icons";

const { Sider, Header, Content } = Layout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "/items", icon: <UnorderedListOutlined />, label: "Items" },
  { key: "/settings", icon: <SettingOutlined />, label: "Settings" },
];

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Layout className="min-h-screen">
      <Sider breakpoint="lg" collapsedWidth={0}>
        <div className="h-8 m-4 text-white text-center font-bold">My App</div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header className="bg-white px-4 shadow-sm" />
        <Content className="m-4 p-6 bg-white rounded-lg">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
```

Then update `App.tsx` to use the layout:

```tsx
import { Route, Routes } from "react-router";
import { lazy, Suspense } from "react";
import MainLayout from "@/components/MainLayout";

const Home = lazy(() => import("@/pages/Home"));
const Items = lazy(() => import("@/pages/Items"));

export default function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/items" element={<Items />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
```

## Notification in Mutations

Use Ant Design's `App.useApp()` for notifications in mutation hooks:

```typescript
import { App } from "antd";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { itemApi } from "@/hooks/api/itemApi";
import { queryKeys } from "@/lib/query-keys";

export function useCreateItem() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: itemApi.create,
    onSuccess: () => {
      message.success("Item created");
      queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
    onError: (error) => {
      message.error(`Failed to create item: ${error.message}`);
    },
  });
}
```
