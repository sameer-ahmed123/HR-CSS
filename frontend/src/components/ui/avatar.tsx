import * as AvatarPrimitive from "@radix-ui/react-avatar";
import { cn } from "../../lib/utils";

export const Avatar = ({
  className,
  ...props
}: AvatarPrimitive.AvatarProps) => (
  <AvatarPrimitive.Root
    className={cn(
      "relative flex h-9 w-9 shrink-0 overflow-hidden rounded-xl",
      className,
    )}
    {...props}
  />
);
export const AvatarImage = ({
  className,
  ...props
}: AvatarPrimitive.AvatarImageProps) => (
  <AvatarPrimitive.Image
    className={cn("aspect-square h-full w-full", className)}
    {...props}
  />
);
export const AvatarFallback = ({
  className,
  ...props
}: AvatarPrimitive.AvatarFallbackProps) => (
  <AvatarPrimitive.Fallback
    className={cn(
      "grid h-full w-full place-items-center bg-mint text-sm font-bold text-ink",
      className,
    )}
    {...props}
  />
);
