/**
 * Hooks barrel export
 */
export { useAutoDesign } from './useAutoDesign';
export { useDesignWebSocket } from './useDesignWebSocket';
export { useBeamGeometry } from './useBeamGeometry';
export { useLiveDesign } from './useLiveDesign';
export {
  useCSVFileImport,
  useCSVTextImport,
  useDualCSVImport,
  useBatchDesign,
} from './useCSVImport';
export {
  useDashboard,
  useCodeChecks,
  useRebarSuggestions,
  useDashboardMutation,
  useCodeChecksMutation,
  useRebarSuggestionsMutation,
} from './useInsights';

// Type exports
export type {
  Point3D,
  RebarSegment,
  RebarPath,
  StirrupLoop,
  Beam3DGeometry,
  BeamGeometryRequest,
} from './useBeamGeometry';
export type {
  ImportedBeam,
  DesignedBeam,
} from './useCSVImport';
export type {
  ConnectionStatus as WebSocketConnectionStatus,
  WebSocketState,
} from './useDesignWebSocket';
export type {
  BeamParams,
  RebarConfig,
  DesignResult,
  DashboardResponse,
  CodeChecksResponse,
  SingleCodeCheck,
  RebarSuggestion,
  RebarSuggestResponse,
} from './useInsights';