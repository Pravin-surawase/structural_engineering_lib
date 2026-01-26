import { cn } from "../../lib/utils";
import type { ReactNode } from "react";

interface BentoGridProps {
  children: ReactNode;
  className?: string;
}

/**
 * BentoGrid - Modern grid layout inspired by Apple's design language.
 * Features:
 * - Fluid 12-column grid with responsive breakpoints
 * - Glassmorphism backdrop blur effects
 * - Smooth hover animations
 */
export function BentoGrid({ children, className }: BentoGridProps) {
  return (
    <div
      className={cn(
        "grid auto-rows-[minmax(180px,_auto)] grid-cols-12 gap-4 p-4",
        className
      )}
    >
      {children}
    </div>
  );
}

interface BentoCardProps {
  children: ReactNode;
  className?: string;
  colSpan?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  rowSpan?: 1 | 2 | 3 | 4;
  variant?: "default" | "glass" | "solid" | "elevated";
  glow?: boolean;
  onClick?: () => void;
}

const colSpanClasses: Record<number, string> = {
  1: "col-span-1",
  2: "col-span-2",
  3: "col-span-3",
  4: "col-span-4",
  5: "col-span-5",
  6: "col-span-6",
  7: "col-span-7",
  8: "col-span-8",
  9: "col-span-9",
  10: "col-span-10",
  11: "col-span-11",
  12: "col-span-12",
};

const rowSpanClasses: Record<number, string> = {
  1: "row-span-1",
  2: "row-span-2",
  3: "row-span-3",
  4: "row-span-4",
};

/**
 * BentoCard - Individual card component for the Bento grid.
 *
 * Variants:
 * - default: Subtle border with opacity
 * - glass: Glassmorphism with backdrop blur
 * - solid: Solid background (for 3D viewport)
 * - elevated: Higher contrast with shadow
 */
export function BentoCard({
  children,
  className,
  colSpan = 4,
  rowSpan = 1,
  variant = "default",
  glow = false,
  onClick,
}: BentoCardProps) {
  const variantClasses = {
    default: [
      "bg-zinc-900/50",
      "border border-zinc-800/50",
      "hover:border-zinc-700/70",
    ],
    glass: [
      "bg-white/5",
      "backdrop-blur-xl",
      "border border-white/10",
      "hover:bg-white/10",
      "hover:border-white/20",
    ],
    solid: [
      "bg-zinc-900",
      "border border-zinc-800",
    ],
    elevated: [
      "bg-zinc-900/90",
      "border border-zinc-700/50",
      "shadow-2xl",
      "shadow-black/50",
    ],
  };

  return (
    <div
      onClick={onClick}
      className={cn(
        // Base styles
        "relative overflow-hidden rounded-2xl transition-all duration-300 ease-out",
        // Grid spanning
        colSpanClasses[colSpan],
        rowSpanClasses[rowSpan],
        // Variant styles
        ...variantClasses[variant],
        // Hover effects
        "hover:scale-[1.01] hover:shadow-xl",
        // Glow effect
        glow && "ring-2 ring-blue-500/30 ring-offset-2 ring-offset-zinc-900",
        // Interactive
        onClick && "cursor-pointer",
        className
      )}
    >
      {/* Optional gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

      {/* Content */}
      <div className="relative h-full w-full p-4">
        {children}
      </div>
    </div>
  );
}

interface BentoCardHeaderProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  badge?: string;
}

/**
 * BentoCardHeader - Consistent header for Bento cards.
 */
export function BentoCardHeader({
  title,
  subtitle,
  icon,
  badge,
}: BentoCardHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-3">
      <div className="flex items-center gap-2">
        {icon && (
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/10 text-white/80">
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-sm font-medium text-white/90">{title}</h3>
          {subtitle && (
            <p className="text-xs text-white/50">{subtitle}</p>
          )}
        </div>
      </div>
      {badge && (
        <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
          {badge}
        </span>
      )}
    </div>
  );
}

export default BentoGrid;
