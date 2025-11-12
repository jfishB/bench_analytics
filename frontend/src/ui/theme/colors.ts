/**
 * Color Tokens
 * 
 * Semantic color tokens that reference CSS variables defined in index.css.
 * These provide type-safe color references throughout the application.
 */

export const colors = {
  // Core colors
  background: 'var(--background)',
  foreground: 'var(--foreground)',
  
  // Card
  card: {
    DEFAULT: 'var(--card)',
    foreground: 'var(--card-foreground)',
  },
  
  // Popover
  popover: {
    DEFAULT: 'var(--popover)',
    foreground: 'var(--popover-foreground)',
  },
  
  // Primary
  primary: {
    DEFAULT: 'var(--primary)',
    foreground: 'var(--primary-foreground)',
  },
  
  // Secondary
  secondary: {
    DEFAULT: 'var(--secondary)',
    foreground: 'var(--secondary-foreground)',
  },
  
  // Muted
  muted: {
    DEFAULT: 'var(--muted)',
    foreground: 'var(--muted-foreground)',
  },
  
  // Accent
  accent: {
    DEFAULT: 'var(--accent)',
    foreground: 'var(--accent-foreground)',
    red: 'var(--accent-red)',
    redForeground: 'var(--accent-red-foreground)',
  },
  
  // Destructive
  destructive: {
    DEFAULT: 'var(--destructive)',
    foreground: 'var(--destructive-foreground)',
  },
  
  // UI Elements
  border: 'var(--border)',
  input: {
    DEFAULT: 'var(--input)',
    background: 'var(--input-background)',
  },
  ring: 'var(--ring)',
  switchBackground: 'var(--switch-background)',
  
  // Charts
  chart: {
    1: 'var(--chart-1)',
    2: 'var(--chart-2)',
    3: 'var(--chart-3)',
    4: 'var(--chart-4)',
    5: 'var(--chart-5)',
  },
  
  // Sidebar
  sidebar: {
    DEFAULT: 'var(--sidebar)',
    foreground: 'var(--sidebar-foreground)',
    primary: 'var(--sidebar-primary)',
    primaryForeground: 'var(--sidebar-primary-foreground)',
    accent: 'var(--sidebar-accent)',
    accentForeground: 'var(--sidebar-accent-foreground)',
    border: 'var(--sidebar-border)',
    ring: 'var(--sidebar-ring)',
  },
  
  // Tailwind gray scale (commonly used)
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  
  // Tailwind blue scale
  blue: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  
  // Additional semantic colors
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
  current: 'currentColor',
} as const;

// Helper function to get color with opacity
// Note: For rgba(var(--color), opacity) to work, the CSS variable must be defined as "r, g, b" (e.g., "255, 255, 255").
// If your variables are not in this format, consider updating them or handling conversion here.
// This function extracts the variable name and returns rgba(var(--color), opacity).
export const withOpacity = (color: string, opacity: number): string => {
  if (color.startsWith('var(')) {
    // Extract the variable name from var(--color)
    const varName = color.slice(4, -1).trim();
    return `rgba(var(${varName}), ${opacity})`;
  }
  return color;
};

export type Color = typeof colors;
