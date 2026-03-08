# React Hook Form API Reference

Detailed API reference for React Hook Form when used with shadcn/ui Field components and Zod validation.

## useForm Options

```typescript
const form = useForm<FormValues>({
  resolver: zodResolver(schema),       // Zod validation resolver
  defaultValues: { name: "", age: 0 }, // initial values (required for controlled components)
  mode: "onSubmit",                    // validation trigger: onSubmit | onBlur | onChange | onTouched | all
  reValidateMode: "onChange",          // re-validation after first submit: onChange | onBlur | onSubmit
  criteriaMode: "firstError",         // firstError | all (collect one or all errors per field)
  shouldFocusError: true,             // auto-focus first field with error on submit
  shouldUnregister: false,            // unregister inputs on unmount
  delayError: undefined,              // delay error display in ms
  disabled: false,                    // disable entire form
})
```

### Mode Details

| Mode | Behavior |
|------|----------|
| `onSubmit` | Validates on submit, then re-validates on change |
| `onBlur` | Validates on blur events |
| `onChange` | Validates on every change (performance impact) |
| `onTouched` | Validates on first blur, then on every change |
| `all` | Validates on both blur and change |

### Async Default Values

```typescript
const form = useForm({
  defaultValues: async () => {
    const response = await fetch("/api/profile")
    return response.json()
  },
})
// form.formState.isLoading is true until defaults resolve
```

## formState Properties

**Important**: `formState` uses a Proxy for render optimization. Destructure the properties you need before the return statement:

```typescript
const {
  formState: { errors, isDirty, isSubmitting, isValid, isSubmitSuccessful },
} = useForm()
```

| Property | Type | Description |
|----------|------|-------------|
| `errors` | `FieldErrors` | Validation errors object |
| `isDirty` | `boolean` | Form modified from defaultValues |
| `dirtyFields` | `Partial<Record<string, boolean>>` | Per-field dirty tracking |
| `touchedFields` | `Partial<Record<string, boolean>>` | Per-field touched tracking |
| `isSubmitting` | `boolean` | Form is currently submitting |
| `isSubmitted` | `boolean` | Form has been submitted (persists until reset) |
| `isSubmitSuccessful` | `boolean` | Submission completed without errors |
| `isValid` | `boolean` | No errors (requires `mode: "onChange"` or `"all"` for pre-submit) |
| `isValidating` | `boolean` | Validation in progress |
| `isLoading` | `boolean` | Async defaultValues loading |
| `submitCount` | `number` | Number of submissions |
| `defaultValues` | `FormValues` | Current default values |

## Controller Component

Used with shadcn/ui Field components for controlled inputs.

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `name` | `string` | Yes | Field name matching schema key |
| `control` | `Control` | Yes | From `useForm().control` |
| `render` | `Function` | Yes | Render prop |
| `defaultValue` | `any` | No | Per-field default (prefer useForm defaultValues) |
| `shouldUnregister` | `boolean` | No | Unregister on unmount |
| `disabled` | `boolean` | No | Disable field |

### Render Prop Arguments

```typescript
render={({ field, fieldState, formState }) => (
  // field: { onChange, onBlur, value, name, ref, disabled }
  // fieldState: { invalid, isTouched, isDirty, error }
  // formState: same as top-level formState
)}
```

#### field Object

| Property | Type | Description |
|----------|------|-------------|
| `onChange` | `(value: any) => void` | Send value to form |
| `onBlur` | `() => void` | Report blur event |
| `value` | `any` | Current field value |
| `name` | `string` | Field name |
| `ref` | `React.Ref` | For focus management |
| `disabled` | `boolean` | Disabled state |

#### fieldState Object

| Property | Type | Description |
|----------|------|-------------|
| `invalid` | `boolean` | Field has validation error |
| `isTouched` | `boolean` | Field has been blurred |
| `isDirty` | `boolean` | Field value differs from default |
| `error` | `FieldError \| undefined` | Error object with `message` and `type` |

### Binding Patterns

| Control Type | Binding |
|-------------|---------|
| Input, Textarea | `{...field}` (spread all) |
| Select | `value={field.value} onValueChange={field.onChange}` |
| Checkbox | `checked={field.value} onCheckedChange={field.onChange}` |
| RadioGroup | `value={field.value} onValueChange={field.onChange}` |
| Switch | `checked={field.value} onCheckedChange={field.onChange}` |

## useFieldArray

For dynamic repeatable field groups.

```typescript
const { fields, append, prepend, insert, swap, move, update, replace, remove } =
  useFieldArray({
    control: form.control,
    name: "items", // must match schema key
    rules: { minLength: 1 }, // optional validation
  })
```

### Return Values

| Method | Type | Description |
|--------|------|-------------|
| `fields` | `Array<object & { id: string }>` | Field objects with unique `id` |
| `append` | `(obj) => void` | Add to end |
| `prepend` | `(obj) => void` | Add to start |
| `insert` | `(index, obj) => void` | Insert at position |
| `remove` | `(index?) => void` | Remove at position (or all) |
| `swap` | `(from, to) => void` | Swap two positions |
| `move` | `(from, to) => void` | Move to position |
| `update` | `(index, obj) => void` | Update at position |
| `replace` | `(obj[]) => void` | Replace entire array |

### Rules

- Always use `item.id` as React `key`, never array index
- Provide complete objects to `append`/`prepend`/`insert`
- Array-level errors: `form.formState.errors.items?.root`
- Must use arrays of objects (flat arrays not supported)

## useFormContext / FormProvider

Access form methods in deeply nested components without prop drilling:

```tsx
import { FormProvider, useForm, useFormContext } from "react-hook-form"

function ParentForm() {
  const methods = useForm()
  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <NestedField />
      </form>
    </FormProvider>
  )
}

function NestedField() {
  const { control } = useFormContext()
  return (
    <Controller name="nested" control={control} render={({ field }) => (
      <Input {...field} />
    )} />
  )
}
```

## Programmatic Methods

### handleSubmit

```typescript
// With error handler (optional second argument)
<form onSubmit={form.handleSubmit(onValid, onInvalid)}>

const onValid = (data: FormValues) => console.log(data)
const onInvalid = (errors: FieldErrors) => console.log(errors)

// Programmatic invocation (outside <form>)
form.handleSubmit(onValid)()
```

### reset

```typescript
form.reset()                                  // reset to defaultValues
form.reset({ name: "new" })                   // reset with new values
form.reset((values) => ({ ...values, name: "new" })) // callback form

// Options
form.reset(values, {
  keepErrors: false,        // preserve errors
  keepDirty: false,         // preserve dirty state
  keepDirtyValues: false,   // keep values of dirty fields only
  keepValues: false,        // keep all values unchanged
  keepDefaultValues: false, // keep original defaults
  keepIsSubmitted: false,   // preserve isSubmitted
  keepTouched: false,       // preserve touched state
  keepIsValid: false,       // preserve isValid
  keepSubmitCount: false,   // preserve submitCount
})
```

### setValue

```typescript
form.setValue("name", "John")
form.setValue("name", "John", {
  shouldValidate: true,  // trigger validation
  shouldDirty: true,     // mark as dirty
  shouldTouch: true,     // mark as touched
})
```

### setError

```typescript
// Field error
form.setError("email", { type: "server", message: "Email already taken" })

// Root-level error (for general/server errors)
form.setError("root.serverError", { type: "server", message: "Failed to save" })

// Display root errors
{form.formState.errors.root?.serverError && (
  <p>{form.formState.errors.root.serverError.message}</p>
)}
```

### clearErrors

```typescript
form.clearErrors("email")                    // single field
form.clearErrors(["email", "name"])          // multiple fields
form.clearErrors()                            // all errors
```

### trigger

Manual validation:

```typescript
await form.trigger("email")                   // single field
await form.trigger(["email", "name"])         // multiple fields
await form.trigger()                           // all fields
// Returns boolean indicating validity
```

### getValues

Non-reactive value access (does not trigger re-renders):

```typescript
form.getValues()              // all values
form.getValues("email")       // single field
form.getValues(["email", "name"]) // multiple fields
```

For reactive values, use `form.watch()`:

```typescript
const email = form.watch("email")       // re-renders on change
const [email, name] = form.watch(["email", "name"])
const allValues = form.watch()          // watch everything
```

### setFocus

```typescript
form.setFocus("email")                   // focus the email field
form.setFocus("email", { shouldSelect: true }) // focus and select
```

## TypeScript Types

```typescript
import type {
  FieldValues,
  FieldPath,
  FieldError,
  FieldErrors,
  SubmitHandler,
  SubmitErrorHandler,
  Control,
  UseFormReturn,
} from "react-hook-form"

// Typed submit handler
const onSubmit: SubmitHandler<FormValues> = (data) => { ... }

// Reusable form field component
type FormFieldProps<T extends FieldValues> = {
  name: FieldPath<T>
  control: Control<T>
  label: string
}
```

### Reusable Field Component Pattern

```tsx
import { Controller, Control, FieldValues, FieldPath } from "react-hook-form"
import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"

type TextFieldProps<T extends FieldValues> = {
  name: FieldPath<T>
  control: Control<T>
  label: string
  placeholder?: string
  type?: React.HTMLInputTypeAttribute
}

function TextField<T extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  type = "text",
}: TextFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={field.name}>{label}</FieldLabel>
          <Input
            {...field}
            id={field.name}
            type={type}
            placeholder={placeholder}
            aria-invalid={fieldState.invalid}
          />
          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  )
}

// Usage
<TextField name="email" control={form.control} label="Email" type="email" />
```

## Common Patterns

### Post-submission reset

```typescript
React.useEffect(() => {
  if (form.formState.isSubmitSuccessful) {
    form.reset()
  }
}, [form.formState.isSubmitSuccessful, form.reset])
```

### Populate form from API

```typescript
const { data } = useQuery({ queryKey: ["profile"], queryFn: fetchProfile })

React.useEffect(() => {
  if (data) {
    form.reset(data)
  }
}, [data, form.reset])
```

### Dependent field validation

Use `deps` in register options or trigger manually:

```typescript
// When "password" changes, also re-validate "confirmPassword"
<Controller
  name="password"
  control={form.control}
  render={({ field, fieldState }) => (
    <Field data-invalid={fieldState.invalid}>
      <FieldLabel htmlFor={field.name}>Password</FieldLabel>
      <Input
        {...field}
        id={field.name}
        type="password"
        onChange={(e) => {
          field.onChange(e)
          form.trigger("confirmPassword")
        }}
      />
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </Field>
  )}
/>
```

### Disabled form during submission

```typescript
<fieldset disabled={form.formState.isSubmitting}>
  {/* all fields inside are disabled during submission */}
</fieldset>
```
