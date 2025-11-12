# Design Tokens

A centralized design system for Bench Analytics that eliminates magic numbers and provides a single source of truth for all design values.

## Overview

Design tokens are the visual design atoms of the design system — specifically, they are named entities that store visual design attributes. We use them in place of hard-coded values to ensure consistency and maintainability.

## Architecture

The design token system is organized into several modules:

### 1. **Core Tokens** (`tokens.ts`)
Foundation tokens for spacing, typography, shadows, etc.

### 2. **Color Tokens** (`colors.ts`)
Semantic color system that references CSS variables for theme support.

### 3. **Component Tokens** (`componentTokens.ts`)
Pre-configured token combinations for common UI components.

### 4. **CSS Variables** (`index.css`)
Root-level CSS custom properties that support light/dark modes.

## Usage

### Importing Tokens

```typescript
import { designTokens, colors, componentTokens } from '@/ui/theme';
```

### Spacing

Use spacing tokens instead of hardcoded pixel values:

```tsx
// ❌ Bad - magic numbers
<div className="p-4 gap-3 mb-6">

// ✅ Good - using Tailwind (which references tokens)
<div className="p-4 gap-3 mb-6">

// ✅ Good - inline styles with tokens
<div style={{ padding: designTokens.spacing[4] }}>
```

### Colors

Reference colors through semantic tokens:

```tsx
// ❌ Bad - hardcoded color
<div className="text-gray-700 bg-blue-50">

// ✅ Good - semantic color tokens
<div className="text-foreground bg-background">

// ✅ Good - inline styles
<div style={{ color: colors.foreground, backgroundColor: colors.background }}>
```

### Typography

Use typography tokens for consistent text styling:

```tsx
// ❌ Bad - magic numbers
<h1 style={{ fontSize: '36px', fontWeight: 700 }}>

// ✅ Good - design tokens
<h1 style={{ 
  fontSize: designTokens.fontSize['3xl'], 
  fontWeight: designTokens.fontWeight.bold 
}}>
```

### Component Tokens

For common components, use pre-configured component tokens:

```tsx
// Button with consistent sizing
<button style={{
  height: componentTokens.button.height.default,
  paddingLeft: componentTokens.button.padding.default.x,
  paddingRight: componentTokens.button.padding.default.x,
  borderRadius: componentTokens.button.borderRadius.default,
}}>
  Click Me
</button>

// Card with consistent padding
<div style={{
  padding: componentTokens.card.padding.default,
  borderRadius: componentTokens.card.borderRadius,
}}>
  Card content
</div>
```

## Available Tokens

### Spacing Scale
```typescript
0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 24, 28, 32
```

### Font Sizes
```typescript
xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl, 6xl
```

### Font Weights
```typescript
normal (400), medium (500), semibold (600), bold (700)
```

### Border Radius
```typescript
none, sm, base, md, lg, xl, 2xl, 3xl, full
```

### Colors (Semantic)
- `background` / `foreground`
- `primary` / `primary.foreground`
- `secondary` / `secondary.foreground`
- `muted` / `muted.foreground`
- `accent` / `accent.foreground`
- `destructive` / `destructive.foreground`
- `card` / `card.foreground`
- `popover` / `popover.foreground`
- `border`, `input`, `ring`
- `chart.1` through `chart.5`
- `gray.50` through `gray.900`
- `blue.50` through `blue.900`

## Component Tokens

Pre-configured tokens for common components:

- `button` - heights, padding, gaps, border radius
- `card` - padding, gaps, border radius
- `input` - height, padding, border radius, font size
- `badge` - padding, gap, border radius, font size
- `avatar` - sizes, border radius
- `header` - height, logo height
- `footer` - padding, logo height, gaps
- `modal` - widths, padding, border radius
- `table` - cell padding, font size
- `listItem` - padding, gap, border radius
- `container` - max widths, padding
- `section` - padding, gaps
- `icon` - sizes

## Best Practices

### DO ✅

1. **Use semantic tokens** - Prefer `colors.primary` over `colors.blue[500]`
2. **Use component tokens** - Leverage pre-configured combinations
3. **Use Tailwind classes** - They reference the same token system
4. **Document custom values** - If you must deviate, explain why
5. **Update tokens, not components** - Change tokens to affect all components

### DON'T ❌

1. **Avoid magic numbers** - Don't use `16px` or `#3B82F6` directly
2. **Don't create one-off values** - Add to tokens if needed elsewhere
3. **Don't bypass the system** - Even for "quick fixes"
4. **Don't mix units** - Stick to rem-based spacing
5. **Don't hardcode breakpoints** - Use `designTokens.breakpoints`

## Examples

### Before (Magic Numbers)
```tsx
<div className="bg-white p-8 rounded-2xl shadow-md w-96">
  <h2 className="text-2xl font-bold mb-6 text-center">Register</h2>
  <input className="border w-full p-2 mb-3 rounded" />
</div>
```

### After (Design Tokens)
```tsx
<div className="bg-background p-8 rounded-2xl shadow-md max-w-sm">
  <h2 className="text-2xl font-bold mb-6 text-center text-foreground">Register</h2>
  <input className="border w-full p-2 mb-3 rounded-md bg-input" />
</div>
```

Or with component tokens:
```tsx
<div style={{
  backgroundColor: colors.background,
  padding: componentTokens.modal.padding,
  borderRadius: componentTokens.modal.borderRadius,
  maxWidth: componentTokens.modal.width.default,
}}>
  <h2 style={{
    fontSize: designTokens.fontSize['2xl'],
    fontWeight: designTokens.fontWeight.bold,
    marginBottom: designTokens.spacing[6],
    color: colors.foreground,
  }}>
    Register
  </h2>
</div>
```

## TypeScript Support

All tokens are fully typed for excellent IDE autocomplete:

```typescript
import type { Spacing, FontSize, Color } from '@/ui/theme';

// TypeScript will autocomplete and validate
const spacing: Spacing = 4; // ✅
const invalidSpacing: Spacing = 13; // ❌ Type error
```

## Dark Mode

Colors automatically adapt to dark mode through CSS variables. No code changes needed:

```tsx
// This works in both light and dark mode
<div className="bg-background text-foreground">
  Content
</div>
```

## Migration Guide

When refactoring existing code:

1. **Identify hardcoded values** - Look for `px`, `#hex`, `rgb()`, magic numbers
2. **Find equivalent token** - Check tokens.ts, colors.ts, componentTokens.ts
3. **Replace with token** - Use Tailwind class or inline style with token
4. **Test both themes** - Ensure it works in light and dark mode
5. **Remove old value** - Delete the hardcoded value

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Design Tokens Specification](https://design-tokens.github.io/community-group/format/)
- [CSS Custom Properties (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)

## Questions?

If you're unsure which token to use or think a new token should be added, reach out to the team or create an issue describing your use case.
