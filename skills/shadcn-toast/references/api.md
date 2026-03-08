# Sonner + shadcn/ui API Reference

Complete reference for the sonner toast library and its shadcn/ui integration.

## Toaster Component Props

All props can be passed to the `<Toaster />` component (shadcn wrapper passes them through to sonner).

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `theme` | `'light' \| 'dark' \| 'system'` | `'light'` | Toast theme. shadcn wrapper auto-sets from `next-themes` |
| `richColors` | `boolean` | `false` | Vivid background colors for typed toasts |
| `expand` | `boolean` | `false` | Toasts expanded by default (normally expand on hover) |
| `visibleToasts` | `number` | `3` | Max visible toasts in the stack |
| `position` | `string` | `'bottom-right'` | `top-left \| top-center \| top-right \| bottom-left \| bottom-center \| bottom-right` |
| `closeButton` | `boolean` | `false` | Show close button on all toasts |
| `offset` | `string \| number \| object` | `'32px'` | Distance from screen edges. Object: `{ top, bottom, left, right }` |
| `mobileOffset` | `string \| number \| object` | `'16px'` | Offset on screens < 600px |
| `dir` | `'ltr' \| 'rtl'` | `'ltr'` | Text directionality |
| `hotkey` | `string` | `'alt+T'` | Keyboard shortcut to focus toaster |
| `invert` | `boolean` | `false` | Invert colors globally (dark in light mode, vice versa) |
| `gap` | `number` | `14` | Gap between expanded toasts in px |
| `duration` | `number` | `4000` | Default auto-close time for all toasts (ms) |
| `icons` | `object` | Lucide icons (shadcn) | Override icons: `{ success, error, warning, info, loading }` |
| `toastOptions` | `object` | — | Default options applied to all toasts |
| `swipeDirections` | `string[]` | Based on position | Allowed swipe directions for dismissal |
| `id` | `string` | — | Toaster ID for multi-toaster setups |
| `containerAriaLabel` | `string` | `'Notifications'` | ARIA label for screen readers |
| `pauseWhenPageIsHidden` | `boolean` | — | Pause auto-close when page is hidden |
| `cn` | `function` | — | Custom class merging function |

## Toast Options

All options can be passed as the second argument to any `toast()` method, or globally via `toastOptions` on `<Toaster />`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `description` | `ReactNode` | — | Text rendered below the title |
| `closeButton` | `boolean` | `false` | Show close button on this toast |
| `invert` | `boolean` | `false` | Invert colors for this toast |
| `duration` | `number` | `4000` | Auto-close time in ms. `Infinity` for persistent |
| `position` | `string` | `'bottom-right'` | Position override for this toast |
| `dismissible` | `boolean` | `true` | Whether user can dismiss |
| `icon` | `ReactNode` | — | Custom icon. `null` to remove default |
| `action` | `{ label, onClick } \| ReactNode` | — | Primary action button |
| `cancel` | `{ label, onClick } \| ReactNode` | — | Secondary cancel button |
| `id` | `string \| number` | auto | Custom ID for deduplication/updating |
| `testId` | `string` | — | Test ID for the toast element |
| `toasterId` | `string` | — | Target a specific `<Toaster id="...">` |
| `onDismiss` | `(toast) => void` | — | Fires when dismissed (close button or swipe) |
| `onAutoClose` | `(toast) => void` | — | Fires when auto-closed after duration |
| `style` | `CSSProperties` | — | Inline styles for the toast |
| `className` | `string` | — | CSS class for the toast |
| `classNames` | `object` | — | Classes for sub-elements (see below) |
| `unstyled` | `boolean` | `false` | Remove all default styles |
| `actionButtonStyle` | `CSSProperties` | — | Inline styles for action button |
| `cancelButtonStyle` | `CSSProperties` | — | Inline styles for cancel button |

## classNames Keys

Use in `classNames` on individual toasts or globally in `toastOptions.classNames`:

| Key | Target |
|-----|--------|
| `toast` | Toast container |
| `title` | Title text |
| `description` | Description text |
| `actionButton` | Action button |
| `cancelButton` | Cancel button |
| `closeButton` | Close button |
| `loader` | Loading spinner |
| `content` | Content wrapper |
| `icon` | Icon container |
| `success` | Success-type toast |
| `error` | Error-type toast |
| `info` | Info-type toast |
| `warning` | Warning-type toast |
| `loading` | Loading-type toast |
| `default` | Default-type toast |

## toast.promise() Options

```tsx
toast.promise(promise, {
  loading: string | ReactNode,
  success: string | ((data) => string | { message, description, duration, ... }),
  error: string | ((error) => string | { message, description, duration, ... }),
  finally: () => void,  // called after resolve or reject
})
```

## CSS Custom Properties

Sonner defines these on `[data-sonner-toaster]`. Override them in CSS for global theming.

### Layout

| Variable | Default | Description |
|----------|---------|-------------|
| `--width` | `356px` | Toast width |
| `--border-radius` | `8px` | Corner radius |
| `--gap` | `14px` | Gap between expanded toasts |
| `--offset-top` | — | Distance from top edge |
| `--offset-bottom` | — | Distance from bottom edge |
| `--offset-left` | — | Distance from left edge |
| `--offset-right` | — | Distance from right edge |

### Colors (Light Theme / richColors)

| Variable | Description |
|----------|-------------|
| `--normal-bg` | Default toast background (`#fff`) |
| `--normal-text` | Default toast text |
| `--normal-border` | Default toast border |
| `--success-bg` | Success background (`hsl(143, 85%, 96%)`) |
| `--success-border` | Success border |
| `--success-text` | Success text (`hsl(140, 100%, 27%)`) |
| `--error-bg` | Error background (`hsl(359, 100%, 97%)`) |
| `--error-border` | Error border |
| `--error-text` | Error text (`hsl(360, 100%, 45%)`) |
| `--info-bg` | Info background |
| `--info-border` | Info border |
| `--info-text` | Info text |
| `--warning-bg` | Warning background |
| `--warning-border` | Warning border |
| `--warning-text` | Warning text |

### Colors (Dark Theme / richColors)

| Variable | Description |
|----------|-------------|
| `--normal-bg` | `#000` |
| `--normal-text` | Light gray |
| `--normal-border` | `hsl(0, 0%, 20%)` |
| `--success-bg` | `hsl(150, 100%, 6%)` |
| `--success-text` | `hsl(150, 86%, 65%)` |
| `--error-bg` | `hsl(358, 76%, 10%)` |
| `--error-text` | `hsl(358, 100%, 81%)` |

### shadcn/ui CSS Variable Mapping

The shadcn wrapper maps these sonner variables to shadcn CSS variables:

```
--normal-bg     → var(--popover)
--normal-text   → var(--popover-foreground)
--normal-border → var(--border)
--border-radius → var(--radius)
```

## Data Attributes

Sonner exposes data attributes on DOM elements for CSS targeting:

| Attribute | Values | Element |
|-----------|--------|---------|
| `data-sonner-toaster` | — | Container |
| `data-sonner-toast` | — | Individual toast (`li`) |
| `data-sonner-theme` | `light`, `dark` | Container |
| `data-type` | `success`, `error`, `warning`, `info`, `loading`, `default` | Toast |
| `data-rich-colors` | `true`, `false` | Container |
| `data-styled` | `true`, `false` | Toast (false when `unstyled`) |
| `data-mounted` | `true`, `false` | Toast (entry animation) |
| `data-visible` | `true`, `false` | Toast (visible in stack) |
| `data-expanded` | `true`, `false` | Toast (expanded state) |
| `data-front` | `true`, `false` | Toast (front of stack) |
| `data-removed` | `true`, `false` | Toast (exit animation) |
| `data-swiping` | `true`, `false` | Toast (active swipe) |
| `data-swipe-out` | `true`, `false` | Toast (dismissed via swipe) |
| `data-y-position` | `top`, `bottom` | Toast |
| `data-x-position` | `left`, `center`, `right` | Toast |

### CSS targeting example

```css
[data-sonner-toaster][data-theme='dark'] [data-sonner-toast][data-type='success'] {
  background: hsl(150, 100%, 6%);
  color: hsl(150, 86%, 65%);
}
```

## shadcn/ui Wrapper Source

The generated `src/components/ui/sonner.tsx`:

```tsx
"use client"

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react"
import { useTheme } from "next-themes"
import { Toaster as Sonner, type ToasterProps } from "sonner"

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4" />,
        info: <InfoIcon className="size-4" />,
        warning: <TriangleAlertIcon className="size-4" />,
        error: <OctagonXIcon className="size-4" />,
        loading: <Loader2Icon className="size-4 animate-spin" />,
      }}
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--popover-foreground)",
          "--normal-border": "var(--border)",
          "--border-radius": "var(--radius)",
        } as React.CSSProperties
      }
      {...props}
    />
  )
}

export { Toaster }
```

## Multi-Toaster Setup

Use the `id` prop to create separate toaster instances:

```tsx
<Toaster id="global" position="top-right" />
<Toaster id="form" position="bottom-center" />

// Target a specific toaster
toast.success("Saved!", { toasterId: "global" })
toast.error("Validation failed", { toasterId: "form" })
```

## Accessibility

- `containerAriaLabel` prop (default: `'Notifications'`) for screen readers
- `hotkey` prop (default: `alt+T`) for keyboard focus
- Respects `prefers-reduced-motion` (disables animations)
- Proper ARIA attributes on toast elements
- Toasts are announced to screen readers automatically

## Responsive Behavior

- Toasts expand to full width on screens < 600px
- `mobileOffset` prop controls edge spacing on mobile
- Swipe-to-dismiss works on touch devices
- Swipe direction is auto-determined by toast position
