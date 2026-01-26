import { cn } from "../../lib/utils";
import { useState, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface DockItem {
  id: string;
  icon: ReactNode;
  label: string;
  onClick?: () => void;
  badge?: string | number;
  active?: boolean;
}

interface FloatingDockProps {
  items: DockItem[];
  className?: string;
  position?: "bottom" | "left" | "right";
}

/**
 * FloatingDock - macOS-style animated dock navigation.
 * Features:
 * - Hover magnification effect
 * - Smooth spring animations
 * - Badge support for notifications
 * - Active state indicators
 */
export function FloatingDock({
  items,
  className,
  position = "bottom",
}: FloatingDockProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const positionClasses = {
    bottom: "bottom-6 left-1/2 -translate-x-1/2 flex-row",
    left: "left-6 top-1/2 -translate-y-1/2 flex-col",
    right: "right-6 top-1/2 -translate-y-1/2 flex-col",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "fixed z-50 flex items-center gap-2 p-2",
        "bg-zinc-900/80 backdrop-blur-2xl",
        "border border-white/10 rounded-2xl",
        "shadow-2xl shadow-black/50",
        positionClasses[position],
        className
      )}
    >
      {items.map((item, index) => (
        <DockIcon
          key={item.id}
          item={item}
          isHovered={hoveredId === item.id}
          isNeighborHovered={
            items.some((i, idx) =>
              i.id === hoveredId && Math.abs(idx - index) === 1
            )
          }
          onHover={() => setHoveredId(item.id)}
          onLeave={() => setHoveredId(null)}
        />
      ))}
    </motion.div>
  );
}

interface DockIconProps {
  item: DockItem;
  isHovered: boolean;
  isNeighborHovered: boolean;
  onHover: () => void;
  onLeave: () => void;
}

function DockIcon({
  item,
  isHovered,
  isNeighborHovered,
  onHover,
  onLeave,
}: DockIconProps) {
  // Calculate scale based on hover state (macOS-style magnification)
  const scale = isHovered ? 1.4 : isNeighborHovered ? 1.15 : 1;

  return (
    <motion.button
      onClick={item.onClick}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      animate={{ scale }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 25,
      }}
      className={cn(
        "relative flex items-center justify-center",
        "w-12 h-12 rounded-xl",
        "transition-colors duration-200",
        item.active
          ? "bg-white/15 text-white"
          : "bg-white/5 text-white/70 hover:bg-white/10 hover:text-white"
      )}
    >
      {/* Icon */}
      <div className="w-6 h-6">{item.icon}</div>

      {/* Badge */}
      {item.badge && (
        <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-500 rounded-full">
          {item.badge}
        </span>
      )}

      {/* Active indicator */}
      {item.active && (
        <motion.div
          layoutId="dock-active"
          className="absolute -bottom-1 w-1 h-1 rounded-full bg-white"
        />
      )}

      {/* Tooltip */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            transition={{ duration: 0.15 }}
            className="absolute -top-10 left-1/2 -translate-x-1/2 whitespace-nowrap px-2 py-1 text-xs font-medium text-white bg-zinc-800 rounded-lg border border-white/10"
          >
            {item.label}
            {/* Arrow */}
            <div className="absolute left-1/2 -bottom-1 -translate-x-1/2 w-2 h-2 bg-zinc-800 border-r border-b border-white/10 rotate-45" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}

export default FloatingDock;
