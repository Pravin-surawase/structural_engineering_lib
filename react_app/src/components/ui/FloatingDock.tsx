import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

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
  position?: 'bottom' | 'left' | 'right';
}

const POSITION_CLASS = {
  bottom: 'bottom-6 left-1/2 -translate-x-1/2 flex-row',
  left: 'left-6 top-1/2 -translate-y-1/2 flex-col',
  right: 'right-6 top-1/2 -translate-y-1/2 flex-col',
} as const;

/** Compact mobile navigation; destinations come from the typed app configuration. */
export function FloatingDock({
  items,
  className,
  position = 'bottom',
}: FloatingDockProps) {
  return (
    <nav aria-label="Quick navigation">
      <div
        className={cn(
          'fixed z-50 flex items-center gap-2 rounded-2xl border border-white/10 bg-zinc-900/90 p-2 shadow-2xl shadow-black/50 backdrop-blur-2xl',
          POSITION_CLASS[position],
          className,
        )}
      >
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            aria-label={item.label}
            aria-current={item.active ? 'page' : undefined}
            onClick={item.onClick}
            className={cn(
              'group relative flex h-12 w-12 items-center justify-center rounded-xl transition-colors',
              item.active
                ? 'bg-white/15 text-white'
                : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white',
            )}
          >
            <span className="h-6 w-6">{item.icon}</span>
            {item.badge ? (
              <span className="absolute -top-1 -right-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                {item.badge}
              </span>
            ) : null}
            {item.active ? (
              <span className="absolute -bottom-1 h-1 w-1 rounded-full bg-white" />
            ) : null}
            <span className="pointer-events-none absolute -top-10 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-lg border border-white/10 bg-zinc-800 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
              {item.label}
            </span>
          </button>
        ))}
      </div>
    </nav>
  );
}

export default FloatingDock;
