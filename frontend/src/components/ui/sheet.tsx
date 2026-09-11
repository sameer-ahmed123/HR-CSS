import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cn } from "../../lib/utils";

export const Sheet = DialogPrimitive.Root;
export const SheetTrigger = DialogPrimitive.Trigger;
export const SheetClose = DialogPrimitive.Close;
export const SheetContent = ({
  className,
  side = "left",
  children,
  ...props
}: DialogPrimitive.DialogContentProps & { side?: "left" | "right" }) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 z-40 bg-ink/50 lg:hidden" />
    <DialogPrimitive.Content
      className={cn(
        "fixed inset-y-0 z-50 w-72 bg-ink px-6 py-7 text-mist outline-none",
        side === "right" ? "right-0" : "left-0",
        className,
      )}
      {...props}
    >
      {children}
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
);
