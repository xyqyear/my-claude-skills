---
name: shadcn-datatable
description: Build data tables with TanStack Table and shadcn/ui. Use when users need to create data tables, implement table sorting, filtering, pagination, row selection, column visibility, faceted filters, or work with @tanstack/react-table in a shadcn/ui project. Triggers on requests like "create a data table", "add a table with sorting", "build a filterable table", "data grid".
user-invokable: true
---

# Data Tables with TanStack Table + shadcn/ui

Build fully-featured data tables using TanStack Table v8 (headless) with shadcn/ui Table components for rendering.

## Setup

### Install dependencies

```bash
pnpm add @tanstack/react-table
```

### Install shadcn components

```bash
pnpm dlx shadcn@latest add table button checkbox dropdown-menu input select
```

For faceted filters (multi-select popover), also add:

```bash
pnpm dlx shadcn@latest add command popover badge separator
```

## File Structure

Organize data table code into three files per table:

```
app/payments/
  columns.tsx      # Column definitions (client component)
  data-table.tsx   # DataTable component (client component)
  page.tsx         # Page that fetches data and renders DataTable
```

For reusable sub-components shared across tables, place them in:

```
components/data-table/
  data-table-column-header.tsx
  data-table-pagination.tsx
  data-table-view-options.tsx
  data-table-toolbar.tsx
  data-table-faceted-filter.tsx
```

## Core Pattern

### 1. Define column definitions (`columns.tsx`)

```tsx
"use client"

import { type ColumnDef } from "@tanstack/react-table"

export type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "status",
    header: "Status",
  },
  {
    accessorKey: "email",
    header: "Email",
  },
  {
    accessorKey: "amount",
    header: "Amount",
  },
]
```

### 2. Create the DataTable component (`data-table.tsx`)

```tsx
"use client"

import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="rounded-md border">
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
                        header.getContext()
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
                      cell.getContext()
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
  )
}
```

### 3. Render on a page (`page.tsx`)

```tsx
import { columns, type Payment } from "./columns"
import { DataTable } from "./data-table"

async function getData(): Promise<Payment[]> {
  return await fetch("/api/payments").then((r) => r.json())
}

export default async function PaymentsPage() {
  const data = await getData()

  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  )
}
```

## Column Definitions

### Cell formatting

```tsx
{
  accessorKey: "amount",
  header: () => <div className="text-right">Amount</div>,
  cell: ({ row }) => {
    const amount = parseFloat(row.getValue("amount"))
    const formatted = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)
    return <div className="text-right font-medium">{formatted}</div>
  },
}
```

### Custom accessor function

When the `id` is not a direct key, use `accessorFn` and provide an explicit `id`:

```tsx
{
  id: "fullName",
  accessorFn: (row) => `${row.firstName} ${row.lastName}`,
  header: "Full Name",
}
```

### Display column (no data, UI only)

```tsx
{
  id: "actions",
  enableHiding: false,
  cell: ({ row }) => <RowActions row={row} />,
}
```

### Column with icon from data lookup

For columns where cell content is rendered from a lookup array (e.g., status icons):

```tsx
{
  accessorKey: "status",
  header: ({ column }) => (
    <DataTableColumnHeader column={column} title="Status" />
  ),
  cell: ({ row }) => {
    const status = statuses.find(
      (s) => s.value === row.getValue("status")
    )
    if (!status) return null
    return (
      <div className="flex w-[100px] items-center">
        {status.icon && (
          <status.icon className="mr-2 size-4 text-muted-foreground" />
        )}
        <span>{status.label}</span>
      </div>
    )
  },
  filterFn: (row, id, value) => {
    return value.includes(row.getValue(id))
  },
}
```

## Adding Features

All features follow the same pattern: add state, pass to `useReactTable`, add the corresponding row model.

### Sorting

Add to `data-table.tsx`:

```tsx
import {
  type SortingState,
  getSortedRowModel,
} from "@tanstack/react-table"

const [sorting, setSorting] = React.useState<SortingState>([])

const table = useReactTable({
  // ...existing options
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
  state: { sorting },
})
```

Make a column header sortable in `columns.tsx`:

```tsx
import { ArrowUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"

{
  accessorKey: "email",
  header: ({ column }) => (
    <Button
      variant="ghost"
      onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
    >
      Email
      <ArrowUpDown className="ml-2 size-4" />
    </Button>
  ),
}
```

Or use the reusable `DataTableColumnHeader` for a dropdown with Asc/Desc/Hide options:

```tsx
import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header"

{
  accessorKey: "email",
  header: ({ column }) => (
    <DataTableColumnHeader column={column} title="Email" />
  ),
}
```

### Filtering

Add to `data-table.tsx`:

```tsx
import {
  type ColumnFiltersState,
  getFilteredRowModel,
} from "@tanstack/react-table"
import { Input } from "@/components/ui/input"

const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])

const table = useReactTable({
  // ...existing options
  onColumnFiltersChange: setColumnFilters,
  getFilteredRowModel: getFilteredRowModel(),
  state: { columnFilters },
})

// Render a filter input above the table:
<Input
  placeholder="Filter emails..."
  value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
  onChange={(event) =>
    table.getColumn("email")?.setFilterValue(event.target.value)
  }
  className="max-w-sm"
/>
```

### Pagination

Add to `data-table.tsx`:

```tsx
import { getPaginationRowModel } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"

const table = useReactTable({
  // ...existing options
  getPaginationRowModel: getPaginationRowModel(),
})

// Simple pagination controls below the table:
<div className="flex items-center justify-end space-x-2 py-4">
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
```

For full pagination with page size selector and first/last buttons, use the reusable `DataTablePagination` component. See [components.md](references/components.md).

### Row Selection

Add checkbox column to `columns.tsx`:

```tsx
import { Checkbox } from "@/components/ui/checkbox"

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
}
```

Add to `data-table.tsx`:

```tsx
const [rowSelection, setRowSelection] = React.useState({})

const table = useReactTable({
  // ...existing options
  enableRowSelection: true,
  onRowSelectionChange: setRowSelection,
  state: { rowSelection },
})

// Display selection count:
<div className="text-sm text-muted-foreground">
  {table.getFilteredSelectedRowModel().rows.length} of{" "}
  {table.getFilteredRowModel().rows.length} row(s) selected.
</div>
```

### Column Visibility

Add to `data-table.tsx`:

```tsx
import { type VisibilityState } from "@tanstack/react-table"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})

const table = useReactTable({
  // ...existing options
  onColumnVisibilityChange: setColumnVisibility,
  state: { columnVisibility },
})

// Column toggle dropdown:
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline" className="ml-auto">Columns</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    {table
      .getAllColumns()
      .filter((column) => column.getCanHide())
      .map((column) => (
        <DropdownMenuCheckboxItem
          key={column.id}
          className="capitalize"
          checked={column.getIsVisible()}
          onCheckedChange={(value) => column.toggleVisibility(!!value)}
        >
          {column.id}
        </DropdownMenuCheckboxItem>
      ))}
  </DropdownMenuContent>
</DropdownMenu>
```

Or use the reusable `DataTableViewOptions` component. See [components.md](references/components.md).

## Row Actions

Add a dropdown menu column for per-row actions:

```tsx
import { MoreHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

{
  id: "actions",
  enableHiding: false,
  cell: ({ row }) => {
    const payment = row.original

    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="size-8 p-0">
            <span className="sr-only">Open menu</span>
            <MoreHorizontal className="size-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Actions</DropdownMenuLabel>
          <DropdownMenuItem
            onClick={() => navigator.clipboard.writeText(payment.id)}
          >
            Copy payment ID
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>View customer</DropdownMenuItem>
          <DropdownMenuItem>View payment details</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    )
  },
}
```

## Faceted Filters

For multi-select enum filters (e.g., status, priority), use `DataTableFacetedFilter`. This requires:

1. `getFacetedRowModel()` and `getFacetedUniqueValues()` in `useReactTable`
2. A custom `filterFn` on the column that checks array inclusion
3. Filter option arrays with `{ label, value, icon? }`

```tsx
// In useReactTable config:
getFacetedRowModel: getFacetedRowModel(),
getFacetedUniqueValues: getFacetedUniqueValues(),

// Column filterFn:
{
  accessorKey: "status",
  filterFn: (row, id, value) => value.includes(row.getValue(id)),
}

// Filter options:
const statuses = [
  { value: "backlog", label: "Backlog", icon: CircleHelp },
  { value: "todo", label: "Todo", icon: Circle },
  { value: "in_progress", label: "In Progress", icon: Timer },
  { value: "done", label: "Done", icon: CircleCheck },
  { value: "cancelled", label: "Cancelled", icon: CircleX },
]
```

For the full `DataTableFacetedFilter`, `DataTableToolbar`, and other reusable component implementations, see [components.md](references/components.md).

For the complete TanStack Table API reference (all types, methods, custom sort/filter functions, server-side patterns, expanding, grouping, column resizing, and column pinning), see [tanstack-api.md](references/tanstack-api.md).
