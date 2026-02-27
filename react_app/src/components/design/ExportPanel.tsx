/**
 * ExportPanel — Download buttons for BBS CSV, DXF drawing, and design report.
 *
 * Accepts beam params and optional design results.
 * Triggers browser file downloads via the /api/v1/export/* endpoints.
 */
import { Download, FileText, FileSpreadsheet, Loader2 } from "lucide-react";
import { useExportBBS, useExportDXF, useExportReport } from "../../hooks/useExport";
import type { ExportBeamParams } from "../../hooks/useExport";

interface ExportPanelProps {
  beamParams: ExportBeamParams;
  utilization?: number;
  isSafe?: boolean;
  astProvided?: number;
}

export function ExportPanel({ beamParams, utilization, isSafe, astProvided }: ExportPanelProps) {
  const bbs = useExportBBS();
  const dxf = useExportDXF();
  const report = useExportReport();

  const anyLoading = bbs.isPending || dxf.isPending || report.isPending;

  return (
    <div className="rounded-xl bg-white/[0.03] border border-white/8 p-3">
      <h4 className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-2.5">Export</h4>
      <div className="flex gap-2">
        <ExportButton
          label="BBS"
          icon={<FileSpreadsheet className="w-3.5 h-3.5" />}
          loading={bbs.isPending}
          disabled={anyLoading}
          onClick={() => bbs.mutate(beamParams)}
        />
        <ExportButton
          label="DXF"
          icon={<Download className="w-3.5 h-3.5" />}
          loading={dxf.isPending}
          disabled={anyLoading}
          onClick={() => dxf.mutate(beamParams)}
        />
        <ExportButton
          label="Report"
          icon={<FileText className="w-3.5 h-3.5" />}
          loading={report.isPending}
          disabled={anyLoading}
          onClick={() =>
            report.mutate({
              beam_id: beamParams.beam_id,
              width: beamParams.width,
              depth: beamParams.depth,
              fck: beamParams.fck,
              fy: beamParams.fy,
              moment: beamParams.moment,
              shear: beamParams.shear,
              ast_required: beamParams.ast_required,
              ast_provided: astProvided,
              utilization: utilization,
              is_safe: isSafe,
              format: "html",
            })
          }
        />
      </div>
      {(bbs.error || dxf.error || report.error) && (
        <p className="mt-2 text-[10px] text-red-400/70">
          Export failed — check API connection
        </p>
      )}
    </div>
  );
}

function ExportButton({ label, icon, loading, disabled, onClick }: {
  label: string;
  icon: React.ReactNode;
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex-1 flex items-center justify-center gap-1.5 px-2.5 py-2 text-xs font-medium text-white/70 bg-white/[0.04] hover:bg-white/[0.08] border border-white/8 rounded-lg transition-colors disabled:opacity-40"
    >
      {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : icon}
      {label}
    </button>
  );
}
