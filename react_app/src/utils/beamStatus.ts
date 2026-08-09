import type { BeamCSVRow } from "../types/csv";

export type BeamStatus = "pending" | "designing" | "pass" | "fail" | "warning";

export function deriveBeamStatus(beam: BeamCSVRow): BeamStatus {
  // An explicit workflow status is authoritative, including "pending" after
  // an input edit. Falling through here would reuse stale design results.
  if (beam.status) {
    return beam.status;
  }

  if (typeof beam.is_valid === "boolean") {
    return beam.is_valid ? "pass" : "fail";
  }

  // Legacy imported results may only contain a utilization ratio.
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
