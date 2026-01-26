/**
 * ConnectionStatus Component
 *
 * Visual indicator for WebSocket connection state.
 * Shows connection status with appropriate colors and icons.
 */
import { Wifi, WifiOff, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import type { ConnectionStatus as ConnectionStatusType } from '../../hooks/useDesignWebSocket';

interface ConnectionStatusProps {
  status: ConnectionStatusType;
  latency?: number | null;
  error?: string | null;
  retryCount?: number;
  onReconnect?: () => void;
  className?: string;
}

const STATUS_CONFIG: Record<
  ConnectionStatusType,
  {
    icon: React.ReactNode;
    label: string;
    bgColor: string;
    textColor: string;
    animate?: boolean;
  }
> = {
  connected: {
    icon: <Wifi className="w-3.5 h-3.5" />,
    label: 'Connected',
    bgColor: 'bg-emerald-500/10',
    textColor: 'text-emerald-500',
  },
  connecting: {
    icon: <Loader2 className="w-3.5 h-3.5" />,
    label: 'Connecting...',
    bgColor: 'bg-blue-500/10',
    textColor: 'text-blue-500',
    animate: true,
  },
  reconnecting: {
    icon: <RefreshCw className="w-3.5 h-3.5" />,
    label: 'Reconnecting...',
    bgColor: 'bg-amber-500/10',
    textColor: 'text-amber-500',
    animate: true,
  },
  disconnected: {
    icon: <WifiOff className="w-3.5 h-3.5" />,
    label: 'Disconnected',
    bgColor: 'bg-zinc-500/10',
    textColor: 'text-zinc-500',
  },
  error: {
    icon: <AlertCircle className="w-3.5 h-3.5" />,
    label: 'Error',
    bgColor: 'bg-red-500/10',
    textColor: 'text-red-500',
  },
};

export function ConnectionStatus({
  status,
  latency,
  error,
  retryCount,
  onReconnect,
  className = '',
}: ConnectionStatusProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div
      className={`flex items-center gap-2 px-2.5 py-1.5 rounded-full ${config.bgColor} ${config.textColor} text-xs font-medium ${className}`}
      title={error || config.label}
    >
      <span className={config.animate ? 'animate-spin' : ''}>{config.icon}</span>
      <span>{config.label}</span>
      {latency !== null && latency !== undefined && status === 'connected' && (
        <span className="text-zinc-500">({latency}ms)</span>
      )}
      {retryCount !== undefined && retryCount > 0 && status !== 'connected' && (
        <span className="text-zinc-500">(retry {retryCount})</span>
      )}
      {(status === 'disconnected' || status === 'error') && onReconnect && (
        <button
          onClick={onReconnect}
          className="ml-1 p-0.5 rounded hover:bg-white/10 transition-colors"
          title="Retry connection"
        >
          <RefreshCw className="w-3 h-3" />
        </button>
      )}
    </div>
  );
}

export default ConnectionStatus;
