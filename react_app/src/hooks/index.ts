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
  useSimpleBatchDesign,
} from './useCSVImport';
export { useBatchDesign } from './useBatchDesign';
export type {
  BatchProgress,
  BatchResult,
  BatchStatus,
  BatchDesignState,
} from './useBatchDesign';
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
  useProjectBOQ,
} from './useInsights';
export type { ProjectBOQResponse } from './useInsights';
export {
  useExportBBS,
  useExportDXF,
  useExportReport,
  useExportBuildingSummary,
} from './useExport';
export { useTorsionDesign } from './useTorsionDesign';
export { useLoadAnalysis } from './useLoadAnalysis';

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
