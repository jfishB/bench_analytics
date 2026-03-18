import * as React from "react";
import { cn } from "../../utils";

/**
 * Card Component
 * Glassmorphism container with frosted-glass background, subtle white border,
 * and rounded-lg corners — aligned with design-tokens.json.
 */
function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card"
      className={cn(
        "glass-card glass-card-hover text-card-foreground flex flex-col gap-6 rounded-lg",
        className
      )}
      {...props}
    />
  );
}

/**
 * CardHeader
 * Contains the title and optional action elements.
 * Uses CSS grid for layout.
 */
function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 pt-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        className
      )}
      {...props}
    />
  );
}

/**
 * CardTitle
 * Primary heading for the card — slate-50 for high contrast.
 */
function CardTitle({
  className,
  children,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <h4
      data-slot="card-title"
      className={cn("leading-none text-foreground font-semibold", className)}
      {...props}
    >
      {children}
    </h4>
  );
}

/**
 * CardDescription
 * Secondary text — slate-400 for measured contrast against dark background.
 */
function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <p
      data-slot="card-description"
      className={cn("text-muted-foreground text-sm leading-relaxed", className)}
      {...props}
    />
  );
}

/**
 * CardAction
 * Container for buttons or interactive elements in the header.
 */
function CardAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className
      )}
      {...props}
    />
  );
}

/**
 * CardContent
 * Main body content of the card.
 */
function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-content"
      className={cn("px-6 [&:last-child]:pb-6", className)}
      {...props}
    />
  );
}

/**
 * CardFooter
 * Container for footer actions or notes, typically buttons or metadata.
 */
function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-footer"
      className={cn("flex items-center px-6 pb-6 [.border-t]:pt-6", className)}
      {...props}
    />
  );
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
};

