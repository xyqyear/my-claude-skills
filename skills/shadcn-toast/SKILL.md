---
name: shadcn-toast
description: Implement toast notifications using sonner with shadcn/ui integration. Use when users need to add toast/notification functionality, display success/error/warning/info messages, show loading states, or handle async operation feedback in a React project with sonner.
user-invokable: true
---

# Toast Notifications with Sonner + shadcn/ui

Implement toast notifications using the sonner library with shadcn/ui integration.

## Setup

### Install the sonner component

```bash
pnpm dlx shadcn@latest add sonner
```

This installs the `sonner` package and creates a wrapper component at `src/components/ui/sonner.tsx` that integrates with shadcn/ui theming and uses Lucide icons.

### Add Toaster to the root layout

Import `Toaster` from the **shadcn wrapper** (not directly from sonner):

```tsx
import { Toaster } from "@/components/ui/sonner"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
```

If the project uses `next-themes` or a similar theme provider, place `<Toaster />` inside the provider so it picks up the current theme automatically.

## Usage

Import `toast` directly from `sonner` (not from shadcn):

```tsx
import { toast } from "sonner"
```

### Toast types

```tsx
toast("Default message")
toast.success("Operation completed")
toast.error("Something went wrong")
toast.warning("Please review your input")
toast.info("New update available")
toast.loading("Processing...")
```

### Toast with description

```tsx
toast.success("Event created", {
  description: "Sunday, December 03, 2023 at 9:00 AM",
})
```

### Toast with action button

```tsx
toast("File deleted", {
  action: {
    label: "Undo",
    onClick: () => restoreFile(),
  },
})
```

To keep the toast open after clicking the action button, call `event.preventDefault()`:

```tsx
toast("Item saved", {
  action: {
    label: "View",
    onClick: (event) => {
      event.preventDefault()
      openDetails()
    },
  },
})
```

### Toast with cancel button

```tsx
toast("Confirm deletion?", {
  action: {
    label: "Delete",
    onClick: () => deleteItem(),
  },
  cancel: {
    label: "Cancel",
    onClick: () => console.log("Cancelled"),
  },
})
```

### Promise toast

Automatically transitions through loading, success, and error states:

```tsx
toast.promise(saveData(), {
  loading: "Saving...",
  success: "Data saved successfully",
  error: "Failed to save data",
})
```

Return objects for richer content:

```tsx
toast.promise(fetchUser(id), {
  loading: "Loading user...",
  success: (data) => ({
    message: `Welcome ${data.name}!`,
    description: data.email,
  }),
  error: (err) => ({
    message: "Failed to load user",
    description: err.message,
  }),
})
```

### Loading toast with manual state management

Use `id` to update a toast in place:

```tsx
const toastId = toast.loading("Uploading...")

try {
  await uploadFile()
  toast.success("Upload complete!", { id: toastId })
} catch (err) {
  toast.error("Upload failed", { id: toastId, description: err.message })
}
```

### Custom toast (JSX)

Render fully custom content using `toast.custom`. The callback receives the toast ID for programmatic dismissal:

```tsx
toast.custom((id) => (
  <div className="flex items-center gap-4 rounded-lg bg-white p-4 shadow-lg ring-1 ring-black/5">
    <div className="flex-1">
      <p className="text-sm font-medium text-gray-900">New message</p>
      <p className="mt-1 text-sm text-gray-500">You have a new notification</p>
    </div>
    <button
      className="rounded bg-indigo-50 px-3 py-1 text-sm font-semibold text-indigo-600 hover:bg-indigo-100"
      onClick={() => toast.dismiss(id)}
    >
      Dismiss
    </button>
  </div>
))
```

### Dismiss toasts

```tsx
// Dismiss a specific toast
const id = toast("Event created")
toast.dismiss(id)

// Dismiss all toasts
toast.dismiss()
```

### Update an existing toast

Pass the same `id` to update content or type:

```tsx
const id = toast("Processing...")
toast.success("Done!", { id })
```

### Persistent toast

Set `duration: Infinity` to keep a toast on screen until manually dismissed:

```tsx
toast.warning("Connection lost", {
  duration: Infinity,
  action: {
    label: "Retry",
    onClick: () => reconnect(),
  },
})
```

### Callbacks

```tsx
toast("Event created", {
  onDismiss: (t) => console.log(`Toast ${t.id} dismissed`),
  onAutoClose: (t) => console.log(`Toast ${t.id} auto-closed`),
})
```

## Toaster Configuration

Pass props to `<Toaster />` to configure global behavior:

```tsx
<Toaster
  position="bottom-right"
  richColors
  expand={false}
  closeButton
  duration={4000}
  visibleToasts={3}
  offset="32px"
  gap={14}
/>
```

Key props:
- `position` — `top-left | top-center | top-right | bottom-left | bottom-center | bottom-right` (default: `bottom-right`)
- `richColors` — more vivid colors for typed toasts (success, error, warning, info)
- `expand` — expand all toasts by default instead of stacking
- `closeButton` — show close button on all toasts
- `duration` — global auto-close time in ms (default: `4000`)
- `visibleToasts` — max visible in stack (default: `3`)
- `offset` — distance from screen edge (default: `32px`). Accepts string, number, or `{ top, bottom, left, right }`
- `mobileOffset` — offset on screens < 600px (default: `16px`)
- `hotkey` — keyboard shortcut to focus toaster (default: `alt+T`)

Apply default options to all toasts:

```tsx
<Toaster
  toastOptions={{
    duration: 5000,
    classNames: {
      title: "font-semibold",
      description: "text-muted-foreground",
    },
  }}
/>
```

## Styling

### Use richColors for quick colored toasts

```tsx
<Toaster richColors />
```

This gives `toast.success()`, `toast.error()`, `toast.warning()`, and `toast.info()` distinct, vivid background colors.

### Inline styles

Per-toast:

```tsx
toast("Custom styled", {
  style: { background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))" },
})
```

### classNames for sub-elements

Available keys: `toast`, `title`, `description`, `actionButton`, `cancelButton`, `closeButton`, `loader`, `content`, `icon`.

Type-specific keys: `success`, `error`, `info`, `warning`, `loading`, `default`.

```tsx
<Toaster
  toastOptions={{
    classNames: {
      actionButton: "!bg-primary !text-primary-foreground",
    },
  }}
/>
```

When overriding default styles with classNames, use `!important` (Tailwind `!` prefix) because sonner's built-in styles have higher specificity.

### Unstyled mode

Remove all default styling for full control:

```tsx
toast("Fully custom", {
  unstyled: true,
  classNames: {
    toast: "bg-card text-card-foreground rounded-lg p-4 shadow-lg border",
    title: "text-sm font-medium",
    description: "text-sm text-muted-foreground",
  },
})
```

### Custom icons

Per-toast:

```tsx
toast.success("Saved", { icon: <CheckCircle2 className="size-4" /> })
toast.success("No icon", { icon: null })
```

Global override via `<Toaster icons={...} />` — the shadcn wrapper already sets Lucide icons by default.

## shadcn/ui Wrapper Details

The generated `src/components/ui/sonner.tsx` wrapper does three things:

1. **Theme sync** — reads theme from `next-themes` via `useTheme()` and passes it to sonner
2. **Icon replacement** — uses Lucide icons (`CircleCheckIcon`, `InfoIcon`, `TriangleAlertIcon`, `OctagonXIcon`, `Loader2Icon`) instead of sonner's default SVGs
3. **CSS variable mapping** — bridges shadcn CSS variables to sonner's internal variables:
   - `--normal-bg` = `var(--popover)`
   - `--normal-text` = `var(--popover-foreground)`
   - `--normal-border` = `var(--border)`
   - `--border-radius` = `var(--radius)`

All additional `<Toaster>` props are passed through to sonner, so any sonner prop works on the shadcn wrapper.

## useSonner Hook

Access active toasts in React:

```tsx
import { useSonner } from "sonner"

function ToastCount() {
  const { toasts } = useSonner()
  return <span>{toasts.length} active</span>
}
```

Outside React: `toast.getActiveToasts()` returns an array of all active toasts.

## Key Rules

- Import `Toaster` from `@/components/ui/sonner` (shadcn wrapper). Import `toast` from `sonner` (the library).
- Place `<Toaster />` once in the root layout. Do not render multiple `<Toaster />` components unless using the `id` prop for multi-toaster setups.
- Use `toast.promise()` for async operations instead of manually managing loading/success/error states when possible.
- Use `richColors` on `<Toaster>` for colored typed toasts — without it, all types share the same neutral style.
- When overriding styles via `classNames`, prefix Tailwind classes with `!` to beat sonner's specificity.
- Set `duration: Infinity` for toasts that require user action (e.g., confirmation prompts, connection-lost warnings).
- The shadcn wrapper requires `next-themes` for theme detection. In projects without `next-themes`, modify the wrapper to remove the `useTheme()` call and pass `theme` manually.

For the complete API reference (all Toaster props, toast options, CSS variables, and data attributes), see [api.md](references/api.md).
