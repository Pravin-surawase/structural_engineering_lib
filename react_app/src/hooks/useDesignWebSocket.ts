/**
 * useDesignWebSocket Hook
 *
 * Real-time WebSocket connection for live beam design updates.
 * Provides <100ms latency for design calculations.
 * Uses reconnecting-websocket for robust auto-reconnection.
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { useDesignStore } from '../store/designStore';
import type { BeamDesignResponse } from '../api/client';

import { WS_BASE_URL } from '../config';

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';

export interface WebSocketState {
  isConnected: boolean;
  status: ConnectionStatus;
  latency: number | null;
  error: string | null;
  retryCount: number;
  lastConnectedAt: Date | null;
}

type WebSocketDesignData = Omit<Partial<BeamDesignResponse>, 'flexure' | 'shear'> & {
  flexure?: Partial<BeamDesignResponse['flexure']> & {
    // Legacy field used by servers before the REST/WebSocket contract was aligned.
    mu_lim?: number;
    is_safe?: boolean;
  };
  shear?: Partial<NonNullable<BeamDesignResponse['shear']>> & {
    // Legacy field names kept for a graceful rolling upgrade.
    tv?: number;
    tc?: number;
    spacing?: number;
  };
};

/** Normalize current and legacy WebSocket payloads to the REST response shape. */
export function normalizeWebSocketDesignResult(data: WebSocketDesignData): BeamDesignResponse {
  const flexure = data.flexure ?? {};
  const shear = data.shear;

  return {
    success: data.success ?? flexure.is_safe ?? false,
    message: data.message ?? 'Design complete via WebSocket',
    flexure: {
      ast_required: flexure.ast_required ?? 0,
      ast_min: flexure.ast_min ?? 0,
      ast_max: flexure.ast_max ?? 0,
      xu: flexure.xu ?? 0,
      xu_max: flexure.xu_max ?? 0,
      is_under_reinforced: flexure.is_under_reinforced ?? true,
      moment_capacity: flexure.moment_capacity ?? flexure.mu_lim ?? 0,
      asc_required: flexure.asc_required ?? 0,
    },
    shear: shear
      ? {
          tau_v: shear.tau_v ?? shear.tv ?? 0,
          tau_c: shear.tau_c ?? shear.tc ?? 0,
          tau_c_max: shear.tau_c_max ?? 0,
          asv_required: shear.asv_required ?? 0,
          stirrup_spacing: shear.stirrup_spacing ?? shear.spacing ?? 0,
          sv_max: shear.sv_max ?? 0,
          shear_capacity: shear.shear_capacity ?? 0,
        }
      : undefined,
    ast_total: data.ast_total ?? flexure.ast_required ?? 0,
    asc_total: data.asc_total ?? flexure.asc_required ?? 0,
    utilization_ratio: data.utilization_ratio ?? 0,
    effective_depth_used: data.effective_depth_used,
    warnings: data.warnings ?? [],
  };
}

// ReconnectingWebSocket options for robust connection
const RWS_OPTIONS = {
  connectionTimeout: 4000,
  maxRetries: 10,
  maxReconnectionDelay: 10000,
  minReconnectionDelay: 1000,
  reconnectionDelayGrowFactor: 1.3,
};

export function useDesignWebSocket(sessionId: string, enabled: boolean = true) {
  const { inputs, setResult, setLoading, setError, length } = useDesignStore();
  const wsRef = useRef<ReconnectingWebSocket | null>(null);
  const retryCountRef = useRef(0);
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    status: 'disconnected',
    latency: null,
    error: null,
    retryCount: 0,
    lastConnectedAt: null,
  });

  // Handle incoming messages
  const handleMessage = useCallback(
    (message: { type: string; latency_ms?: number; data?: unknown; message?: string }) => {
      switch (message.type) {
        case 'design_result':
          setState((s) => ({ ...s, latency: message.latency_ms ?? null }));
          setLoading(false);
          if (message.data) {
            setResult(normalizeWebSocketDesignResult(message.data as WebSocketDesignData));
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

  // Connect to WebSocket using ReconnectingWebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      setState((s) => ({ ...s, status: 'connecting', error: null }));

      const ws = new ReconnectingWebSocket(
        `${WS_BASE_URL}/ws/design/${sessionId}`,
        [],
        RWS_OPTIONS
      );

      ws.onopen = () => {
        retryCountRef.current = 0;
        setState((s) => ({
          ...s,
          isConnected: true,
          status: 'connected',
          error: null,
          retryCount: 0,
          lastConnectedAt: new Date(),
        }));
      };

      ws.onclose = () => {
        setState((s) => ({
          ...s,
          isConnected: false,
          status: enabled ? 'reconnecting' : 'disconnected',
        }));
      };

      ws.onerror = () => {
        retryCountRef.current++;
        setState((s) => ({
          ...s,
          status: 'error',
          error: `Connection error (retry ${retryCountRef.current}/${RWS_OPTIONS.maxRetries})`,
          retryCount: retryCountRef.current,
        }));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data as string);
          handleMessage(message);
        } catch {
          console.error('Failed to parse WebSocket message');
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setState((s) => ({
        ...s,
        status: 'error',
        error: (err as Error).message,
      }));
    }
  }, [sessionId, enabled, handleMessage]);

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

  // Reconnect function for manual retry
  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.reconnect();
    }
  }, []);

  return {
    ...state,
    sendDesign,
    reconnect,
    disconnect: () => wsRef.current?.close(),
  };
}
