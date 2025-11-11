import * as React from "react";
import * as LabelPrimitive from "@radix-ui/react-label";

/**
 * Utility function to merge class names conditionally
 */
function cn(...a: Array<string | false | null | undefined>) {
  return a.filter(Boolean).join(" ");
}

/**
 * Label (UI primitive)
 *
 * Wraps Radix's Label component with custom styling.
 * - Supports standard HTML label props
 * - Respects disabled state via peer/group for accessibility
 * - Flexible for use with forms and inputs
 */
export const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>
>(function Label({ className, ...props }, ref) {
  return (
    <LabelPrimitive.Root
      ref={ref}
      data-slot="label"
      className={cn(
        "flex items-center gap-2 text-sm leading-none font-medium select-none",
        "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
        "group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50",
        className
      )}
      {...props}
    />
  );
});
