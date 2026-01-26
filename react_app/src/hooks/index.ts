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
  useBatchDesign,
} from './useCSVImport';

// V2 Hooks - React parity
export {
  useBuildingGeometry,
  useBuildingGeometryMutation,
} from './useBuildingGeometry';
export {
  useCrossSectionGeometry,
  useCrossSectionMutation,
} from './useCrossSectionGeometry';
export {
  useRebarValidation,
  useRebarValidationMutation,
  getWarningColor,
} from './useRebarValidation';
export {
  useDualCSVImport,
  useDualCSVImportMutation,
} from './useDualCSVImport';

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

// V2 Type exports
export type {
  BeamInstance,
  Building3DGeometry,
  BuildingGeometryRequest,
} from './useBuildingGeometry';
export type {
  RebarPosition,
  StirrupVertex,
  CrossSectionGeometry,
  CrossSectionRequest,
} from './useCrossSectionGeometry';
export type {
  RebarWarning,
  RebarValidationResult,
  RebarValidationRequest,
  WarningSeverity,
} from './useRebarValidation';
export type {
  BeamData,
  ImportResult,
  DualCSVImportRequest,
  DualImportState,
} from './useDualCSVImport';
