/**
 * Centralized API configuration.
 *
 * In development: defaults to '' (empty) so requests go through the Vite proxy
 * on the same origin — works seamlessly over SSH remote development.
 *
 * In production / Docker: set VITE_API_URL to the backend URL.
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/** WebSocket base URL — defaults to current host with ws:// protocol */
export const WS_BASE_URL =
  import.meta.env.VITE_WS_URL ||
  (API_BASE_URL
    ? API_BASE_URL.replace(/^http/, 'ws')
    : `ws://${window.location.host}`);
