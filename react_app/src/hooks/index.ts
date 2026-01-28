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
  useBuildingGeometry,
  useCrossSectionGeometry,
} from './useGeometryAdvanced';
export {
  useRebarValidation,
  useRebarApply,
} from './useRebarEditor';
export {
  useDashboardInsights,
  useCodeChecks,
  useRebarSuggestions,
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
  BeamDesignPayload,
} from './useCSVImport';
export type {
  ConnectionStatus as WebSocketConnectionStatus,
  WebSocketState,
} from './useDesignWebSocket';
export type {
  BuildingBeamInput,
  BuildingBeamResult,
  BuildingGeometryResponse,
  CrossSectionRequest,
  CrossSectionResponse,
  BarPosition,
} from './useGeometryAdvanced';
export type {
  BeamParams as RebarBeamParams,
  RebarConfig,
  ValidationDetail,
  RebarValidateResponse,
  RebarApplyResponse,
} from './useRebarEditor';
export type {
  BeamResult,
  DashboardData,
  CheckDetail,
  CodeChecksResult,
  SuggestionItem,
  RebarSuggestionsResult,
} from './useInsights';
