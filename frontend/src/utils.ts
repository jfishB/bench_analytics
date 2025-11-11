/**
 * Utility function to conditionally combine class names.
 *
 * Filters out falsy values (undefined, false, null) and joins the rest into a single string.
 *
**/
export function cn(...args: (string | undefined | false)[]) {
  return args.filter(Boolean).join(" ");
}