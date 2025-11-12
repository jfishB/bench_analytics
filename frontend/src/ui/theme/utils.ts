/**
 * Design Token Utilities
 * 
 * Helper functions for working with design tokens.
 */

import { designTokens } from './tokens';
import { colors } from './colors';
import type { Spacing } from './tokens';

/**
 * Generate CSS string from token values
 * Useful for inline styles
 */
export const css = {
  /**
   * Create padding style object
   * @example css.padding(4) => { padding: '1rem' }
   * @example css.padding(4, 2) => { paddingTop: '1rem', paddingBottom: '0.5rem', paddingLeft: '0.5rem', paddingRight: '0.5rem' }
   */
  padding: (all: Spacing, x?: Spacing, y?: Spacing) => {
    if (x !== undefined || y !== undefined) {
      return {
        paddingTop: designTokens.spacing[y ?? all],
        paddingBottom: designTokens.spacing[y ?? all],
        paddingLeft: designTokens.spacing[x ?? all],
        paddingRight: designTokens.spacing[x ?? all],
      };
    }
    return { padding: designTokens.spacing[all] };
  },

  /**
   * Create margin style object
   * @example css.margin({ all: 4 }) => { margin: '1rem' }
   * @example css.margin({ all: 4, x: 2 }) => { marginTop: '1rem', marginBottom: '1rem', marginLeft: '0.5rem', marginRight: '0.5rem' }
   * @example css.margin({ all: 4, x: 2, y: 1 }) => { marginTop: '0.25rem', marginBottom: '0.25rem', marginLeft: '0.5rem', marginRight: '0.5rem' }
   */
  margin: ({ all, x, y }: { all: Spacing, x?: Spacing, y?: Spacing }) => {
    if (x !== undefined || y !== undefined) {
      return {
        marginTop: designTokens.spacing[y ?? all],
        marginBottom: designTokens.spacing[y ?? all],
        marginLeft: designTokens.spacing[x ?? all],
        marginRight: designTokens.spacing[x ?? all],
      };
    }
    return { margin: designTokens.spacing[all] };
  },

  /**
   * Create gap style
   * @example css.gap(4) => { gap: '1rem' }
   */
  gap: (size: Spacing) => ({ gap: designTokens.spacing[size] }),

  /**
   * Create font style object
   * @example css.font('lg', 'bold') => { fontSize: '1.125rem', fontWeight: 700 }
   */
  font: (
    size: keyof typeof designTokens.fontSize,
    weight?: keyof typeof designTokens.fontWeight
  ) => ({
    fontSize: designTokens.fontSize[size],
    ...(weight && { fontWeight: designTokens.fontWeight[weight] }),
  }),

  /**
   * Create border radius style
   * @example css.rounded('lg') => { borderRadius: '0.5rem' }
   */
  rounded: (size: keyof typeof designTokens.borderRadius) => ({
    borderRadius: designTokens.borderRadius[size],
  }),

  /**
   * Create box shadow style
   * @example css.shadow('md') => { boxShadow: '...' }
   */
  shadow: (size: keyof typeof designTokens.boxShadow) => ({
    boxShadow: designTokens.boxShadow[size],
  }),
};

/**
 * Get token value directly
 * Useful when you need the raw value
 */
export const token = {
  spacing: (size: keyof typeof designTokens.spacing) => designTokens.spacing[size],
  fontSize: (size: keyof typeof designTokens.fontSize) => designTokens.fontSize[size],
  color: (path: string) => {
    const parts = path.split('.');
    let value: any = colors;
    for (const part of parts) {
      if (value && Object.prototype.hasOwnProperty.call(value, part)) {
        value = value[part];
      } else {
        throw new Error(`token.color: Invalid color path "${path}"`);
      }
    }
    return value;
  },
};

/**
 * Responsive breakpoint utilities
 */
export const breakpoint = {
  /**
   * Get media query for breakpoint
   * @example breakpoint.up('md') => '@media (min-width: 768px)'
   */
  up: (size: keyof typeof designTokens.breakpoints) =>
    `@media (min-width: ${designTokens.breakpoints[size]})`,

  /**
   * Get media query for max-width breakpoint
   * @example breakpoint.down('md') => '@media (max-width: 767px)'
   */
  down: (size: keyof typeof designTokens.breakpoints) => {
    const breakpointValue = parseInt(designTokens.breakpoints[size]);
    return `@media (max-width: ${breakpointValue - 1}px)`;
  },

  /**
   * Check if viewport matches breakpoint (client-side only)
   */
  matches: (size: keyof typeof designTokens.breakpoints): boolean => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(`(min-width: ${designTokens.breakpoints[size]})`).matches;
  },
};

/**
 * Combine class names with proper handling
 * Already exists as `cn` in utils, but included here for token-specific use
 */
export const combineStyles = (...styles: (Record<string, any> | undefined)[]) => {
  return Object.assign({}, ...styles.filter(Boolean));
};

/**
 * Create transition style
 * @example transition('all', 'base') => { transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)' }
 */
export const transition = (
  property: string,
  duration: keyof typeof designTokens.transition.duration = 'base',
  timing: keyof typeof designTokens.transition.timing = 'ease'
) => ({
  transition: `${property} ${designTokens.transition.duration[duration]} ${designTokens.transition.timing[timing]}`,
});

/**
 * Create z-index style
 * @example zIndex('modal') => { zIndex: 1200 }
 */
export const zIndex = (level: keyof typeof designTokens.zIndex) => ({
  zIndex: designTokens.zIndex[level],
});
