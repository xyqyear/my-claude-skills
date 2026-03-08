---
name: shadcn-form
description: Build forms with shadcn/ui Field components, React Hook Form, and Zod validation. Use when users need to create forms, add form fields, implement form validation, or work with react-hook-form and zod in a shadcn/ui project. Triggers on requests like "create a form", "add form validation", "build a settings form", "form with react-hook-form".
user-invokable: true
---

# Forms with shadcn/ui + React Hook Form + Zod

Build validated forms using shadcn/ui Field components with React Hook Form for state management and Zod for schema validation.

## Setup

### Install dependencies

```bash
pnpm add react-hook-form @hookform/resolvers zod
```

### Install shadcn components

```bash
pnpm dlx shadcn@latest add field input button
```

Add more as needed:

```bash
pnpm dlx shadcn@latest add select checkbox radio-group textarea switch
```

## Core Pattern

Every form follows three steps: define a Zod schema, create a form with `useForm` + `zodResolver`, and render fields with `Controller` + `Field` components.

```tsx
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"

// 1. Define schema
const profileSchema = z.object({
  username: z.string().min(2, "Username must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
})

type ProfileForm = z.infer<typeof profileSchema>

// 2. Create form
export function ProfileForm() {
  const form = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: "",
      email: "",
    },
  })

  function onSubmit(data: ProfileForm) {
    console.log(data)
  }

  // 3. Render with Controller + Field
  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      <Controller
        name="username"
        control={form.control}
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor={field.name}>Username</FieldLabel>
            <Input
              {...field}
              id={field.name}
              placeholder="johndoe"
              aria-invalid={fieldState.invalid}
            />
            <FieldDescription>Your public display name.</FieldDescription>
            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />
      <Controller
        name="email"
        control={form.control}
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid}>
            <FieldLabel htmlFor={field.name}>Email</FieldLabel>
            <Input
              {...field}
              id={field.name}
              type="email"
              placeholder="john@example.com"
              aria-invalid={fieldState.invalid}
            />
            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />
      <Button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? "Saving..." : "Save"}
      </Button>
    </form>
  )
}
```

## Form Controls

### Input

Spread `{...field}` directly. Works for text, email, password, number types.

```tsx
<Controller
  name="email"
  control={form.control}
  render={({ field, fieldState }) => (
    <Field data-invalid={fieldState.invalid}>
      <FieldLabel htmlFor={field.name}>Email</FieldLabel>
      <Input
        {...field}
        id={field.name}
        type="email"
        aria-invalid={fieldState.invalid}
      />
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </Field>
  )}
/>
```

For numeric inputs, use `z.coerce.number()` in the schema to convert the string value:

```typescript
const schema = z.object({
  age: z.coerce.number().int().positive("Must be a positive integer"),
  price: z.coerce.number().nonnegative("Must be non-negative"),
})
```

### Textarea

Same spread pattern as Input:

```tsx
<Controller
  name="description"
  control={form.control}
  render={({ field, fieldState }) => (
    <Field data-invalid={fieldState.invalid}>
      <FieldLabel htmlFor={field.name}>Description</FieldLabel>
      <Textarea
        {...field}
        id={field.name}
        className="min-h-[120px]"
        aria-invalid={fieldState.invalid}
      />
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </Field>
  )}
/>
```

### Select

Use `value`/`onValueChange` instead of spreading `{...field}`:

```tsx
<Controller
  name="role"
  control={form.control}
  render={({ field, fieldState }) => (
    <Field data-invalid={fieldState.invalid}>
      <FieldLabel htmlFor={field.name}>Role</FieldLabel>
      <Select name={field.name} value={field.value} onValueChange={field.onChange}>
        <SelectTrigger id={field.name} aria-invalid={fieldState.invalid}>
          <SelectValue placeholder="Select a role" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="admin">Admin</SelectItem>
          <SelectItem value="editor">Editor</SelectItem>
          <SelectItem value="viewer">Viewer</SelectItem>
        </SelectContent>
      </Select>
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </Field>
  )}
/>
```

Schema: `z.enum(["admin", "editor", "viewer"], { message: "Select a role" })`

### Checkbox (single boolean)

Use `checked`/`onCheckedChange`:

```tsx
<Controller
  name="terms"
  control={form.control}
  render={({ field, fieldState }) => (
    <Field orientation="horizontal" data-invalid={fieldState.invalid}>
      <Checkbox
        id={field.name}
        checked={field.value}
        onCheckedChange={field.onChange}
        aria-invalid={fieldState.invalid}
      />
      <FieldLabel htmlFor={field.name} className="font-normal">
        Accept terms and conditions
      </FieldLabel>
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </Field>
  )}
/>
```

Schema: `z.boolean().refine((v) => v, "You must accept the terms")`

### Checkbox (multiple values)

For selecting multiple items from a list:

```tsx
const items = [
  { id: "react", label: "React" },
  { id: "vue", label: "Vue" },
  { id: "svelte", label: "Svelte" },
]

<Controller
  name="frameworks"
  control={form.control}
  render={({ field, fieldState }) => (
    <FieldSet>
      <FieldLegend variant="label">Frameworks</FieldLegend>
      <FieldGroup>
        {items.map((item) => (
          <Field key={item.id} orientation="horizontal">
            <Checkbox
              id={`checkbox-${item.id}`}
              checked={field.value?.includes(item.id)}
              onCheckedChange={(checked) => {
                const current = field.value || []
                field.onChange(
                  checked
                    ? [...current, item.id]
                    : current.filter((v: string) => v !== item.id)
                )
              }}
            />
            <FieldLabel htmlFor={`checkbox-${item.id}`} className="font-normal">
              {item.label}
            </FieldLabel>
          </Field>
        ))}
      </FieldGroup>
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </FieldSet>
  )}
/>
```

Schema: `z.array(z.string()).min(1, "Select at least one")`

### RadioGroup

Use `value`/`onValueChange`:

```tsx
<Controller
  name="plan"
  control={form.control}
  render={({ field, fieldState }) => (
    <FieldSet>
      <FieldLegend>Plan</FieldLegend>
      <RadioGroup
        name={field.name}
        value={field.value}
        onValueChange={field.onChange}
      >
        <Field orientation="horizontal">
          <RadioGroupItem value="free" id="plan-free" />
          <FieldLabel htmlFor="plan-free">Free</FieldLabel>
        </Field>
        <Field orientation="horizontal">
          <RadioGroupItem value="pro" id="plan-pro" />
          <FieldLabel htmlFor="plan-pro">Pro ($9.99/mo)</FieldLabel>
        </Field>
        <Field orientation="horizontal">
          <RadioGroupItem value="enterprise" id="plan-enterprise" />
          <FieldLabel htmlFor="plan-enterprise">Enterprise</FieldLabel>
        </Field>
      </RadioGroup>
      {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
    </FieldSet>
  )}
/>
```

Schema: `z.enum(["free", "pro", "enterprise"], { message: "Select a plan" })`

### Switch

Use `checked`/`onCheckedChange`:

```tsx
<Controller
  name="notifications"
  control={form.control}
  render={({ field }) => (
    <Field orientation="horizontal">
      <FieldContent>
        <FieldLabel htmlFor={field.name}>Email notifications</FieldLabel>
        <FieldDescription>Receive emails about account activity.</FieldDescription>
      </FieldContent>
      <Switch
        id={field.name}
        checked={field.value}
        onCheckedChange={field.onChange}
      />
    </Field>
  )}
/>
```

Schema: `z.boolean().default(false)`

## Field Layout

`Field` supports `orientation` prop for layout control:

- **`vertical`** (default) — label above input
- **`horizontal`** — label and input side by side
- **`responsive`** — vertical on mobile, horizontal on desktop

Horizontal/responsive layouts use `FieldContent` to group label and description:

```tsx
<Field orientation="responsive">
  <FieldContent>
    <FieldLabel htmlFor="name">Full Name</FieldLabel>
    <FieldDescription>As it appears on your ID.</FieldDescription>
  </FieldContent>
  <Input id="name" />
</Field>
```

Grid layout with `FieldGroup`:

```tsx
<FieldGroup className="grid grid-cols-2 gap-4">
  <Field>
    <FieldLabel>First Name</FieldLabel>
    <Input />
  </Field>
  <Field>
    <FieldLabel>Last Name</FieldLabel>
    <Input />
  </Field>
</FieldGroup>
```

Organize related fields into sections with `FieldSet`, `FieldLegend`, and `FieldSeparator`:

```tsx
<FieldGroup>
  <FieldSet>
    <FieldLegend>Personal Information</FieldLegend>
    <FieldGroup>{/* fields */}</FieldGroup>
  </FieldSet>
  <FieldSeparator />
  <FieldSet>
    <FieldLegend>Preferences</FieldLegend>
    <FieldGroup>{/* fields */}</FieldGroup>
  </FieldSet>
</FieldGroup>
```

## Dynamic Fields

Use `useFieldArray` for repeatable field groups:

```tsx
import { Controller, useFieldArray, useForm } from "react-hook-form"

const schema = z.object({
  emails: z
    .array(z.object({ address: z.string().email("Invalid email") }))
    .min(1, "At least one email required"),
})

function EmailForm() {
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { emails: [{ address: "" }] },
  })

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "emails",
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {fields.map((item, index) => (
        <Controller
          key={item.id}
          name={`emails.${index}.address`}
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={field.name}>Email {index + 1}</FieldLabel>
              <div className="flex gap-2">
                <Input
                  {...field}
                  id={field.name}
                  type="email"
                  aria-invalid={fieldState.invalid}
                />
                {fields.length > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => remove(index)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                )}
              </div>
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
      ))}
      <Button
        type="button"
        variant="outline"
        onClick={() => append({ address: "" })}
      >
        Add Email
      </Button>
    </form>
  )
}
```

Key rules:
- Always use `item.id` as the React `key`, never the array index
- Provide complete objects to `append`/`prepend`/`insert`
- Array-level errors appear at `form.formState.errors.emails?.root`

## Form Submission

### Async submission with error handling

```tsx
async function onSubmit(data: FormValues) {
  try {
    await api.post("endpoint", { json: data }).json()
    toast.success("Saved successfully")
    form.reset()
  } catch (error) {
    if (error instanceof HTTPError) {
      const body = await error.response.json<{ detail: string }>()
      form.setError("root.serverError", { message: body.detail })
    } else {
      form.setError("root.serverError", { message: "An unexpected error occurred" })
    }
  }
}
```

### Display server errors and loading state

```tsx
{form.formState.errors.root?.serverError && (
  <p className="text-sm text-destructive">
    {form.formState.errors.root.serverError.message}
  </p>
)}

<Button type="submit" disabled={form.formState.isSubmitting}>
  {form.formState.isSubmitting ? "Saving..." : "Save"}
</Button>
```

## Form Reset

```tsx
form.reset()                                              // reset to defaultValues
form.reset({ username: "new", email: "new@example.com" }) // reset with new values

// Auto-reset after successful submission
React.useEffect(() => {
  if (form.formState.isSubmitSuccessful) {
    form.reset()
  }
}, [form.formState.isSubmitSuccessful, form.reset])
```

## Cross-Field Validation

Use `.refine()` on the object schema. The `path` option controls which field displays the error:

```typescript
const schema = z
  .object({
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })
```

## Validation Mode

```typescript
const form = useForm({
  resolver: zodResolver(schema),
  mode: "onBlur",     // validate on blur (good balance of UX and performance)
  // mode: "onSubmit"  — default, validate only on submit
  // mode: "onChange"   — validate on every change (can impact performance)
  // mode: "onTouched"  — validate on first blur, then on every change
  // mode: "all"        — validate on both blur and change
})
```

## Accessibility Checklist

Every `Controller` render function must include:

1. `data-invalid={fieldState.invalid}` on `<Field>`
2. `id={field.name}` on the form control
3. `htmlFor={field.name}` on `<FieldLabel>`
4. `aria-invalid={fieldState.invalid}` on the form control
5. Conditional `{fieldState.invalid && <FieldError errors={[fieldState.error]} />}`

For detailed Zod schema patterns, see [zod.md](references/zod.md). For the complete React Hook Form API, see [rhf-api.md](references/rhf-api.md).
