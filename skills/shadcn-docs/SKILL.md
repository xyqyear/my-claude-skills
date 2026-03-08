---
name: shadcn-docs
description: Provides development guidelines and best practices for shadcn/ui — styling rules, component composition, CLI commands, theming, and accessibility. Activates when working with shadcn/ui components, Tailwind CSS styling, components.json, or any React frontend using shadcn. Covers correct API usage, semantic colors, form layout, icons, and base vs radix differences.
---

# shadcn/ui Development Guide

A framework for building UI, components and design systems. Components are added as source code via the CLI — you own the code entirely.

> **Related skills:** For specific patterns, use the dedicated skills:
> - `/shadcn-form` — Forms with shadcn/ui Field + React Hook Form + Zod
> - `/shadcn-toast` — Toast notifications with sonner + shadcn/ui
> - `/shadcn-datatable` — Data tables with TanStack Table + shadcn/ui

> **IMPORTANT:** Run all CLI commands using `pnpm dlx shadcn@latest`. If the project uses a different package manager, check `packageManager` from `pnpm dlx shadcn@latest info` and substitute accordingly.

## Current Project Context

```json
!`pnpm dlx shadcn@latest info --json 2>/dev/null || echo '{"error": "No shadcn project found. Run shadcn init first."}'`
```

The JSON above contains the project config and installed components. Use `pnpm dlx shadcn@latest docs <component>` to get documentation and example URLs for any component.

## Principles

1. **Use existing components first.** Use `pnpm dlx shadcn@latest search` to check registries before writing custom UI. Check community registries too.
2. **Compose, don't reinvent.** Settings page = Tabs + Card + form controls. Dashboard = Sidebar + Card + Chart + Table.
3. **Use built-in variants before custom styles.** `variant="outline"`, `size="sm"`, etc.
4. **Use semantic colors.** `bg-primary`, `text-muted-foreground` — never raw values like `bg-blue-500`.

## Critical Rules

These rules are **always enforced**. Each links to a file with Incorrect/Correct code pairs.

### Styling & Tailwind → [styling.md](./references/styling.md)

- **`className` for layout, not styling.** Never override component colors or typography.
- **No `space-x-*` or `space-y-*`.** Use `flex` with `gap-*`. For vertical stacks, `flex flex-col gap-*`.
- **Use `size-*` when width and height are equal.** `size-10` not `w-10 h-10`.
- **Use `truncate` shorthand.** Not `overflow-hidden text-ellipsis whitespace-nowrap`.
- **No manual `dark:` color overrides.** Use semantic tokens (`bg-background`, `text-muted-foreground`).
- **Use `cn()` for conditional classes.** Don't write manual template literal ternaries.
- **No manual `z-index` on overlay components.** Dialog, Sheet, Popover, etc. handle their own stacking.

### Forms & Inputs → [forms.md](./references/forms.md)

- **Forms use `FieldGroup` + `Field`.** Never use raw `div` with `space-y-*` or `grid gap-*` for form layout.
- **`InputGroup` uses `InputGroupInput`/`InputGroupTextarea`.** Never raw `Input`/`Textarea` inside `InputGroup`.
- **Buttons inside inputs use `InputGroup` + `InputGroupAddon`.**
- **Option sets (2–7 choices) use `ToggleGroup`.** Don't loop `Button` with manual active state.
- **`FieldSet` + `FieldLegend` for grouping related checkboxes/radios.** Don't use a `div` with a heading.
- **Field validation uses `data-invalid` + `aria-invalid`.** `data-invalid` on `Field`, `aria-invalid` on the control.

> For complex forms with React Hook Form + Zod, use the `/shadcn-form` skill.

### Component Structure → [composition.md](./references/composition.md)

- **Items always inside their Group.** `SelectItem` → `SelectGroup`. `DropdownMenuItem` → `DropdownMenuGroup`. `CommandItem` → `CommandGroup`.
- **Use `asChild` (radix) or `render` (base) for custom triggers.** Check `base` field from `pnpm dlx shadcn@latest info`. → [base-vs-radix.md](./references/base-vs-radix.md)
- **Dialog, Sheet, and Drawer always need a Title.** Required for accessibility. Use `className="sr-only"` if visually hidden.
- **Use full Card composition.** `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`.
- **Button has no `isPending`/`isLoading`.** Compose with `Spinner` + `data-icon` + `disabled`.
- **`TabsTrigger` must be inside `TabsList`.** Never render triggers directly in `Tabs`.
- **`Avatar` always needs `AvatarFallback`.** For when the image fails to load.

### Use Components, Not Custom Markup → [composition.md](./references/composition.md)

- **Callouts use `Alert`.** Don't build custom styled divs.
- **Empty states use `Empty`.** Don't build custom empty state markup.
- **Toast via `sonner`.** Use `toast()` from `sonner`. For detailed patterns, use `/shadcn-toast`.
- **Use `Separator`** instead of `<hr>` or `<div className="border-t">`.
- **Use `Skeleton`** for loading placeholders. No custom `animate-pulse` divs.
- **Use `Badge`** instead of custom styled spans.

### Icons → [icons.md](./references/icons.md)

- **Icons in `Button` use `data-icon`.** `data-icon="inline-start"` or `data-icon="inline-end"` on the icon.
- **No sizing classes on icons inside components.** Components handle icon sizing via CSS.
- **Pass icons as objects, not string keys.** `icon={CheckIcon}`, not a string lookup.

### CLI

- **Never decode or fetch preset codes manually.** Pass them directly to `pnpm dlx shadcn@latest init --preset <code>`.

## Key Patterns

```tsx
// Form layout: FieldGroup + Field, not div + Label.
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <Input id="email" />
  </Field>
</FieldGroup>

// Validation: data-invalid on Field, aria-invalid on the control.
<Field data-invalid>
  <FieldLabel>Email</FieldLabel>
  <Input aria-invalid />
  <FieldDescription>Invalid email.</FieldDescription>
</Field>

// Icons in buttons: data-icon, no sizing classes.
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

// Spacing: gap-*, not space-y-*.
<div className="flex flex-col gap-4">  // correct
<div className="space-y-4">           // wrong

// Equal dimensions: size-*, not w-* h-*.
<Avatar className="size-10">   // correct
<Avatar className="w-10 h-10"> // wrong

// Status colors: Badge variants or semantic tokens, not raw colors.
<Badge variant="secondary">+20.1%</Badge>    // correct
<span className="text-emerald-600">+20.1%</span> // wrong
```

## Component Selection

| Need                       | Use                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------- |
| Button/action              | `Button` with appropriate variant                                                                   |
| Form inputs                | `Input`, `Select`, `Combobox`, `Switch`, `Checkbox`, `RadioGroup`, `Textarea`, `InputOTP`, `Slider` |
| Toggle between 2–5 options | `ToggleGroup` + `ToggleGroupItem`                                                                   |
| Data display               | `Table`, `Card`, `Badge`, `Avatar`                                                                  |
| Data tables                | Use `/shadcn-datatable` skill for TanStack Table integration                                        |
| Navigation                 | `Sidebar`, `NavigationMenu`, `Breadcrumb`, `Tabs`, `Pagination`                                     |
| Overlays                   | `Dialog` (modal), `Sheet` (side panel), `Drawer` (bottom sheet), `AlertDialog` (confirmation)       |
| Feedback                   | `sonner` (toast), `Alert`, `Progress`, `Skeleton`, `Spinner`                                        |
| Command palette            | `Command` inside `Dialog`                                                                           |
| Charts                     | `Chart` (wraps Recharts)                                                                            |
| Layout                     | `Card`, `Separator`, `Resizable`, `ScrollArea`, `Accordion`, `Collapsible`                          |
| Empty states               | `Empty`                                                                                             |
| Menus                      | `DropdownMenu`, `ContextMenu`, `Menubar`                                                            |
| Tooltips/info              | `Tooltip`, `HoverCard`, `Popover`                                                                   |

## Key Fields

The injected project context contains these key fields:

- **`aliases`** → use the actual alias prefix for imports (e.g. `@/`), never hardcode.
- **`isRSC`** → when `true`, components using `useState`, `useEffect`, event handlers, or browser APIs need `"use client"` at the top. For Vite projects, this is always `false`.
- **`tailwindVersion`** → `"v4"` uses `@theme inline` blocks; `"v3"` uses `tailwind.config.js`.
- **`tailwindCssFile`** → the global CSS file where custom CSS variables are defined. Always edit this file, never create a new one.
- **`style`** → component visual treatment (e.g. `nova`, `vega`).
- **`base`** → primitive library (`radix` or `base`). Affects component APIs and available props. See [base-vs-radix.md](./references/base-vs-radix.md).
- **`iconLibrary`** → determines icon imports. Use `lucide-react` for `lucide`, `@tabler/icons-react` for `tabler`, etc. Never assume `lucide-react`.
- **`resolvedPaths`** → exact file-system destinations for components, utils, hooks, etc.
- **`framework`** → routing and file conventions (e.g. Next.js App Router vs Vite SPA).
- **`packageManager`** → use this for non-shadcn dependency installs (e.g. `pnpm add date-fns`).

See [cli.md — `info` command](./references/cli.md) for the full field reference.

## Component Docs, Examples, and Usage

Run `pnpm dlx shadcn@latest docs <component>` to get URLs for documentation, examples, and API references. Fetch these URLs to get the actual content.

```bash
pnpm dlx shadcn@latest docs button dialog select
```

**When creating, fixing, debugging, or using a component, always run `pnpm dlx shadcn@latest docs` and fetch the URLs first.** This ensures you work with the correct API and usage patterns.

## Workflow

1. **Get project context** — already injected above. Run `pnpm dlx shadcn@latest info` to refresh.
2. **Check installed components** — before running `add`, check the `components` list from project context or list the `resolvedPaths.ui` directory. Don't import components that haven't been added.
3. **Find components** — `pnpm dlx shadcn@latest search`.
4. **Get docs and examples** — run `pnpm dlx shadcn@latest docs <component>` to get URLs, then fetch them. Use `pnpm dlx shadcn@latest view` to browse registry items not yet installed.
5. **Install or update** — `pnpm dlx shadcn@latest add`. When updating existing components, use `--dry-run` and `--diff` to preview changes first.
6. **Fix imports in third-party components** — After adding from community registries, check added files for hardcoded import paths like `@/components/ui/...`. Use the project's actual aliases from `info` output.
7. **Review added components** — After adding from any registry, read the added files and verify correctness. Check for missing sub-components, missing imports, incorrect composition, or rule violations. Replace icon imports to match the project's `iconLibrary`.
8. **Registry must be explicit** — When adding a block or component, do not guess the registry. If none specified, ask which registry to use.

## Updating Components

When updating a component from upstream while keeping local changes, use `--dry-run` and `--diff`. **NEVER fetch raw files from GitHub manually — always use the CLI.**

1. Run `pnpm dlx shadcn@latest add <component> --dry-run` to see affected files.
2. For each file, run `pnpm dlx shadcn@latest add <component> --diff <file>` to see changes.
3. Decide per file:
   - No local changes → safe to overwrite.
   - Has local changes → analyze diff, apply upstream updates while preserving local modifications.
   - User says "just update everything" → use `--overwrite`, but confirm first.
4. **Never use `--overwrite` without the user's explicit approval.**

## Quick Reference

```bash
# Initialize in existing Vite project.
pnpm dlx shadcn@latest init -d

# Add components.
pnpm dlx shadcn@latest add button card dialog
pnpm dlx shadcn@latest add @magicui/shimmer-button
pnpm dlx shadcn@latest add --all

# Preview changes before adding/updating.
pnpm dlx shadcn@latest add button --dry-run
pnpm dlx shadcn@latest add button --diff button.tsx

# Search registries.
pnpm dlx shadcn@latest search @shadcn -q "sidebar"
pnpm dlx shadcn@latest search @tailark -q "stats"

# Get component docs and example URLs.
pnpm dlx shadcn@latest docs button dialog select
```

**Named presets:** `base-nova`, `radix-nova`
**Preset codes:** Base62 strings starting with `a` (e.g. `a2r6bw`), from [ui.shadcn.com](https://ui.shadcn.com).

## Detailed References

- [references/forms.md](./references/forms.md) — FieldGroup, Field, InputGroup, ToggleGroup, FieldSet, validation states
- [references/composition.md](./references/composition.md) — Groups, overlays, Card, Tabs, Avatar, Alert, Empty, Toast, Separator, Skeleton, Badge, Button loading
- [references/icons.md](./references/icons.md) — data-icon, icon sizing, passing icons as objects
- [references/styling.md](./references/styling.md) — Semantic colors, variants, className, spacing, size, truncate, dark mode, cn(), z-index
- [references/base-vs-radix.md](./references/base-vs-radix.md) — asChild vs render, Select, ToggleGroup, Slider, Accordion
- [references/cli.md](./references/cli.md) — Commands, flags, presets, templates
- [references/customization.md](./references/customization.md) — Theming, CSS variables, extending components
