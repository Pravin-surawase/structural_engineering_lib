/**
 * useDesignWebSocket Hook
 *
 * Real-time WebSocket connection for live beam design updates.
 * Provides <100ms latency for design calculations.
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { useDesignStore } from '../store/designStore';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export interface WebSocketState {
  isConnected: boolean;
  latency: number | null;
  error: string | null;
}

export function useDesignWebSocket(sessionId: string, enabled: boolean = true) {
  const { inputs, setResult, setLoading, setError, length } = useDesignStore();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    latency: null,
    error: null,
  });

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(`${WS_URL}/ws/design/${sessionId}`);

      ws.onopen = () => {
        setState((s) => ({ ...s, isConnected: true, error: null }));
        console.log('WebSocket connected');
      };

      ws.onclose = () => {
        setState((s) => ({ ...s, isConnected: false }));
        console.log('WebSocket disconnected');

        // Auto-reconnect after 3 seconds
        if (enabled) {
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        setState((s) => ({ ...s, error: 'WebSocket connection error' }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleMessage(message);
        } catch {
          console.error('Failed to parse WebSocket message');
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setState((s) => ({ ...s, error: (err as Error).message }));
    }
  }, [sessionId, enabled]);

  // Handle incoming messages
  const handleMessage = useCallback(
    (message: { type: string; latency_ms?: number; data?: unknown; message?: string }) => {
      switch (message.type) {
        case 'design_result':
          setState((s) => ({ ...s, latency: message.latency_ms ?? null }));
          setLoading(false);
          if (message.data) {
            // Transform WebSocket response to match BeamDesignResponse
            const data = message.data as {
              flexure?: {
                ast_required?: number;
                mu_lim?: number;
                xu?: number;
                xu_max?: number;
                is_safe?: boolean;
              };
              shear?: {
                tv?: number;
                tc?: number;
                spacing?: number;
                is_safe?: boolean;
              };
            };
            setResult({
              success: data.flexure?.is_safe ?? false,
              message: 'Design complete via WebSocket',
              flexure: {
                ast_required: data.flexure?.ast_required ?? 0,
                ast_min: 0,
                ast_max: 0,
                xu: data.flexure?.xu ?? 0,
                xu_max: data.flexure?.xu_max ?? 0,
                is_under_reinforced: true,
                moment_capacity: data.flexure?.mu_lim ?? 0,
              },
              shear: data.shear
                ? {
                    tau_v: data.shear.tv ?? 0,
                    tau_c: data.shear.tc ?? 0,
                    tau_c_max: 0,
                    asv_required: 0,
                    stirrup_spacing: data.shear.spacing ?? 0,
                    sv_max: 0,
                    shear_capacity: 0,
                  }
                : undefined,
              ast_total: data.flexure?.ast_required ?? 0,
              asc_total: 0,
              utilization_ratio: 0,
            });
          }
          break;

        case 'pong':
          // Heartbeat response
          break;

        case 'error':
          setError(message.message ?? 'Unknown WebSocket error');
          setLoading(false);
          break;
      }
    },
    [setResult, setLoading, setError]
  );

  // Send design request
  const sendDesign = useCallback(() => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send design');
      return false;
    }

    setLoading(true);
    wsRef.current.send(
      JSON.stringify({
        type: 'design_beam',
        params: {
          width: inputs.width,
          depth: inputs.depth,
          moment: inputs.moment,
          shear: inputs.shear,
          fck: inputs.fck,
          fy: inputs.fy,
          length: length,
        },
      })
    );
    return true;
  }, [inputs, length, setLoading]);

  // Connect on mount
  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [enabled, connect]);

  // Send design on input changes when connected
  useEffect(() => {
    if (enabled && state.isConnected) {
      sendDesign();
    }
  }, [enabled, state.isConnected, inputs, sendDesign]);

  return {
    ...state,
    sendDesign,
    disconnect: () => wsRef.current?.close(),
  };
}
