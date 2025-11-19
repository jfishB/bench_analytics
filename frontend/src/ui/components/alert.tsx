/**
 * Alert component for displaying notifications and errors
 */

import React from "react";

interface AlertProps {
  variant?: "default" | "error" | "warning" | "success";
  children: React.ReactNode;
  onClose?: () => void;
}

export function Alert({ variant = "default", children, onClose }: AlertProps) {
  const variantStyles = {
    default: "bg-blue-50 border-blue-200 text-blue-800",
    error: "bg-red-50 border-red-200 text-red-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    success: "bg-green-50 border-green-200 text-green-800",
  };

  const iconPaths = {
    default: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    error: "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z",
    warning:
      "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
    success:
      "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  };

  return (
    <div
      className={`relative rounded-lg border p-4 ${variantStyles[variant]}`}
      role="alert"
    >
      <div className="flex items-start">
        <svg
          className="h-5 w-5 flex-shrink-0 mr-3 mt-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d={iconPaths[variant]}
          />
        </svg>
        <div className="flex-1">{children}</div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 flex-shrink-0 inline-flex text-current hover:opacity-75 focus:outline-none"
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

interface AlertTitleProps {
  children: React.ReactNode;
}

export function AlertTitle({ children }: AlertTitleProps) {
  return <h3 className="font-semibold mb-1">{children}</h3>;
}

interface AlertDescriptionProps {
  children: React.ReactNode;
}

export function AlertDescription({ children }: AlertDescriptionProps) {
  return <p className="text-sm">{children}</p>;
}

