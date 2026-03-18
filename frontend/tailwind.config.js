/**
 * TailwindCSS configuration
 * 
 * - Specifies files to scan for class names (`content`)
 * - Extends the default theme with design tokens
 * - Integrates with our centralized design system (design-tokens.json)
 */
/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Colors using CSS variables (driven by design-tokens.json)
      colors: {
        background: 'var(--background)',
        surface:    'var(--surface)',
        subtle:     'var(--subtle)',
        foreground: 'var(--foreground)',
        card: {
          DEFAULT: 'var(--card)',
          foreground: 'var(--card-foreground)',
        },
        popover: {
          DEFAULT: 'var(--popover)',
          foreground: 'var(--popover-foreground)',
        },
        primary: {
          DEFAULT: 'var(--primary)',
          hover:      'var(--primary-hover)',
          foreground: 'var(--primary-foreground)',
          glow:       'var(--primary-glow)',
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)',
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)',
          red: 'var(--accent-red)',
          redForeground: 'var(--accent-red-foreground)',
          glow: 'var(--accent-glow)',
        },
        destructive: {
          DEFAULT: 'var(--destructive)',
          foreground: 'var(--destructive-foreground)',
        },
        border: 'var(--border)',
        input:  'var(--input)',
        ring:   'var(--ring)',
        chart: {
          1: 'var(--chart-1)',
          2: 'var(--chart-2)',
          3: 'var(--chart-3)',
          4: 'var(--chart-4)',
          5: 'var(--chart-5)',
        },
      },
      // Border radius aligned with design-tokens.json
      borderRadius: {
        sm:  'var(--radius-sm)',   // 6px  – badges / tags
        md:  'var(--radius-md)',   // 8px  – buttons / inputs
        lg:  'var(--radius)',      // 12px – cards / panels (default)
        xl:  'var(--radius-xl)',   // 16px – hero sections
      },
      // Box shadows aligned with design-tokens.json
      boxShadow: {
        sm:        'var(--shadow-sm)',
        md:        'var(--shadow-md)',
        lg:        'var(--shadow-lg)',
        'glow-blue': 'var(--shadow-glow-blue)',
        'glow-red':  'var(--shadow-glow-red)',
      },
    },
  },
  plugins: [],
};

export default config;