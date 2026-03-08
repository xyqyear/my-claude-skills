# shadcn/ui Integration

Optional UI feature for the fullstack scaffold. Read this file when the user requests shadcn/ui.

shadcn/ui is **not** a traditional component library. Components are copied directly into your project via CLI — you own the source code entirely. Built on Radix UI primitives (accessibility + behavior) and styled with Tailwind CSS.

## Installation

### Prerequisites

Before running `shadcn init`, the base scaffold must have:

1. **tsconfig.json** with path aliases (shadcn CLI reads this file, not `tsconfig.app.json`):

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "files": [],
  "references": [{ "path": "./tsconfig.app.json" }]
}
```

2. **Tailwind CSS v4** fully configured — `@tailwindcss/vite` plugin in `vite.config.ts` and `@import "tailwindcss"` in `src/index.css` (both are part of the base scaffold's Step 3).

### Initialize

```bash
cd frontend
pnpm add -D @types/node
pnpm dlx shadcn@latest init -d
```

The `-d` flag uses defaults (style: new-york, neutral base color, CSS variables enabled). The CLI auto-detects Vite + Tailwind CSS v4 and creates:

- `components.json` — project configuration (`rsc: false` for Vite, `tailwind.config: ""` for v4)
- `src/lib/utils.ts` — the `cn()` helper (clsx + tailwind-merge)
- Updates `src/index.css` with CSS variables and theme directives
- Installs dependencies: `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`, `tw-animate-css`

Add components individually:

```bash
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add card dialog sheet
pnpm dlx shadcn@latest add sidebar
```

Components are placed in `src/components/ui/`. Each `add` command also installs the required Radix UI dependency automatically.

## Dark Mode

Dark mode uses a class-based approach — toggling the `dark` class on `<html>`.

### ThemeProvider

Create `src/components/theme-provider.tsx`:

```tsx
import { createContext, useContext, useEffect, useState } from "react";

type Theme = "dark" | "light" | "system";

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
};

type ThemeProviderState = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
};

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "vite-ui-theme",
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme,
  );

  useEffect(() => {
    const root = window.document.documentElement;

    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
      return;
    }

    root.classList.add(theme);
  }, [theme]);

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme);
      setTheme(theme);
    },
  };

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
```

### ModeToggle Component

Requires `button` and `dropdown-menu` components:

```bash
pnpm dlx shadcn@latest add button dropdown-menu
```

Create `src/components/mode-toggle.tsx`:

```tsx
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme } from "@/components/theme-provider";

export function ModeToggle() {
  const { setTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

### Wrapping the App

Add `ThemeProvider` to `src/main.tsx`, wrapping everything inside `QueryClientProvider`:

```tsx
import { ThemeProvider } from "@/components/theme-provider";

// Inside the render tree:
<QueryClientProvider client={queryClient}>
  <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </ThemeProvider>
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

## Component Directory Structure

After adding components, the frontend structure expands to:

```
frontend/src/
├── components/
│   ├── ui/                       # shadcn/ui components (generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── select.tsx
│   │   ├── sheet.tsx
│   │   ├── sidebar.tsx
│   │   ├── sonner.tsx
│   │   ├── table.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   ├── theme-provider.tsx        # Dark mode context
│   ├── mode-toggle.tsx           # Theme switcher
│   └── app-sidebar.tsx           # Application sidebar
├── lib/
│   ├── api.ts                    # ky HTTP client
│   ├── query-keys.ts             # Query key factory
│   └── utils.ts                  # cn() utility (generated by shadcn init)
└── ...
```

## Key Components

### Button

Six variants: `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`. Four sizes: `default`, `sm`, `lg`, `icon`.

```tsx
import { Button } from "@/components/ui/button";

<Button variant="default">Save</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><PlusIcon /></Button>

// With icon
<Button>
  <Mail />
  Login with Email
</Button>

// As a link (using asChild to render as <a>)
<Button asChild>
  <a href="/dashboard">Go to Dashboard</a>
</Button>

// Loading state
<Button disabled>
  <Loader2 className="animate-spin" />
  Please wait
</Button>
```

### Card

```tsx
import {
  Card, CardAction, CardContent, CardDescription,
  CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
    <CardAction>
      <Button variant="outline" size="sm">Action</Button>
    </CardAction>
  </CardHeader>
  <CardContent>
    <p>Card Content</p>
  </CardContent>
  <CardFooter>
    <p>Card Footer</p>
  </CardFooter>
</Card>
```

### Dialog

```tsx
import {
  Dialog, DialogTrigger, DialogContent, DialogHeader,
  DialogTitle, DialogDescription, DialogFooter, DialogClose,
} from "@/components/ui/dialog";

<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">Edit Profile</Button>
  </DialogTrigger>
  <DialogContent className="sm:max-w-[425px]">
    <DialogHeader>
      <DialogTitle>Edit profile</DialogTitle>
      <DialogDescription>
        Make changes to your profile here.
      </DialogDescription>
    </DialogHeader>
    <div className="grid gap-4 py-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="name" className="text-right">Name</Label>
        <Input id="name" defaultValue="John Doe" className="col-span-3" />
      </div>
    </div>
    <DialogFooter>
      <Button type="submit">Save changes</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Sheet (Slide-in Panel)

Supports `side` prop: `top`, `right`, `bottom`, `left`.

```tsx
import {
  Sheet, SheetClose, SheetContent, SheetDescription,
  SheetFooter, SheetHeader, SheetTitle, SheetTrigger,
} from "@/components/ui/sheet";

<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline">Open</Button>
  </SheetTrigger>
  <SheetContent side="right">
    <SheetHeader>
      <SheetTitle>Edit Profile</SheetTitle>
      <SheetDescription>Make changes to your profile.</SheetDescription>
    </SheetHeader>
    {/* Form content */}
    <SheetFooter>
      <SheetClose asChild>
        <Button type="submit">Save</Button>
      </SheetClose>
    </SheetFooter>
  </SheetContent>
</Sheet>
```

### Dropdown Menu

```tsx
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuGroup,
  DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuGroup>
      <DropdownMenuItem>Profile</DropdownMenuItem>
      <DropdownMenuItem>Billing</DropdownMenuItem>
      <DropdownMenuItem>Settings</DropdownMenuItem>
    </DropdownMenuGroup>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Log out</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### Input, Select, Checkbox, Switch

```tsx
// Input
import { Input } from "@/components/ui/input";
<Input type="email" placeholder="Email" />

// Select
import {
  Select, SelectContent, SelectGroup, SelectItem,
  SelectLabel, SelectTrigger, SelectValue,
} from "@/components/ui/select";

<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Select a fruit" />
  </SelectTrigger>
  <SelectContent>
    <SelectGroup>
      <SelectLabel>Fruits</SelectLabel>
      <SelectItem value="apple">Apple</SelectItem>
      <SelectItem value="banana">Banana</SelectItem>
    </SelectGroup>
  </SelectContent>
</Select>

// Checkbox
import { Checkbox } from "@/components/ui/checkbox";
<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <label htmlFor="terms">Accept terms</label>
</div>

// Switch
import { Switch } from "@/components/ui/switch";
<div className="flex items-center space-x-2">
  <Switch id="airplane-mode" />
  <label htmlFor="airplane-mode">Airplane Mode</label>
</div>
```

### Alert, Badge, Avatar

```tsx
// Alert — variants: default, destructive
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
<Alert>
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>You can add components to your app.</AlertDescription>
</Alert>

// Badge — variants: default, secondary, destructive, outline
import { Badge } from "@/components/ui/badge";
<Badge>Badge</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>

// Avatar
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>
```

### Tabs

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">Account settings...</TabsContent>
  <TabsContent value="password">Password settings...</TabsContent>
</Tabs>
```

Content stays mounted across tab switches (preserves form state). Supports horizontal and vertical orientations.

### Accordion

```tsx
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion";

<Accordion defaultValue={["item-1"]}>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>Yes. WAI-ARIA compliant.</AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-2">
    <AccordionTrigger>Is it styled?</AccordionTrigger>
    <AccordionContent>Yes. Tailwind CSS styles.</AccordionContent>
  </AccordionItem>
</Accordion>
```

### Breadcrumb

```tsx
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/products">Products</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Current Page</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

### Command (Command Palette / Combobox)

Built on the `cmdk` library. Provides fuzzy search, keyboard navigation, and grouping.

```tsx
import {
  Command, CommandEmpty, CommandGroup, CommandInput,
  CommandItem, CommandList, CommandSeparator,
} from "@/components/ui/command";

<Command className="max-w-sm rounded-lg border">
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
      <CommandItem>Search Emoji</CommandItem>
      <CommandItem>Calculator</CommandItem>
    </CommandGroup>
    <CommandSeparator />
    <CommandGroup heading="Settings">
      <CommandItem>Profile</CommandItem>
      <CommandItem>Billing</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

As a `Cmd+K` dialog:

```tsx
import { CommandDialog } from "@/components/ui/command";

const [open, setOpen] = useState(false);

useEffect(() => {
  const down = (e: KeyboardEvent) => {
    if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      setOpen((open) => !open);
    }
  };
  document.addEventListener("keydown", down);
  return () => document.removeEventListener("keydown", down);
}, []);

<CommandDialog open={open} onOpenChange={setOpen}>
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    {/* same structure */}
  </CommandList>
</CommandDialog>
```

## Toast Notifications (Sonner)

Sonner is the recommended toast library for shadcn/ui.

### Installation

```bash
pnpm dlx shadcn@latest add sonner
```

### Setup

Add `<Toaster />` to the root layout in `src/main.tsx`:

```tsx
import { Toaster } from "@/components/ui/sonner";

// Inside the render tree, after the router:
<ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
  <BrowserRouter>
    <App />
  </BrowserRouter>
  <Toaster />
</ThemeProvider>
```

### Usage

```tsx
import { toast } from "sonner";

// Basic
toast("Event has been created.");

// Success
toast.success("Settings saved successfully.");

// Error
toast.error("Something went wrong.");

// Warning
toast.warning("This action cannot be undone.");

// Info
toast.info("New update available.");

// With description
toast("Event created", {
  description: "Your event has been scheduled for tomorrow.",
});

// Action button
toast("File uploaded", {
  action: { label: "Undo", onClick: () => console.log("Undo!") },
});

// Promise (auto-updates based on promise state)
toast.promise(myAsyncFunction(), {
  loading: "Saving...",
  success: (data) => `${data.name} has been added`,
  error: "Failed to save.",
});
```

### Notification in Mutations

Use Sonner instead of Ant Design's message API:

```typescript
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { itemApi } from "@/hooks/api/itemApi";
import { queryKeys } from "@/lib/query-keys";

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: itemApi.create,
    onSuccess: () => {
      toast.success("Item created");
      queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
    onError: (error) => {
      toast.error(`Failed to create item: ${error.message}`);
    },
  });
}
```

## Forms: React Hook Form + Zod

### Installation

```bash
pnpm add react-hook-form @hookform/resolvers zod
pnpm dlx shadcn@latest add input label
```

### Pattern

shadcn/ui uses the `Field` component family with React Hook Form's `Controller`. This pattern is form-library-agnostic and gives full control over markup.

```tsx
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card, CardContent, CardDescription, CardFooter,
  CardHeader, CardTitle,
} from "@/components/ui/card";

const formSchema = z.object({
  title: z
    .string()
    .min(2, "Title must be at least 2 characters.")
    .max(200, "Title must be at most 200 characters."),
  description: z
    .string()
    .max(1000, "Description must be at most 1000 characters.")
    .optional(),
});

export function ItemForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { title: "", description: "" },
  });

  function onSubmit(data: z.infer<typeof formSchema>) {
    toast.success("Item created!");
    console.log(data);
  }

  return (
    <Card className="w-full sm:max-w-md">
      <CardHeader>
        <CardTitle>Create Item</CardTitle>
        <CardDescription>Add a new item to your collection.</CardDescription>
      </CardHeader>
      <CardContent>
        <form
          id="item-form"
          onSubmit={form.handleSubmit(onSubmit)}
          className="space-y-4"
        >
          <Controller
            name="title"
            control={form.control}
            render={({ field, fieldState }) => (
              <div className="space-y-2">
                <label htmlFor={field.name} className="text-sm font-medium">
                  Title
                </label>
                <Input
                  {...field}
                  id={field.name}
                  aria-invalid={fieldState.invalid}
                  placeholder="Item title"
                />
                {fieldState.error && (
                  <p className="text-sm text-destructive">
                    {fieldState.error.message}
                  </p>
                )}
              </div>
            )}
          />
          <Controller
            name="description"
            control={form.control}
            render={({ field, fieldState }) => (
              <div className="space-y-2">
                <label htmlFor={field.name} className="text-sm font-medium">
                  Description
                </label>
                <Input
                  {...field}
                  id={field.name}
                  aria-invalid={fieldState.invalid}
                  placeholder="Optional description"
                />
                {fieldState.error && (
                  <p className="text-sm text-destructive">
                    {fieldState.error.message}
                  </p>
                )}
              </div>
            )}
          />
        </form>
      </CardContent>
      <CardFooter>
        <Button type="submit" form="item-form">
          Create
        </Button>
      </CardFooter>
    </Card>
  );
}
```

Key points:

- Use `Controller` from React Hook Form to bridge field state with shadcn/ui inputs
- `zodResolver(formSchema)` connects Zod validation to React Hook Form
- `fieldState.invalid` and `fieldState.error` drive error display
- Use `aria-invalid={fieldState.invalid}` on inputs for accessibility
- For Select components, use `field.value` and `field.onChange` instead of spreading `{...field}`

## Data Table (TanStack Table)

### Installation

```bash
pnpm dlx shadcn@latest add table checkbox
pnpm add @tanstack/react-table
```

### Column Definitions

Create `src/components/data-table/columns.tsx`:

```tsx
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Item } from "@/types/item";

export const columns: ColumnDef<Item>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "title",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Title
        <ArrowUpDown className="ml-2 size-4" />
      </Button>
    ),
    cell: ({ row }) => <div>{row.getValue("title")}</div>,
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => (
      <div className="text-muted-foreground">
        {row.getValue("description") || "—"}
      </div>
    ),
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const item = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal />
              <span className="sr-only">Open menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(String(item.id))}
            >
              Copy ID
            </DropdownMenuItem>
            <DropdownMenuItem>Edit</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
```

### DataTable Component

Create `src/components/data-table/data-table.tsx`:

```tsx
import * as React from "react";
import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Table, TableBody, TableCell, TableHead,
  TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] =
    React.useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: { sorting, columnFilters, columnVisibility, rowSelection },
  });

  return (
    <div className="w-full">
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter by title..."
          value={(table.getColumn("title")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("title")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
      </div>
      <div className="overflow-hidden rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-between space-x-2 py-4">
        <div className="text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
```

### Using with TanStack Query

Connect the DataTable to server data via query hooks:

```tsx
import { useItems } from "@/hooks/queries/useItemQueries";
import { DataTable } from "@/components/data-table/data-table";
import { columns } from "@/components/data-table/columns";

export default function ItemsPage() {
  const { data, isPending } = useItems();

  if (isPending) return <div>Loading...</div>;

  return <DataTable columns={columns} data={data ?? []} />;
}
```

### Server-Side Pagination

For large datasets, switch to manual (server-side) pagination:

```tsx
const table = useReactTable({
  data,
  columns,
  manualPagination: true,
  manualSorting: true,
  manualFiltering: true,
  pageCount: serverPageCount,
  getCoreRowModel: getCoreRowModel(),
  onSortingChange: setSorting,
  onPaginationChange: setPagination,
  state: { sorting, pagination },
});
```

Then pass the sorting/pagination state to TanStack Query as query key parameters so refetching happens automatically when the user sorts or paginates.

## Sidebar

The Sidebar component provides a composable, collapsible navigation panel. Install with:

```bash
pnpm dlx shadcn@latest add sidebar
```

### Component Hierarchy

```
SidebarProvider          # Context wrapper (manages state)
├── Sidebar              # Main container
│   ├── SidebarHeader    # Sticky top (logo, team switcher)
│   ├── SidebarContent   # Scrollable middle
│   │   └── SidebarGroup
│   │       ├── SidebarGroupLabel
│   │       ├── SidebarGroupAction
│   │       └── SidebarGroupContent
│   │           └── SidebarMenu
│   │               └── SidebarMenuItem
│   │                   ├── SidebarMenuButton
│   │                   ├── SidebarMenuAction
│   │                   ├── SidebarMenuBadge
│   │                   └── SidebarMenuSub
│   │                       └── SidebarMenuSubItem
│   │                           └── SidebarMenuSubButton
│   ├── SidebarFooter    # Sticky bottom (user profile)
│   └── SidebarRail      # Interactive edge rail for toggling
├── SidebarInset         # Main content wrapper (for variant="inset")
└── SidebarTrigger       # Toggle button
```

### Sidebar Props

| Prop | Type | Options | Default |
|------|------|---------|---------|
| `side` | `string` | `"left"` \| `"right"` | `"left"` |
| `variant` | `string` | `"sidebar"` \| `"floating"` \| `"inset"` | `"sidebar"` |
| `collapsible` | `string` | `"offcanvas"` \| `"icon"` \| `"none"` | `"offcanvas"` |

### SidebarProvider Props

| Prop | Type | Description |
|------|------|-------------|
| `defaultOpen` | `boolean` | Default open state |
| `open` | `boolean` | Controlled open state |
| `onOpenChange` | `(open: boolean) => void` | State change callback |
| `style` | `CSSProperties` | Custom width via `--sidebar-width`, `--sidebar-width-mobile` |

### useSidebar Hook

```tsx
import { useSidebar } from "@/components/ui/sidebar";

const {
  state,          // "expanded" | "collapsed"
  open,           // boolean (desktop)
  setOpen,        // (open: boolean) => void
  openMobile,     // boolean (mobile)
  setOpenMobile,  // (open: boolean) => void
  isMobile,       // boolean
  toggleSidebar,  // () => void (works for both desktop and mobile)
} = useSidebar();
```

Keyboard shortcut: `Cmd+B` (Mac) / `Ctrl+B` (Windows).

On mobile (< 768px), the Sidebar automatically renders as a Sheet (drawer overlay).

## Layout Templates

### Layout 1: Dashboard with Sidebar (Recommended)

The standard admin dashboard layout. Uses `SidebarProvider` + `SidebarInset` for a sidebar with an inset content area.

Install required components:

```bash
pnpm dlx shadcn@latest add sidebar breadcrumb separator
```

Create `src/components/app-sidebar.tsx`:

```tsx
import { Link, useLocation } from "react-router";
import {
  LayoutDashboard, ListTodo, Settings, type LucideIcon,
} from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup,
  SidebarGroupContent, SidebarGroupLabel, SidebarHeader,
  SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail,
} from "@/components/ui/sidebar";

type NavItem = { title: string; url: string; icon: LucideIcon };

const navMain: NavItem[] = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Items", url: "/items", icon: ListTodo },
  { title: "Settings", url: "/settings", icon: Settings },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  A
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">My App</span>
                  <span className="truncate text-xs text-muted-foreground">
                    Dashboard
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navMain.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={location.pathname === item.url}
                  >
                    <Link to={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter />
      <SidebarRail />
    </Sidebar>
  );
}
```

Create `src/components/MainLayout.tsx`:

```tsx
import { Outlet } from "react-router";
import {
  SidebarInset, SidebarProvider, SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { AppSidebar } from "@/components/app-sidebar";

export default function MainLayout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/">Home</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Dashboard</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <main className="flex flex-1 flex-col gap-4 p-4 md:gap-6 md:p-6">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
```

Update `src/App.tsx`:

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

#### Sidebar Variant: Collapsible to Icons

For a sidebar that collapses to show only icons instead of hiding completely:

```tsx
<Sidebar collapsible="icon">
  {/* same content */}
</Sidebar>
```

When collapsed, `SidebarMenuButton` shrinks to `size-8` with `overflow-hidden`, so only the leading icon remains visible and text is clipped automatically. To hide an entire `SidebarGroup` or a custom element that lives **outside** a `SidebarMenuButton`, add `className="group-data-[collapsible=icon]:hidden"`. Do not apply this class to children **inside** a `SidebarMenuButton` — the button's built-in overflow clipping already handles them.

If the button contains a sized icon container (e.g. a `size-8` div in the header), add `shrink-0` so it holds its dimensions during the collapse transition instead of getting squeezed by flex.

#### Sidebar Variant: Floating

A sidebar that floats with a visible border and rounded corners:

```tsx
<Sidebar variant="floating">
  {/* same content */}
</Sidebar>
```

#### Custom Sidebar Width

```tsx
<SidebarProvider
  style={{
    "--sidebar-width": "20rem",
    "--sidebar-width-mobile": "20rem",
  } as React.CSSProperties}
>
```

#### Collapsible Groups

```tsx
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";

<Collapsible defaultOpen className="group/collapsible">
  <SidebarGroup>
    <SidebarGroupLabel asChild>
      <CollapsibleTrigger>
        Help
        <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
      </CollapsibleTrigger>
    </SidebarGroupLabel>
    <CollapsibleContent>
      <SidebarGroupContent>
        <SidebarMenu>
          {/* menu items */}
        </SidebarMenu>
      </SidebarGroupContent>
    </CollapsibleContent>
  </SidebarGroup>
</Collapsible>
```

#### Submenus

```tsx
<SidebarMenuItem>
  <SidebarMenuButton>
    <FileText />
    <span>Documents</span>
  </SidebarMenuButton>
  <SidebarMenuSub>
    <SidebarMenuSubItem>
      <SidebarMenuSubButton asChild>
        <Link to="/docs/getting-started">Getting Started</Link>
      </SidebarMenuSubButton>
    </SidebarMenuSubItem>
    <SidebarMenuSubItem>
      <SidebarMenuSubButton asChild>
        <Link to="/docs/api">API Reference</Link>
      </SidebarMenuSubButton>
    </SidebarMenuSubItem>
  </SidebarMenuSub>
</SidebarMenuItem>
```

#### Menu with Badge

```tsx
<SidebarMenuItem>
  <SidebarMenuButton>
    <Inbox />
    <span>Inbox</span>
  </SidebarMenuButton>
  <SidebarMenuBadge>24</SidebarMenuBadge>
</SidebarMenuItem>
```

#### Menu with Action Button

```tsx
<SidebarMenuItem>
  <SidebarMenuButton asChild>
    <Link to="/projects"><Folder /><span>Projects</span></Link>
  </SidebarMenuButton>
  <SidebarMenuAction>
    <Plus /> <span className="sr-only">Add Project</span>
  </SidebarMenuAction>
</SidebarMenuItem>
```

### Layout 2: Centered Content (Auth Pages)

Simple centered layout for login/register pages — no sidebar.

```tsx
// src/components/AuthLayout.tsx
import { Outlet } from "react-router";

export default function AuthLayout() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <Outlet />
      </div>
    </div>
  );
}
```

Login page example:

```tsx
import { Button } from "@/components/ui/button";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Login to your account</CardTitle>
        <CardDescription>
          Enter your email below to login to your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <Input id="email" type="email" placeholder="m@example.com" required />
          </div>
          <div className="space-y-2">
            <div className="flex items-center">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <a
                href="#"
                className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
              >
                Forgot your password?
              </a>
            </div>
            <Input id="password" type="password" required />
          </div>
          <Button type="submit" className="w-full">
            Login
          </Button>
          <Button variant="outline" type="button" className="w-full">
            Login with Google
          </Button>
          <div className="text-center text-sm">
            Don't have an account?{" "}
            <a href="#" className="underline underline-offset-4">
              Sign up
            </a>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

### Layout 3: Two-Column Auth (Split Screen)

Login form on one side, cover image on the other:

```tsx
import { GalleryVerticalEnd } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="#" className="flex items-center gap-2 font-medium">
            <div className="flex size-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <GalleryVerticalEnd className="size-4" />
            </div>
            Acme Inc.
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            {/* Login form */}
          </div>
        </div>
      </div>
      <div className="relative hidden bg-muted lg:block">
        <img
          src="/placeholder.svg"
          alt="Image"
          className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
        />
      </div>
    </div>
  );
}
```

### Layout 4: Settings Page (Tabs)

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      <p className="text-muted-foreground">
        Manage your account settings and preferences.
      </p>
      <Tabs defaultValue="general" className="mt-6">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>
        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Configure your general preferences.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Settings form */}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security</CardTitle>
              <CardDescription>
                Manage your security settings.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Security form */}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>
                Configure notification preferences.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Notification preferences */}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### Layout 5: Marketing / Landing Page

No sidebar. Uses Tailwind CSS layout utilities with shadcn/ui components for hero sections, feature grids, FAQs, and CTAs.

```tsx
import { Button } from "@/components/ui/button";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from "@/components/ui/card";
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion";

export default function LandingPage() {
  return (
    <div className="flex min-h-svh flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <span className="text-xl font-bold">My App</span>
          <nav className="hidden gap-6 md:flex">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground">
              Features
            </a>
            <a href="#faq" className="text-sm text-muted-foreground hover:text-foreground">
              FAQ
            </a>
          </nav>
          <Button>Get Started</Button>
        </div>
      </header>

      {/* Hero */}
      <section className="flex flex-col items-center justify-center gap-6 px-4 py-24 text-center md:px-6 md:py-32">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          Build something amazing
        </h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          A modern full-stack application built with FastAPI and React.
        </p>
        <div className="flex gap-4">
          <Button size="lg">Get Started</Button>
          <Button size="lg" variant="outline">Learn More</Button>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="mb-12 text-center text-3xl font-bold">Features</h2>
        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Fast Backend</CardTitle>
              <CardDescription>Powered by FastAPI with async SQLAlchemy.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                High-performance async Python backend.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Modern Frontend</CardTitle>
              <CardDescription>React + TypeScript + Tailwind CSS.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Type-safe, responsive, and beautiful.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Production Ready</CardTitle>
              <CardDescription>Docker, CI/CD, and monitoring.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Deploy anywhere with confidence.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="mb-12 text-center text-3xl font-bold">FAQ</h2>
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>What is this?</AccordionTrigger>
            <AccordionContent>
              A full-stack web application scaffold.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-2">
            <AccordionTrigger>Is it free?</AccordionTrigger>
            <AccordionContent>
              Yes. It is open source and free to use.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-muted-foreground sm:px-6 lg:px-8">
          Built with FastAPI + React + shadcn/ui
        </div>
      </footer>
    </div>
  );
}
```

## Multiple Layouts with React Router

Use React Router's nested routes with the `Outlet` pattern to switch between layouts:

```tsx
// src/App.tsx
import { Route, Routes } from "react-router";
import { lazy, Suspense } from "react";
import MainLayout from "@/components/MainLayout";
import AuthLayout from "@/components/AuthLayout";

const Home = lazy(() => import("@/pages/Home"));
const Items = lazy(() => import("@/pages/Items"));
const Settings = lazy(() => import("@/pages/Settings"));
const Login = lazy(() => import("@/pages/Login"));

export default function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        {/* Dashboard routes — sidebar layout */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/items" element={<Items />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        {/* Auth routes — centered layout */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
```

## Tailwind CSS v4 Notes

Key differences from Tailwind v3 that affect this setup:

- **No `tailwind.config.js`**: all configuration lives in CSS via `@theme` directives
- **No `postcss.config.js`**: uses the `@tailwindcss/vite` plugin instead
- **Import syntax**: `@import "tailwindcss"` (not `@tailwind base/components/utilities`)
- **Animation**: `tw-animate-css` replaces the deprecated `tailwindcss-animate` plugin
- **Colors**: OKLCH format instead of HSL
- **Dark mode**: `@custom-variant dark (&:is(.dark *))` in CSS (not `darkMode: "class"` in config)
- **Border default**: `currentColor` (was `gray-200` in v3)
- **Ring width**: `ring` = 1px (was 3px in v3), use `ring-3` for old behavior

## Vite Build Configuration

shadcn/ui components are individually imported and tree-shaken. No special chunk splitting is needed (unlike Ant Design which requires manual chunking). The build output is naturally small because you only add components you use.

If the bundle grows, add manual chunking for Radix UI:

```typescript
// vite.config.ts — add to defineConfig
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        "radix-ui": ["radix-ui"],
      },
    },
  },
},
```

## Available Component List

Components are added individually via `pnpm dlx shadcn@latest add <name>`:

**Layout**: Sidebar, Separator, Resizable, Scroll Area, Collapsible, Aspect Ratio
**Navigation**: Navigation Menu, Breadcrumb, Pagination, Tabs, Menubar
**Data Display**: Table, Card, Avatar, Badge, Alert, Accordion, Carousel, Tooltip, Hover Card
**Data Input**: Input, Textarea, Select, Checkbox, Switch, Slider, Radio Group, Toggle, Toggle Group, Calendar, Date Picker, Input OTP, Combobox
**Feedback**: Dialog, Alert Dialog, Sheet, Drawer, Dropdown Menu, Context Menu, Command, Popover, Sonner (toast), Progress, Skeleton, Spinner
**Typography**: Label, Kbd

Full list: https://ui.shadcn.com/docs/components

## Official Blocks

Pre-built page templates that can be installed directly:

```bash
pnpm dlx shadcn@latest add sidebar-07     # Collapsible icon sidebar
pnpm dlx shadcn@latest add login-01       # Simple centered login
pnpm dlx shadcn@latest add dashboard-01   # Full dashboard with charts
```

Available blocks:
- **Dashboard**: `dashboard-01` (sidebar + charts + data table)
- **Sidebar**: `sidebar-01` through `sidebar-16` (16 variants: simple, collapsible, floating, inset, dual, with calendar, file tree, etc.)
- **Login**: `login-01` through `login-05` (centered, split-screen, muted background, etc.)
- **Signup**: `signup-01` through `signup-05`

Browse all blocks: https://ui.shadcn.com/blocks
