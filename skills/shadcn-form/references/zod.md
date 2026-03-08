# Zod Schema Patterns for Forms

Reference for Zod schema definitions and validation patterns commonly used in forms.

## Primitive Types

```typescript
z.string()
z.number()
z.boolean()
z.date()
z.bigint()
```

## String Validations

```typescript
z.string().min(1, "Required")
z.string().min(5, "Too short")
z.string().max(200, "Too long")
z.string().length(5, "Must be exactly 5 characters")
z.string().email("Invalid email")
z.string().url("Invalid URL")
z.string().uuid("Invalid UUID")
z.string().regex(/^[a-z]+$/, "Lowercase letters only")
z.string().startsWith("https://", "Must start with https://")
z.string().endsWith(".com", "Must end with .com")
z.string().includes("@", "Must contain @")
z.string().trim()           // trims whitespace before validation
z.string().toLowerCase()    // converts to lowercase
z.string().toUpperCase()    // converts to uppercase
```

## Number Validations

```typescript
z.number().min(0, "Must be non-negative")
z.number().max(100, "Must be 100 or less")
z.number().int("Must be a whole number")
z.number().positive("Must be positive")
z.number().nonnegative("Must be non-negative")
z.number().finite("Must be finite")
z.number().multipleOf(5, "Must be a multiple of 5")
```

## Date Validations

```typescript
z.date()
z.date().min(new Date("1900-01-01"), "Too old")
z.date().max(new Date(), "Cannot be in the future")
```

## Optional, Nullable, Default

```typescript
z.string().optional()               // string | undefined
z.string().nullable()               // string | null
z.string().nullish()                // string | null | undefined
z.string().default("fallback")      // uses "fallback" if undefined
z.number().default(0)
z.boolean().default(false)
z.number().default(Math.random)     // function for dynamic defaults
```

## Enums

For Select and RadioGroup fields:

```typescript
// String union
z.enum(["admin", "editor", "viewer"])
// => "admin" | "editor" | "viewer"

// With error message
z.enum(["admin", "editor", "viewer"], { message: "Select a role" })

// From const array
const ROLES = ["admin", "editor", "viewer"] as const
z.enum(ROLES)

// TypeScript enum (Zod v4)
enum Status { Active, Inactive }
z.enum(Status)
```

## Arrays

For dynamic field lists and multi-select checkboxes:

```typescript
z.array(z.string())
z.array(z.string()).min(1, "Select at least one")
z.array(z.string()).max(5, "Maximum 5 items")
z.array(z.string()).length(3, "Exactly 3 items")
z.array(z.string()).nonempty("Cannot be empty")

// Array of objects (for useFieldArray)
z.array(
  z.object({
    email: z.string().email(),
    role: z.enum(["admin", "editor"]),
  })
).min(1, "At least one entry required")
```

## Objects

```typescript
const schema = z.object({
  name: z.string(),
  age: z.number(),
})

type FormValues = z.infer<typeof schema>
// => { name: string; age: number }

// Make all fields optional
schema.partial()

// Make specific fields optional
schema.partial({ age: true })

// Pick specific fields
schema.pick({ name: true })

// Omit specific fields
schema.omit({ age: true })

// Extend with new fields
schema.extend({ email: z.string().email() })
```

## Coercion

HTML form inputs always produce strings. Use `z.coerce` to convert:

```typescript
z.coerce.number()    // Number(input) — for numeric inputs
z.coerce.boolean()   // Boolean(input) — for checkbox values
z.coerce.date()      // new Date(input) — for date inputs
z.coerce.bigint()    // BigInt(input)

// Examples
z.coerce.number().parse("42")        // => 42
z.coerce.number().parse("")          // => 0 (Number("") === 0)
z.coerce.date().parse("2024-01-15") // => Date object
```

**Warning**: `z.coerce.boolean()` uses JavaScript `Boolean()` — any non-empty string (including `"false"`) coerces to `true`. For string booleans, use Zod v4's `z.stringbool()`:

```typescript
z.stringbool().parse("true")   // => true
z.stringbool().parse("false")  // => false
z.stringbool().parse("1")      // => true
z.stringbool().parse("0")      // => false
```

## Type Inference

```typescript
const schema = z.object({
  name: z.string(),
  age: z.coerce.number(),
})

// Infer the output type (after transforms/coercion)
type FormValues = z.infer<typeof schema>
// => { name: string; age: number }

// For schemas with transforms, use z.input and z.output
type FormInput = z.input<typeof schema>   // before transforms
type FormOutput = z.output<typeof schema> // after transforms
```

## Custom Validation with .refine()

```typescript
// Simple boolean check
z.string().refine((val) => val.length <= 255, "Too long")

// With custom error message
z.string().refine((val) => !val.includes(" "), {
  message: "Cannot contain spaces",
})

// Cross-field validation on object
const schema = z
  .object({
    password: z.string().min(8),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"], // error appears on confirmPassword field
  })

// Multiple cross-field validations
const dateRange = z
  .object({
    startDate: z.coerce.date(),
    endDate: z.coerce.date(),
  })
  .refine((data) => data.endDate > data.startDate, {
    message: "End date must be after start date",
    path: ["endDate"],
  })
```

## Multiple Custom Issues with .superRefine()

```typescript
const passwordSchema = z.string().superRefine((val, ctx) => {
  if (val.length < 8) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Must be at least 8 characters",
    })
  }
  if (!/[A-Z]/.test(val)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Must contain an uppercase letter",
    })
  }
  if (!/[0-9]/.test(val)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Must contain a number",
    })
  }
})
```

## Transform

Change the output type during parsing:

```typescript
const trimmed = z.string().transform((val) => val.trim())
const toNumber = z.string().transform((val) => parseInt(val, 10))

// Validate then transform
const schema = z.string().email().transform((val) => val.toLowerCase())
```

## Discriminated Unions

For conditional form sections based on a discriminator field:

```typescript
const contactSchema = z.discriminatedUnion("method", [
  z.object({
    method: z.literal("email"),
    email: z.string().email(),
  }),
  z.object({
    method: z.literal("phone"),
    phone: z.string().min(10, "Phone must be at least 10 digits"),
  }),
])
```

## Parsing Methods

```typescript
// Throws ZodError on failure
schema.parse(data)

// Returns { success, data, error } — never throws
const result = schema.safeParse(data)
if (result.success) {
  console.log(result.data)
} else {
  console.log(result.error.issues)
}

// Async versions (required for async refinements/transforms)
await schema.parseAsync(data)
await schema.safeParseAsync(data)
```

## Error Customization

```typescript
// Inline error messages
z.string().min(5, "Must be at least 5 characters")
z.string().email("Please enter a valid email")
z.number().positive("Must be a positive number")

// Error map function
z.string({
  error: (issue) =>
    issue.input === undefined ? "This field is required" : "Invalid input",
})
```

## Common Form Schema Patterns

### Login form

```typescript
const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})
```

### Registration form

```typescript
const registerSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Must contain an uppercase letter")
      .regex(/[0-9]/, "Must contain a number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })
```

### Settings form with mixed types

```typescript
const settingsSchema = z.object({
  displayName: z.string().min(1, "Required").max(50),
  bio: z.string().max(200).optional(),
  age: z.coerce.number().int().positive().optional(),
  website: z.string().url("Invalid URL").optional().or(z.literal("")),
  theme: z.enum(["light", "dark", "system"]),
  emailNotifications: z.boolean().default(true),
  language: z.enum(["en", "es", "fr", "de"]),
  tags: z.array(z.string()).max(5, "Maximum 5 tags"),
})
```

### Optional URL field

URL fields that should allow empty strings:

```typescript
// z.string().url() rejects empty strings — use union with literal
website: z.string().url("Invalid URL").optional().or(z.literal(""))
```

### Schema composition

```typescript
const addressSchema = z.object({
  street: z.string().min(1, "Required"),
  city: z.string().min(1, "Required"),
  state: z.string().min(1, "Required"),
  zip: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP code"),
})

const orderSchema = z.object({
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.coerce.number().int().positive(),
  })).min(1),
  shippingAddress: addressSchema,
  billingAddress: addressSchema.optional(),
  sameAsShipping: z.boolean().default(true),
})
```
