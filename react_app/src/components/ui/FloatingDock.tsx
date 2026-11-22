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
  position?: 'bottom' | 'left' | 'right' | 'inline';
}

const POSITION_CLASS = {
  bottom: 'fixed bottom-6 left-1/2 -translate-x-1/2 flex-row rounded-xl border',
  left: 'fixed left-6 top-1/2 -translate-y-1/2 flex-col rounded-xl border',
  right: 'fixed right-6 top-1/2 -translate-y-1/2 flex-col rounded-xl border',
  inline: 'grid grid-cols-2 border-t px-4 pb-[max(0.25rem,env(safe-area-inset-bottom))]',
} as const;

/** Compact mobile navigation; destinations come from the typed app configuration. */
export function FloatingDock({
  items,
  className,
  position = 'bottom',
}: FloatingDockProps) {
  const isInline = position === 'inline';
  return (
    <nav aria-label="Quick navigation">
      <div
        className={cn(
          'z-50 flex items-center gap-2 border-zinc-700 bg-zinc-950 p-1',
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
              'group relative flex items-center justify-center rounded-sm transition-colors',
              isInline ? 'min-h-11 gap-2 text-sm font-medium' : 'size-12',
              item.active
                ? 'bg-white/15 text-white'
                : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white',
            )}
          >
            <span aria-hidden="true">{item.icon}</span>
            {item.badge ? (
              <span className="absolute -top-1 -right-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                {item.badge}
              </span>
            ) : null}
            <span className={isInline ? '' : 'pointer-events-none absolute -top-10 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-sm border border-zinc-700 bg-zinc-800 px-2 py-1 text-xs font-medium text-white opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100'}>
              {item.label}
            </span>
          </button>
        ))}
      </div>
    </nav>
  );
}

export default FloatingDock;
