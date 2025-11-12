/**
 * Design System Tokens
 * 
 * Central export for all design tokens.
 * Import from here to access spacing, colors, typography, and component tokens.
 * 
 * @example
 * ```ts
 * import { designTokens, colors, componentTokens } from '@/ui/theme';
 * 
 * const MyComponent = () => (
 *   <div 
 *     style={{
 *       padding: designTokens.spacing[4],
 *       color: colors.primary.DEFAULT,
 *       fontSize: designTokens.fontSize.lg,
 *     }}
 *   >
 *     Hello World
 *   </div>
 * );
 * ```
 */

export { designTokens } from './tokens';
export type {
  Spacing,
  FontSize,
  FontWeight,
  LineHeight,
  BorderRadius,
  BorderWidth,
  BoxShadow,
  ZIndex,
  Opacity,
  MaxWidth,
  Breakpoint,
} from './tokens';

export { colors, withOpacity } from './colors';
export type { Color } from './colors';

export { componentTokens } from './componentTokens';
export type { ComponentTokens } from './componentTokens';

// Re-export CSS for convenience
import './index.css';
