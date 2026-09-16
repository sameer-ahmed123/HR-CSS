import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export type AlertTone = "success" | "info" | "error";

const toneClasses: Record<AlertTone, string> = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  info: "border-sky-200 bg-sky-50 text-sky-800",
  error: "border-red-200 bg-red-50 text-red-800",
};

export function Alert({
  tone,
  children,
  className,
}: {
  tone: AlertTone;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-xl border px-3 py-2.5 text-sm",
        toneClasses[tone],
        className,
      )}
      role={tone === "error" ? "alert" : "status"}
    >
      {children}
    </div>
  );
}
