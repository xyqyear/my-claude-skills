# TanStack Table API Reference

Complete API reference for `@tanstack/react-table` v8.

## Core Types

```typescript
import {
  // Core
  type ColumnDef,
  type Table,
  type Row,
  type Column,
  type Cell,
  type Header,
  type HeaderGroup,
  type CellContext,
  flexRender,
  getCoreRowModel,
  useReactTable,
  createColumnHelper,

  // Feature Row Models
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getExpandedRowModel,
  getGroupedRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,

  // State Types
  type SortingState,
  type ColumnFiltersState,
  type VisibilityState,
  type RowSelectionState,
  type ExpandedState,
  type ColumnOrderState,
  type ColumnPinningState,
  type PaginationState,
  type ColumnResizeMode,
  type ColumnResizeDirection,
  type SortingFn,
  type FilterFn,
} from "@tanstack/react-table"
```

## ColumnDef Options

| Option | Type | Description |
|--------|------|-------------|
| `id` | `string` | Unique ID (auto-derived from `accessorKey`) |
| `accessorKey` | `string` | Key in data object (dot notation supported) |
| `accessorFn` | `(row: TData) => TValue` | Custom accessor (requires `id`) |
| `header` | `string \| ((props) => ReactNode)` | Header renderer |
| `cell` | `string \| ((props: CellContext) => ReactNode)` | Cell renderer |
| `footer` | `string \| ((props) => ReactNode)` | Footer renderer |
| `columns` | `ColumnDef[]` | Sub-columns for header groups |
| `meta` | `any` | Custom metadata via `column.columnDef.meta` |
| `enableSorting` | `boolean` | Enable sorting (default: `true`) |
| `enableFiltering` | `boolean` | Enable filtering |
| `enableHiding` | `boolean` | Enable hiding (default: `true`) |
| `enableResizing` | `boolean` | Enable resizing |
| `sortingFn` | `SortingFn \| string` | Custom or built-in sort function |
| `sortDescFirst` | `boolean` | Start sort descending |
| `filterFn` | `FilterFn \| string` | Custom or built-in filter function |
| `size` | `number` | Default width (default: 150) |
| `minSize` | `number` | Min width (default: 20) |
| `maxSize` | `number` | Max width |

## CellContext Properties

The `cell` render function receives:

```typescript
{
  table,        // Table instance
  row,          // Row instance (access row.original for raw data)
  column,       // Column instance
  cell,         // Cell instance
  getValue(),   // Shortcut for cell.getValue()
  renderValue() // getValue() with fallback for undefined
}
```

## useReactTable Options

```typescript
const table = useReactTable({
  data,                                  // TData[] (must be stable reference)
  columns,                               // ColumnDef[] (must be stable reference)
  getCoreRowModel: getCoreRowModel(),    // Required
  getRowId: (row) => row.id,             // Custom row ID (recommended)
  defaultColumn: { size: 200 },          // Defaults for all columns

  // Feature row models (add as needed):
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  getGroupedRowModel: getGroupedRowModel(),
  getFacetedRowModel: getFacetedRowModel(),
  getFacetedUniqueValues: getFacetedUniqueValues(),
  getFacetedMinMaxValues: getFacetedMinMaxValues(),

  // State (controlled):
  state: { sorting, columnFilters, columnVisibility, rowSelection, pagination },

  // State change handlers:
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onColumnVisibilityChange: setColumnVisibility,
  onRowSelectionChange: setRowSelection,
  onPaginationChange: setPagination,

  // Feature options:
  enableRowSelection: true,              // boolean | (row) => boolean
  enableMultiRowSelection: true,         // boolean | (row) => boolean
  enableSorting: true,                   // global sort toggle
  enableMultiSort: true,                 // shift+click multi-sort
  enableSortingRemoval: true,            // allow clearing sort
  manualSorting: false,                  // server-side sorting
  manualFiltering: false,               // server-side filtering
  manualPagination: false,              // server-side pagination
  pageCount: -1,                         // required for manualPagination
  autoResetPageIndex: true,              // reset to page 0 on sort/filter
  columnResizeMode: 'onEnd',            // 'onChange' | 'onEnd'
  columnResizeDirection: 'ltr',         // 'ltr' | 'rtl'
  globalFilterFn: 'includesString',      // global filter function
})
```

## Table Instance Methods

### Core

| Method | Returns | Description |
|--------|---------|-------------|
| `getHeaderGroups()` | `HeaderGroup[]` | Header groups for `<thead>` |
| `getFooterGroups()` | `HeaderGroup[]` | Footer groups for `<tfoot>` |
| `getRowModel()` | `RowModel` | Final row model (all features applied) |
| `getAllColumns()` | `Column[]` | All columns including hidden |
| `getAllLeafColumns()` | `Column[]` | All leaf columns |
| `getVisibleLeafColumns()` | `Column[]` | Only visible leaf columns |
| `getColumn(id)` | `Column \| undefined` | Get column by ID |
| `getState()` | `TableState` | Full state object |

### Sorting

| Method | Description |
|--------|-------------|
| `setSorting(updater)` | Set sorting state |
| `resetSorting()` | Reset to initial sorting |
| `getSortedRowModel()` | Row model after sorting |

### Filtering

| Method | Description |
|--------|-------------|
| `setColumnFilters(updater)` | Set column filter state |
| `resetColumnFilters()` | Reset all column filters |
| `setGlobalFilter(value)` | Set global filter value |
| `resetGlobalFilter()` | Reset global filter |
| `getFilteredRowModel()` | Row model after filtering |

### Pagination

| Method | Description |
|--------|-------------|
| `setPageIndex(index)` | Go to specific page |
| `setPageSize(size)` | Set page size |
| `previousPage()` | Go to previous page |
| `nextPage()` | Go to next page |
| `firstPage()` | Go to first page |
| `lastPage()` | Go to last page |
| `getCanPreviousPage()` | Whether previous page exists |
| `getCanNextPage()` | Whether next page exists |
| `getPageCount()` | Total page count |
| `getRowCount()` | Total row count |

### Row Selection

| Method | Description |
|--------|-------------|
| `toggleAllRowsSelected(value?)` | Select/deselect all rows |
| `toggleAllPageRowsSelected(value?)` | Select/deselect current page |
| `getIsAllRowsSelected()` | All rows selected |
| `getIsAllPageRowsSelected()` | All page rows selected |
| `getIsSomeRowsSelected()` | Some rows selected |
| `getIsSomePageRowsSelected()` | Some page rows selected |
| `getSelectedRowModel()` | Selected rows model |
| `getFilteredSelectedRowModel()` | Filtered selected rows |
| `getToggleAllRowsSelectedHandler()` | Event handler for "select all" |
| `getToggleAllPageRowsSelectedHandler()` | Event handler for "select all on page" |

### Column Visibility

| Method | Description |
|--------|-------------|
| `getIsAllColumnsVisible()` | All columns visible |
| `getToggleAllColumnsVisibilityHandler()` | Event handler for "show all" |

## Column Instance Methods

| Method | Description |
|--------|-------------|
| `getCanSort()` | Whether column can be sorted |
| `getIsSorted()` | `'asc'`, `'desc'`, or `false` |
| `toggleSorting(desc?, isMulti?)` | Toggle sort direction |
| `getToggleSortingHandler()` | Click handler for sorting |
| `getCanFilter()` | Whether column can be filtered |
| `getFilterValue()` | Current filter value |
| `setFilterValue(value)` | Set filter value |
| `getCanHide()` | Whether column can be hidden |
| `getIsVisible()` | Whether column is visible |
| `toggleVisibility(value?)` | Toggle visibility |
| `getToggleVisibilityHandler()` | Checkbox handler |
| `getSize()` | Current column width |
| `getCanResize()` | Whether column can be resized |
| `getIsResizing()` | Whether currently resizing |
| `resetSize()` | Reset to original size |
| `getFacetedUniqueValues()` | `Map<value, count>` of unique values |
| `getFacetedMinMaxValues()` | `[min, max]` for numeric columns |

## Row Instance Properties and Methods

| Property/Method | Description |
|--------|-------------|
| `original` | The original data object |
| `id` | Row ID |
| `index` | Row index |
| `depth` | Nesting depth (0 = root) |
| `subRows` | Array of sub-row objects |
| `getVisibleCells()` | Visible cells in this row |
| `getAllCells()` | All cells in this row |
| `getIsSelected()` | Whether row is selected |
| `getCanSelect()` | Whether row can be selected |
| `toggleSelected(value?)` | Toggle selection |
| `getToggleSelectedHandler()` | Checkbox handler |
| `getIsExpanded()` | Whether row is expanded |
| `getCanExpand()` | Whether row can expand |
| `toggleExpanded(value?)` | Toggle expansion |
| `getToggleExpandedHandler()` | Click handler for expand |

## Built-in Sorting Functions

| Name | Description |
|------|-------------|
| `alphanumeric` | Mixed alpha+numeric, case-insensitive |
| `alphanumericCaseSensitive` | Mixed alpha+numeric, case-sensitive |
| `text` | Text only, case-insensitive (faster) |
| `textCaseSensitive` | Text only, case-sensitive |
| `datetime` | Date/time comparisons |
| `basic` | Simple `a > b ? 1 : a < b ? -1 : 0` |

### Custom sorting function

```typescript
const sortStatusFn: SortingFn<MyData> = (rowA, rowB, columnId) => {
  const statusOrder = ["pending", "active", "completed"]
  return (
    statusOrder.indexOf(rowA.getValue(columnId)) -
    statusOrder.indexOf(rowB.getValue(columnId))
  )
}

// Use in column: { sortingFn: sortStatusFn }
```

## Built-in Filter Functions

| Name | Description |
|------|-------------|
| `includesString` | Case-insensitive string inclusion |
| `includesStringSensitive` | Case-sensitive string inclusion |
| `equalsString` | Exact string match |
| `arrIncludes` | Array includes value |
| `arrIncludesAll` | Array includes all values |
| `arrIncludesSome` | Array includes some values |
| `equals` | Strict equality |
| `weakEquals` | Loose equality |
| `inNumberRange` | Number within `[min, max]` range |

### Custom filter function

```typescript
{
  accessorKey: "status",
  filterFn: (row, columnId, filterValue: string[]) => {
    return filterValue.includes(row.getValue(columnId))
  },
}
```

## Global Filtering

```typescript
const [globalFilter, setGlobalFilter] = React.useState("")

const table = useReactTable({
  getFilteredRowModel: getFilteredRowModel(),
  onGlobalFilterChange: setGlobalFilter,
  globalFilterFn: "includesString",
  state: { globalFilter },
})
```

## Server-Side Patterns

For server-side sorting, filtering, and pagination, set `manual*` options and do NOT include the corresponding row model:

```typescript
const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  // Do NOT include getPaginationRowModel for server-side
  manualPagination: true,
  manualSorting: true,
  manualFiltering: true,
  pageCount: Math.ceil(totalRows / pageSize),
  onPaginationChange: setPagination,
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  state: { pagination, sorting, columnFilters },
})
```

## Row Expanding

```typescript
const [expanded, setExpanded] = React.useState<ExpandedState>({})

const table = useReactTable({
  getSubRows: (row) => row.children,
  getExpandedRowModel: getExpandedRowModel(),
  onExpandedChange: setExpanded,
  state: { expanded },
})

// Custom detail panel (without sub-rows):
{table.getRowModel().rows.map((row) => (
  <React.Fragment key={row.id}>
    <TableRow>{/* cells */}</TableRow>
    {row.getIsExpanded() && (
      <TableRow>
        <TableCell colSpan={columns.length}>
          <DetailPanel data={row.original} />
        </TableCell>
      </TableRow>
    )}
  </React.Fragment>
))}
```

## Column Pinning

```typescript
const [columnPinning, setColumnPinning] = React.useState<ColumnPinningState>({
  left: ["select"],
  right: ["actions"],
})

const table = useReactTable({
  onColumnPinningChange: setColumnPinning,
  state: { columnPinning },
})
```

Key pinning methods: `column.pin('left' | 'right' | false)`, `column.getIsPinned()`, `table.getLeftHeaderGroups()`, `table.getCenterHeaderGroups()`, `table.getRightHeaderGroups()`.

## Column Resizing

```typescript
const table = useReactTable({
  columnResizeMode: 'onChange',  // 'onChange' | 'onEnd'
  enableColumnResizing: true,
})

// Resize handle in header:
<div
  onMouseDown={header.getResizeHandler()}
  onTouchStart={header.getResizeHandler()}
  onDoubleClick={() => header.column.resetSize()}
  className={cn("resizer", header.column.getIsResizing() && "isResizing")}
/>
```

## Column Ordering

```typescript
const [columnOrder, setColumnOrder] = React.useState<ColumnOrderState>([])

const table = useReactTable({
  onColumnOrderChange: setColumnOrder,
  state: { columnOrder },
})
```

Priority: Column Pinning -> Manual Column Ordering -> Grouping Reorder.

## Row Model Pipeline

The row models form a processing pipeline in this order:

`getCoreRowModel` -> `getFilteredRowModel` -> `getGroupedRowModel` -> `getSortedRowModel` -> `getExpandedRowModel` -> `getPaginationRowModel` -> `getRowModel()`

Only include the row models you need. Each is tree-shakeable.

## Type-Safe Column Meta

Extend the `ColumnMeta` interface via module augmentation:

```typescript
declare module "@tanstack/react-table" {
  interface ColumnMeta<TData extends RowData, TValue> {
    filterVariant?: "text" | "range" | "select"
    align?: "left" | "center" | "right"
  }
}
```

Access via `column.columnDef.meta?.filterVariant`.

## Performance Tips

- **Stabilize `data` and `columns`**: Wrap in `useMemo` or `useState`. Unstable references cause infinite re-renders.
- **Use `getRowId`**: For stable row identity across data updates, especially with selection and expansion state.
- **`columnResizeMode: 'onEnd'`**: Avoids re-renders during drag. Use CSS variables for column widths for smooth 60fps resizing.
- **`autoResetPageIndex`**: Defaults to `true` (resets to page 0 on sort/filter). Set to `false` to preserve page index.
- **Accessor return types**: Return primitive values (string, number) from `accessorFn`. Non-primitives require custom sort/filter functions.
