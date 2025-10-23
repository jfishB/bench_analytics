import * as React from "react";
import * as Select from "@radix-ui/react-select";
import { Check, ChevronDown, ChevronUp } from "lucide-react";

function cn(...a: Array<string | false | null | undefined>) {
  return a.filter(Boolean).join(" ");
}

type Option = { label: string; value: string };

type PrettySelectProps = {
  id?: string;                 // optional id (for testing)
  labelId?: string;            // pass the <Label id="..."> here for a11y
  value: string;
  onValueChange: (v: string) => void;
  options: Option[];
  placeholder?: string;
  className?: string;
  disabled?: boolean;
};

export default function PrettySelect({
  id,
  labelId,
  value,
  onValueChange,
  options,
  placeholder = "Select…",
  className,
  disabled,
}: PrettySelectProps) {
  return (
    <Select.Root value={value} onValueChange={onValueChange} disabled={disabled}>
      <Select.Trigger
        id={id}
        aria-labelledby={labelId}
        className={cn(
          "inline-flex w-full items-center justify-between",
          "rounded-xl border border-transparent bg-gray-100 px-3 py-2 text-sm text-gray-900",
          "shadow-inner ring-1 ring-inset ring-black/0 hover:bg-gray-100/90",
          "focus:outline-none focus:ring-2 focus:ring-blue-500/30",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          className
        )}
      >
        <Select.Value placeholder={placeholder} />
        <Select.Icon className="ml-2 opacity-70">
          <ChevronDown size={16} />
        </Select.Icon>
      </Select.Trigger>

      <Select.Portal>
        <Select.Content
          position="popper"
          sideOffset={8}
          className={cn(
            "z-[10000] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-lg",
            "animate-in fade-in-0 zoom-in-95"
          )}
        >
          <Select.ScrollUpButton className="flex items-center justify-center py-1 text-gray-600">
            <ChevronUp size={16} />
          </Select.ScrollUpButton>

          <Select.Viewport className="p-1">
            {options.map((opt) => (
              <Select.Item
                key={opt.value}
                value={opt.value}
                className={cn(
                  "relative flex cursor-pointer select-none items-center rounded-lg px-3 py-2 text-sm text-gray-900",
                  "outline-none data-[highlighted]:bg-gray-100 data-[state=checked]:font-medium"
                )}
              >
                <Select.ItemText>{opt.label}</Select.ItemText>
                <Select.ItemIndicator className="absolute right-2 text-blue-600">
                  <Check size={16} />
                </Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Viewport>

          <Select.ScrollDownButton className="flex items-center justify-center py-1 text-gray-600">
            <ChevronDown size={16} />
          </Select.ScrollDownButton>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
}
