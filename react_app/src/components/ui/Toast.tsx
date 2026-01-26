/**
 * Toast Notifications
 *
 * Lightweight toast notification system using Zustand.
 * Provides success, error, warning, and info notifications.
 */
import { create } from 'zustand';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { useEffect } from 'react';
import { cn } from '../../lib/utils';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearAll: () => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = crypto.randomUUID();
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }));
    return id;
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
  clearAll: () => set({ toasts: [] }),
}));

// Helper functions for creating toasts
export const toast = {
  success: (title: string, message?: string, duration = 4000) =>
    useToastStore.getState().addToast({ type: 'success', title, message, duration }),
  error: (title: string, message?: string, duration = 6000) =>
    useToastStore.getState().addToast({ type: 'error', title, message, duration }),
  warning: (title: string, message?: string, duration = 5000) =>
    useToastStore.getState().addToast({ type: 'warning', title, message, duration }),
  info: (title: string, message?: string, duration = 4000) =>
    useToastStore.getState().addToast({ type: 'info', title, message, duration }),
};

const TOAST_ICONS: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle className="w-5 h-5 text-emerald-500" />,
  error: <XCircle className="w-5 h-5 text-red-500" />,
  warning: <AlertTriangle className="w-5 h-5 text-amber-500" />,
  info: <Info className="w-5 h-5 text-blue-500" />,
};

const TOAST_STYLES: Record<ToastType, string> = {
  success: 'border-emerald-500/20 bg-emerald-500/5',
  error: 'border-red-500/20 bg-red-500/5',
  warning: 'border-amber-500/20 bg-amber-500/5',
  info: 'border-blue-500/20 bg-blue-500/5',
};

function ToastItem({ toast: t }: { toast: Toast }) {
  const { removeToast } = useToastStore();

  useEffect(() => {
    if (t.duration && t.duration > 0) {
      const timer = setTimeout(() => removeToast(t.id), t.duration);
      return () => clearTimeout(timer);
    }
  }, [t.id, t.duration, removeToast]);

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg border backdrop-blur-sm shadow-lg',
        'animate-in slide-in-from-right-full duration-300',
        TOAST_STYLES[t.type]
      )}
      role="alert"
    >
      {TOAST_ICONS[t.type]}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-zinc-100">{t.title}</p>
        {t.message && (
          <p className="mt-1 text-xs text-zinc-400">{t.message}</p>
        )}
      </div>
      <button
        onClick={() => removeToast(t.id)}
        className="p-1 rounded hover:bg-white/10 text-zinc-400 hover:text-zinc-100 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

export function ToastContainer() {
  const { toasts } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)]">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  );
}

export default ToastContainer;
