/**
 * Component Tokens
 * 
 * Reusable component-specific design tokens.
 * These provide consistent sizing and styling for common UI patterns.
 */

import { designTokens } from './tokens';

export const componentTokens = {
  // Button sizes
  button: {
    height: {
      sm: designTokens.spacing[8],      // h-8
      default: designTokens.spacing[9], // h-9
      lg: designTokens.spacing[10],     // h-10
    },
    padding: {
      sm: {
        x: designTokens.spacing[3],     // px-3
        y: designTokens.spacing[2],     // py-2
      },
      default: {
        x: designTokens.spacing[4],     // px-4
        y: designTokens.spacing[2],     // py-2
      },
      lg: {
        x: designTokens.spacing[6],     // px-6
        y: designTokens.spacing[2.5],   // py-2.5
      },
    },
    gap: {
      sm: designTokens.spacing[1.5],    // gap-1.5
      default: designTokens.spacing[2], // gap-2
      lg: designTokens.spacing[2],      // gap-2
    },
    borderRadius: {
      sm: designTokens.borderRadius.md,
      default: designTokens.borderRadius.md,
      lg: designTokens.borderRadius.md,
    },
  },

  // Card spacing
  card: {
    padding: {
      sm: designTokens.spacing[4],      // p-4
      default: designTokens.spacing[6], // p-6
      lg: designTokens.spacing[8],      // p-8
    },
    gap: designTokens.spacing[6],       // gap-6
    borderRadius: designTokens.borderRadius.xl,
  },

  // Input fields
  input: {
    height: designTokens.spacing[9],    // h-9
    padding: {
      x: designTokens.spacing[3],       // px-3
      y: designTokens.spacing[2],       // py-2
    },
    borderRadius: designTokens.borderRadius.md,
    fontSize: designTokens.fontSize.sm,
  },

  // Badge
  badge: {
    padding: {
      x: designTokens.spacing[2],       // px-2
      y: designTokens.spacing[0.5],     // py-0.5
    },
    gap: designTokens.spacing[1],       // gap-1
    borderRadius: designTokens.borderRadius.md,
    fontSize: designTokens.fontSize.xs,
  },

  // Avatar/Profile Picture
  avatar: {
    size: {
      xs: designTokens.spacing[6],      // 24px
      sm: designTokens.spacing[8],      // 32px
      default: designTokens.spacing[10], // 40px
      lg: designTokens.spacing[12],     // 48px
      xl: designTokens.spacing[16],     // 64px
    },
    borderRadius: designTokens.borderRadius.full,
  },

  // Header
  header: {
    height: designTokens.spacing[20],   // h-20 (80px)
    logoHeight: designTokens.spacing[14], // h-14 (56px)
  },

  // Footer
  footer: {
    padding: {
      y: designTokens.spacing[10],      // py-10
      x: designTokens.spacing[6],       // px-6
    },
    logoHeight: designTokens.spacing[10], // h-10 (40px)
    gap: designTokens.spacing[10],      // gap-10
  },

  // Form
  form: {
    labelGap: designTokens.spacing[2],  // gap-2
    fieldGap: designTokens.spacing[4],  // gap-4 between fields
    sectionGap: designTokens.spacing[6], // gap-6 between sections
  },

  // Modal/Dialog
  modal: {
    width: {
      sm: designTokens.maxWidth.sm,     // 384px
      default: designTokens.maxWidth.md, // 448px
      lg: designTokens.maxWidth.lg,     // 512px
    },
    padding: designTokens.spacing[8],   // p-8
    borderRadius: designTokens.borderRadius['2xl'],
  },

  // Table
  table: {
    cellPadding: {
      x: designTokens.spacing[4],       // px-4
      y: designTokens.spacing[2],       // py-2
    },
    fontSize: designTokens.fontSize.sm,
  },

  // List Item
  listItem: {
    padding: designTokens.spacing[3],   // p-3
    gap: designTokens.spacing[3],       // gap-3
    borderRadius: designTokens.borderRadius.lg,
  },

  // Container
  container: {
    maxWidth: {
      sm: designTokens.maxWidth['3xl'],  // 768px
      default: designTokens.maxWidth['4xl'], // 896px
      lg: designTokens.maxWidth['6xl'],  // 1152px
      xl: designTokens.maxWidth['7xl'],  // 1280px
    },
    padding: {
      x: designTokens.spacing[4],       // px-4
    },
  },

  // Section Spacing
  section: {
    padding: {
      y: {
        sm: designTokens.spacing[8],    // py-8
        default: designTokens.spacing[12], // py-12
        lg: designTokens.spacing[16],   // py-16
      },
    },
    gap: designTokens.spacing[8],       // gap-8
  },

  // Icon Sizes
  icon: {
    xs: designTokens.spacing[3],        // 12px
    sm: designTokens.spacing[4],        // 16px
    default: designTokens.spacing[5],   // 20px
    lg: designTokens.spacing[6],        // 24px
    xl: designTokens.spacing[8],        // 32px
  },
} as const;

export type ComponentTokens = typeof componentTokens;
