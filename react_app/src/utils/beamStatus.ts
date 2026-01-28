import type { BeamCSVRow } from "../types/csv";

export type BeamStatus = "pending" | "designing" | "pass" | "fail" | "warning";

export function deriveBeamStatus(beam: BeamCSVRow): BeamStatus {
  if (beam.status && beam.status !== "pending") {
    return beam.status;
  }

  if (typeof beam.utilization === "number") {
    if (beam.utilization > 1) return "fail";
    if (beam.utilization > 0.9) return "warning";
    return "pass";
  }

  if (typeof beam.ast_required === "number" && typeof beam.ast_provided === "number") {
    if (beam.ast_provided < beam.ast_required) return "fail";
    return "pass";
  }

  return beam.status ?? "pending";
}
