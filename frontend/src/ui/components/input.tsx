import React from "react";
import { cn } from "../../utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

export function Input({ className = "", ...props }: InputProps) {
  return (
    <input
      {...props}
      className={cn(
        "w-full px-3 py-2 rounded-md border text-sm bg-white text-gray-900 placeholder:text-gray-400 border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/50",
        className
      )}
    />
  );
}

export default Input;
